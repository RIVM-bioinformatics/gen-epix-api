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

    presets = {
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
            "--max-line-length=88",
            "--fail-under=9",
            "gen_epix/",
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
        self, file: Path | str, filter_on_codes: set[str] | None = None
    ) -> None:
        cmd = self.presets["pylint"]
        if isinstance(file, str):
            file = Path(file)
        if filter_on_codes:
            cmd = cmd + ["--disable=all", "--enable=" + ",".join(filter_on_codes)]
        self.run(cmd, file=file)

    def run_mypy(
        self, file: Path | str, filter_on_codes: set[str] | None = None
    ) -> None:
        cmd = self.presets["mypy"]
        if isinstance(file, str):
            file = Path(file)
        self.run(cmd, file=file)
        if filter_on_codes:
            lines = self.parse_mypy_for_messages(file, filter_on_codes)
            file.write_text("\n".join(lines))

    def parse_pylint_for_messages(
        self, file: Path | str, filter_on_codes: set[str] | None = None
    ) -> list[str]:
        if isinstance(file, str):
            file = Path(file)
        with open(file, "rt") as handle:
            lines = handle.readlines()
        pattern = re.compile(r": ([A-Z]\d{4}):")
        messages = [
            line
            for line in lines
            if pattern.search(line)
            and (
                not filter_on_codes or pattern.search(line).group(1) in filter_on_codes
            )
        ]
        return messages

    def parse_mypy_for_messages(
        self, file: Path | str, filter_on_codes: set[str] | None = None
    ) -> list[str]:
        if isinstance(file, str):
            file = Path(file)
        with open(file, "rt") as handle:
            lines = handle.readlines()
        location_pattern = re.compile(r"^(.*?:(\d+):)")
        error_code_pattern = re.compile(r"\[(.*?)\]\r?\n?$")
        out_lines = []
        prev_location = ""
        is_prev_match = False
        for line in lines:
            line = line.rstrip()
            location_match = location_pattern.search(line)
            if not location_match:
                # No location -> keep if empty line and previous match
                if not line and is_prev_match:
                    out_lines.append(line)
                continue
            location = location_match.group(1)
            if location == prev_location:
                # Same location -> keep if previous line was kept
                if is_prev_match:
                    out_lines.append(line)
                continue
            prev_location = location
            error_code_match = error_code_pattern.search(line)
            if not error_code_match:
                if is_prev_match:
                    # Note for a non-matched error code
                    continue
                # Special case: keep
                out_lines.append(line)
                continue
                # raise ValueError(f"Error code not found in line: {line}")
            error_code = error_code_match.group(1)
            if not filter_on_codes or error_code in filter_on_codes:
                is_prev_match = True
                out_lines.append(line)
            else:
                is_prev_match = False
        # Remove empty lines at the end
        while out_lines and not out_lines[-1]:
            out_lines.pop()
        return out_lines

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
        for value in self.presets.values():
            if file_basename:
                file = Path(f"{file_basename}.{value[0]}.txt")
                file2 = Path(f"{file_basename}.{now_str}.{value[0]}.txt")
            else:
                file = None
                file2 = None
            output = self.run(value, file=file)
            if file:
                file2.write_text(file.read_text())
            if output:
                outputs.append(output)
        if file_basename:
            file = Path(f"{file_basename}.txt")
            file2 = Path(f"{file_basename}.{now_str}.txt")
            with open(file, "wt") as handle:
                handle.write("\n".join(outputs))
            file2.write_text(file.read_text())
