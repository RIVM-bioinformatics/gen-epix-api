"""
This module contains the `Linter` class which is used to enforce code quality in the
`gen-epix` package. It uses tools like pylint and mypy as specified in the project's
documentation.

Note:
    This module is part of the `gen-epix` package.
"""

import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from test.test_client.util import get_test_root_output_dir

import polars as pl
import xlsxwriter


class Linter:
    """
    This class provides an interface to run linting tools like mypy,
    pylint, isort, and black with predefined settings. The settings are stored
    in the `presets` class attribute as a dictionary.

    Attributes:
        presets (dict): A dictionary containing the command-line arguments for
            each linting tool. The keys are the names of the tools, and the
            values are lists of arguments to be passed to the tools.

    Methods:
        run_linter(cmd: list[str]): Runs the specified linting tool with the
            provided command-line arguments.

        run_lint_and_format(): Runs a series of linting and formatting tools on
            the gen-epix project.
    """

    PYLINT_CODE_PATTERN = re.compile(r": (?P<code>[A-Z]+\d+):")
    PYLINT_LINE_PARTS_PATTERN = re.compile(
        r"^(?P<module>.*?):(?P<line>.*?):(?P<position>.*?): (?P<code>[A-Z]+\d+): (?P<message>.*)$"
    )
    PYLINT_SCORE_PATTERN = re.compile(
        r"Your code has been rated at (?P<score>[\d\.]+)/10"
    )
    MYPY_LOCATION_PATTERN = re.compile(r"^(?P<location>.*?:(\d+):)")
    MYPY_ISSUE_CODE_PATTERN = re.compile(r"\[([a-z0-9_]+)\]")

    PRESETS = {
        "mypy": [
            "mypy",
            "--no-incremental",
            "--disallow-untyped-defs",
            "--disallow-untyped-calls",
            "--disallow-incomplete-defs",
            "--disallow-untyped-decorators",
            "--strict-equality",
            "--warn-redundant-casts",
            "--warn-unused-ignores",
            "--warn-return-any",
            "--warn-unreachable",
            "--show-error-codes",
            "gen_epix/",
            # "test/",
        ],
        "pylint": [
            "pylint",
            "--fail-under=9",
            "gen_epix/",
            "--disable=C0301",  # Ignore "line too long" warnings since black handles that
            # "--disable=C0414",  # Ignore "useless-import-alias" warnings
            # "test/",
        ],
        "isort": [
            "isort",
            "--check-only",
            "--diff",
            "--profile",
            "black",
            ".",
        ],
        "black": [
            "black",
            "--check",
            "--diff",
            ".",
        ],
    }

    def run_pylint(
        self,
        file: Path | str,
        filter_on_codes: set[str] | None = None,
        disable_codes: set[str] | None = None,
    ) -> str:
        base_cmd = list(self.PRESETS["pylint"])  # copy to avoid mutation
        if isinstance(file, str):
            file = Path(file)
        if filter_on_codes:
            base_cmd += [
                "--disable=all",
                f"--enable={','.join(sorted(filter_on_codes))}",
            ]
        if disable_codes:
            base_cmd += [f"--disable={','.join(sorted(disable_codes))}"]
        return self.run(base_cmd, file=file)

    def run_mypy(
        self, file: Path | str, filter_on_codes: set[str] | None = None
    ) -> None:
        cmd = self.PRESETS["mypy"]
        if isinstance(file, str):
            file = Path(file)
        self.run(cmd, file=file)
        if filter_on_codes:
            lines = self.parse_mypy_for_issue_lines(file, filter_on_codes)
            file.write_text("\n".join(lines))

    def parse_pylint_for_issue_lines(
        self, file: Path | str, filter_on_codes: set[str] | None = None
    ) -> list[str]:
        if isinstance(file, str):
            file = Path(file)
        with open(file, "rt") as handle:
            lines = handle.readlines()
        pattern = self.PYLINT_CODE_PATTERN
        issue_lines = [
            line
            for line in lines
            if pattern.search(line)
            and (
                not filter_on_codes or pattern.search(line).group(1) in filter_on_codes
            )
        ]
        return issue_lines

    def parse_mypy_for_issue_lines(
        self, file: Path | str, filter_on_codes: set[str] | None = None
    ) -> list[str]:
        if isinstance(file, str):
            file = Path(file)
        with open(file, "rt") as handle:
            lines = handle.readlines()
        location_pattern = self.MYPY_LOCATION_PATTERN
        issue_code_pattern = self.MYPY_ISSUE_CODE_PATTERN
        issue_lines: list[str] = []
        prev_location = ""
        is_prev_match = False
        for line in lines:
            line = line.rstrip()
            location_match = location_pattern.search(line)
            if not location_match:
                # No location -> keep if empty line and previous match
                if not line and is_prev_match:
                    issue_lines.append(line)
                continue
            location = location_match.group(1)
            if location == prev_location:
                # Same location -> keep if previous line was kept
                if is_prev_match:
                    issue_lines.append(line)
                continue
            prev_location = location
            error_code_match = issue_code_pattern.search(line)
            if not error_code_match:
                if is_prev_match:
                    # Note for a non-matched error code
                    continue
                # Special case: keep
                issue_lines.append(line)
                continue
                # raise ValueError(f"Error code not found in line: {line}")
            error_code = error_code_match.group(1)
            if not filter_on_codes or error_code in filter_on_codes:
                is_prev_match = True
                issue_lines.append(line)
            else:
                is_prev_match = False
        # Remove empty lines at the end
        while issue_lines and not issue_lines[-1]:
            issue_lines.pop()
        return issue_lines

    def run(
        self, cmd: list[str], file: Path | str | None = None, verbose: bool = False
    ) -> str:
        """
        Runs the specified linting tool with the provided command-line arguments.

        This method uses the subprocess module to run the linting tool in a separate
        process. It captures the output of the tool and prints it to the console.

        Parameters
        ----------
        cmd : list[str]
            A list of command-line arguments to be passed to the linting tool. The first
            element of the list is the name of the tool.

        Raises
        ------
        subprocess.CalledProcessError
            If the linting tool returns a non-zero exit code, indicating that it found some
            issues with the code.
        """
        if verbose:
            print(f"Running program: {cmd[0]}")

        # Subprocess does not naturally inherit the conda environment,
        # so we need to activate it manually.
        cmd = [sys.executable, "-m"] + cmd
        try:
            retval = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            if verbose:
                print(f"{cmd[2]} passed")
            output = retval.decode("utf-8")
        except subprocess.CalledProcessError as e:
            output = e.output.decode("utf-8")
            if verbose:
                print(f"Failed running {cmd[2]}, here is the output:")
                print(output)
        if file:
            if isinstance(file, str):
                file = Path(file)
            file.write_text(output)
        return output

    def run_all(self, file_basename: Path | str | None = None) -> None:
        """
        Runs a series of linting and formatting tools on the gen-epix project.

        This method iterates over the `presets` class attribute, and for each set of
        command-line arguments, it calls the `run_linter` method.

        Raises
        ------
        subprocess.CalledProcessError
            If any of the linting or formatting tools return a non-zero exit code,
            indicating that it found some issues with the code.
        """
        outputs = []
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        if file_basename and isinstance(file_basename, str):
            file_basename = Path(file_basename)
        for value in self.PRESETS.values():
            if file_basename:
                file = Path(f"{file_basename}.{value[0]}.txt")
                file2 = Path(f"{file_basename}.{now_str}.{value[0]}.txt")
            else:
                file = None
                file2 = None
            output = self.run(value, file=file)
            if file2:
                file2.write_text(file.read_text())
            if output:
                outputs.append(output)
        if file_basename:
            file = Path(f"{file_basename}.txt")
            file2 = Path(f"{file_basename}.{now_str}.txt")
            with open(file, "wt") as handle:
                handle.write("\n".join(outputs))
            file2.write_text(file.read_text())

    def analyse_pylint_code_impact(self, verbose: bool = True) -> None:
        output_dir = get_test_root_output_dir()
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_report_file = output_dir / f"pylint.rule_impact.{now_str}.base_report.txt"
        result_file = output_dir / f"pylint.rule_impact.{now_str}.result.xlsx"
        temp_report_file_template = f"pylint.rule_impact.{now_str}.disable_{{code}}.txt"

        # Get baseline score and issues
        if verbose:
            print(f"Getting baseline")
        start_time = datetime.now()
        base_report = self.run_pylint(file=base_report_file)
        # base_report = base_report_file.read_text()
        end_time = datetime.now()
        if verbose:
            print(f"Baseline completed in {(end_time - start_time).seconds}s")
        base_score = Linter.parse_pylint_score(base_report)
        if base_score is None:
            raise ValueError("Could not determine base pylint score.")
        issue_lines = self.parse_pylint_for_issue_lines(base_report_file)
        total_n_issues = len(issue_lines)

        # Parse baseline issues and get aggregated counts
        issue_list = []
        for issue_line in issue_lines:
            pattern_match = self.PYLINT_LINE_PARTS_PATTERN.match(issue_line)
            if not pattern_match:
                if verbose:
                    print(f"Could not parse pylint issue line: {issue_line}")
                continue
            issue_list.append(pattern_match.groupdict())
        issue_df = pl.DataFrame(issue_list)
        code_counts_df = issue_df.group_by("code").len().rename({"len": "count"})
        module_counts_df = issue_df.group_by("module").len().rename({"len": "count"})

        # Run pylint disabling one code at a time
        code_pattern = self.PYLINT_CODE_PATTERN
        codes = sorted(set(code_pattern.findall(base_report)))
        results: list[dict] = [
            {
                "code": "BASE",
                "score": base_score,
                "impact_score": 0.0,
                "n_issues": 0,
                "impact_score_per_issue": 0.0,
            }
        ]
        for i, code in enumerate(codes):
            if verbose:
                print(f"Analyzing code {i+1}/{len(codes)}: {code}")
            temp_report_file = output_dir / temp_report_file_template.format(code=code)
            output = self.run_pylint(file=temp_report_file, disable_codes={code})
            score = Linter.parse_pylint_score(output)
            n_issues = total_n_issues - len(
                self.parse_pylint_for_issue_lines(temp_report_file)
            )
            temp_report_file.unlink(missing_ok=True)
            impact_score = (score - base_score) if score is not None else None
            if verbose:
                print(f"\tImpact on score: {impact_score}")
                print(f"\tNumber of issues: {n_issues}")
            results.append(
                {
                    "code": code,
                    "score": score,
                    "impact_score": impact_score,
                    "n_issues": n_issues,
                    "impact_score_per_issue": (
                        impact_score / n_issues
                        if n_issues and impact_score is not None
                        else 0.0
                    ),
                }
            )
        score_df = pl.DataFrame(results)
        score_df = score_df.sort("impact_score", descending=True)

        # Write out
        with xlsxwriter.Workbook(result_file) as workbook:
            issue_df.write_excel(workbook, worksheet="issues")
            code_counts_df.write_excel(workbook, worksheet="code_counts")
            module_counts_df.write_excel(workbook, worksheet="module_counts")
            score_df.write_excel(workbook, worksheet="score_impact")
        if verbose:
            print(f"Analysis complete. Results written to: {result_file}")

    @staticmethod
    def parse_pylint_score(report: str) -> float | None:
        match = re.search(r"Your code has been rated at ([\d\.]+)/10", report)
        return float(match.group(1)) if match else None
