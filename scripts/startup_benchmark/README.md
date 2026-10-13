# Application startup benchmark

## What it measures

This tool measures how long `casedb`, `seqdb`, or `omopdb` takes to start and
answer its first successful health request at `/v1/health`.

Each run starts a new Python process. The timer starts just before that process
is launched and stops when the complete health response arrives. The tool checks
that the response belongs to the application it just started. It then stops that
application before the next run.

The target is a **p95 below 15 seconds**. This means that at least 95% of the
successful measured runs take no longer than the reported p95 value.

The measurement includes Python startup, loading code, application setup, and
the health request. It excludes preparation, shutdown, and report creation.
A successful health request shows that this application can answer that request;
it does not show that every database or application feature is ready.

## Before you start

Run the commands from the repository root using Python 3.14 or newer. The
examples use the project's `.venv` environment. Linux and WSL are supported.

Make sure any required databases and other services are already running. The
benchmark does not start them. Stop any existing application using the selected
port: `casedb` uses 8000, `seqdb` uses 8001, and `omopdb` uses 8002. The tool will
refuse an occupied port and will not stop another application for you.

You must choose both settings for every benchmark or diagnostic command:

| Setting | Choices |
| --- | --- |
| `--idp-mode` | `IDPS` uses configured sign-in providers; `MOCK` uses test sign-in; `NONE` disables sign-in and is for local tests. |
| `--repository-mode` | `DICT_DEMO` or `DICT_EMPTY` uses data held in memory, with demo data or an empty starting point. `SA_SQLITE_DEMO` or `SA_SQLITE_EMPTY` uses local SQLite database files. `SA_SQL` uses the configured database. |

The application must have `debug=False`. Debug mode leaves out the response
header that the tool needs to identify its own application.

## Choose the command

There are three commands. They share saved results, but answer different
questions:

| Command | Use it to answer | Starts applications? |
| --- | --- | --- |
| `benchmark` | How long does normal startup take across several runs? | Yes, once for each measured run and any requested warmups. |
| `diagnose` | Which code loading or setup steps might explain the startup time? | Yes, in separate runs that collect extra information. |
| `report` | How do I view saved results again or combine them with matching diagnostics? | No. It only reads saved files and writes a report. |

Start with `benchmark` to measure the overall time. Use `diagnose` when you
want to understand where that time may be spent. Use `report` to bring the two
views together. All application starts use the existing `run.py` command;
these commands do not measure Docker container or full Docker Compose startup.

## Run a benchmark

For the casedb reference configuration:

```bash
.venv/bin/python -m scripts.startup_benchmark benchmark casedb \
  --idp-mode IDPS --repository-mode DICT_DEMO
```

By default, this takes 30 measurements. Progress appears in the terminal, and
the final line gives the report location.

For a quick local check, use fewer runs:

```bash
.venv/bin/python -m scripts.startup_benchmark benchmark seqdb \
  --idp-mode NONE --repository-mode DICT_EMPTY --runs 3
```

This is useful for checking that startup works, but three runs are not enough
to pass the target check. Replace the application and settings as needed.

### Measured runs and warmups

`--runs` sets how many starts contribute to the startup statistics. Each one
uses a new application process. The first measured run counts just like the
others; it is not automatically discarded.

`--warmups` adds starts before the measured runs. They also use new processes,
but their times are kept out of the statistics. They can help you observe what
happens after the machine has already loaded some files. They do not guarantee
that later starts are faster.

For example:

```bash
.venv/bin/python -m scripts.startup_benchmark benchmark casedb \
  --idp-mode IDPS --repository-mode DICT_DEMO --runs 30 --warmups 2
```

This requests **32 application starts**: two warmups, followed by 30 measured
runs. All 32 appear in the saved results. Only the 30 measured runs contribute
to p95. A failed warmup still prevents the series from passing the target check.

| Option | What it does |
| --- | --- |
| `--runs 30` | Sets the number of measured starts. |
| `--warmups 2` | Adds two starts before measurement. Their results are saved separately. The default is zero. |
| `--check-target` | Makes the command return a failure result if the target check does not pass. |

The report always shows whether the target passed. `--check-target` changes
the command's final success or failure result, which is useful in automated
checks. Without it, a completed series can return success even when p95 is too
high or the sample is too small. Application startup failures still return
failure either way.

### Options shared by benchmark and diagnostics

These options control how applications are checked and where results are saved.
They are available for both `benchmark` and `diagnose`.

| Option | What it does |
| --- | --- |
| `--output DIRECTORY` | Saves results in a directory you choose. Use a new directory for each series. |
| `--readiness-timeout 60` | Allows up to 60 seconds for each application to answer its health request. |
| `--poll-interval 0.05` | Sets the pause between health checks, in seconds. |
| `--request-timeout 0.25` | Limits each health request to 0.25 seconds. |
| `--settle-seconds 1` | Adds a one-second pause after stopping each application. |

The readiness timeout is the limit for the **whole startup attempt**. The
request timeout is the limit for **one health request**. A failed request can
be tried again while time remains. No request is allowed more time than is left
in the whole startup attempt.

The polling interval affects how quickly the tool notices that an application
is ready. That small delay is included in the measurement. The settle pause
happens after shutdown, so it does not contribute to the startup time.

If the repository has both `cert/key.pem` and `cert/cert.pem`, requests use
HTTPS. Use `--ca-file FILE` to supply a trusted certificate file, or explicitly
use `--insecure` to skip certificate verification for a local test. The report
records that choice.

## Read the results

Default output directories are under `test/output/startup_benchmark/`. Start
with `report.md` for the readable report.

| File | Contents |
| --- | --- |
| `report.md` | Run results, statistics, charts, and explanations. |
| `results.json` | Saved measurements, settings, machine details, and information about failures. |
| `startup.svg` | A chart of runs in their original order and successful runs sorted by time. Open it in a browser. |
| `*.stdout.log` and `*.stderr.log` | Original application output for each attempted run. |
| `configuration-before.json` and `configuration-after.json` | Application settings captured before and after measurement, with sensitive values hidden. |

Statistics use **successful measured runs only**. Warmups and diagnostic runs
do not count. Failed runs remain visible in the report and have no invented
startup time. If there are no successful measurements, statistics are `null`,
meaning no value is available.

| Result | Meaning |
| --- | --- |
| Mean | The average startup time. |
| Median | The middle startup time after sorting the results. |
| Minimum and maximum | The fastest and slowest successful starts. |
| p90 and p95 | Times that cover at least 90% and 95% of successful measured runs. For 30 successful runs, p95 is the 29th value when sorted from fastest to slowest. |
| Margin | `15 − p95`, in seconds. A positive value is below the target; zero or a negative value does not meet it. |
| Above target | The count and percentage of successful starts taking more than 15 seconds. |
| Evidence valid | Whether the series has enough successful measurements and passed the completion, cleanup, and configuration checks. |
| Target pass | Whether the evidence is valid **and** p95 is strictly below 15 seconds. |

A target pass requires at least 30 successful measured runs, no failures in
the series, successful shutdown checks, and unchanged configuration. A fast
p95 from a small or failed series does not qualify. Failures and starts that
were never attempted are reported separately. Pressing Ctrl-C stops the series
and produces a partial report.

The startup chart marks the 15-second target and p95. Failed runs use `×` and
unattempted runs use `·`; these marks do not represent durations.

You may see an application warning about the extra
`X-Startup-Benchmark-Instance` response header. This header is used to identify
the application started by the benchmark. The current configuration checker
warns about its name even though the application uses it correctly.

## Investigate slow startup

### Choose the diagnostic kind

Use a separate diagnostic command with the same application settings:

```bash
.venv/bin/python -m scripts.startup_benchmark diagnose casedb \
  --idp-mode IDPS --repository-mode DICT_DEMO --kind both
```

Diagnostics run once per selected kind by default. Use `--kind imports` to
look at loading Python code, `--kind phases` to look at application setup
steps, or `--kind both` for both views. `--runs` changes the number of runs
for each selected kind.

| Choice | What it records | When it helps |
| --- | --- | --- |
| `--kind imports` | Time spent loading Python code, including work performed while that code is loaded. | When you want to find files or groups of files that take a long time to load. |
| `--kind phases` | Time spent in selected application setup steps, such as reading settings, creating services, and starting the server. | When you want to find which setup step deserves a closer look. |
| `--kind both` | Both views, collected in separate application starts. This is the default. | When you want a broader picture before choosing what to investigate. |

`--runs` has a different meaning here than for `benchmark`. For example,
`diagnose ... --kind both --runs 3` requests **six application starts**: three
import runs, then three phase runs. It does not request three runs that collect
both views at the same time. Diagnostics do not accept `--warmups` or
`--check-target`.

Diagnostic output includes `diagnostics.json` and `diagnostic-*.svg` charts.
These runs gather extra information that can change startup time. Their
durations never enter the normal benchmark statistics.

Open `report.md` and find the sections named `imports` and `phases`. Each
diagnostic run gets its own section and chart. A report containing only
diagnostics has no normal measured runs, so its normal startup statistics are
`null`. This does not mean the diagnostic runs failed; check their run statuses.

### Read the import report

In the import report, **self time** is a code module's own work.
**Cumulative time** includes other modules loaded underneath it. The listed
chains show which loading steps were observed inside others. Do not add
cumulative times together: that would count some work more than once.
These times are shown in milliseconds; 1,000 milliseconds is one second.

Start with the chart of the 20 largest self times. A long bar points to a
module whose own work took a long time. A module is a named piece of Python
code, often a single file. Its own work can include reading settings or
constructing the application, so a long bar is not necessarily caused by
reading the file from disk.

Next, check the cumulative times and the observed chains. A module with a
small self time but a large cumulative time spent much of its loading time
waiting for other modules to load. For example, 100 milliseconds of its own
work plus 600 milliseconds loading other modules gives a cumulative time of
700 milliseconds. Do not add the 100 milliseconds to that 700 again.

A chain such as `A → B → C` means C was loaded inside B's loading work, which
was inside A's loading work. It describes that run, not every possible
relationship between those files. The same module can appear more than once;
those entries are separate recorded occurrences.

Warnings about missing or malformed records mean the loading sequence could
not be reconstructed fully. Use the raw `*.stderr.log` file to check those
records before drawing conclusions about a chain.

### Read the phase report

In the phase report, **inclusive time** includes work done inside a setup
step. **Exclusive time** removes recorded inner steps where that calculation
is possible. Missing exclusive values mean that the calculation is unavailable.
Some steps contain or overlap others, and some time has no recorded step.
Incomplete steps and gaps are retained. These charts help locate work to
investigate; they do not divide normal startup into exact parts.

Read the timeline from left to right to see when each step started and ended.
Long bars show long steps. The `parent` number identifies the outer step that
contains a recorded step. For example, creating a repository can appear inside
the larger step that builds the application's services.

If an outer step took two seconds and its recorded inner work took half a
second, its exclusive time would be one and a half seconds, where this can be
calculated. That remaining time may still include work that was not recorded
as a separate step. It is not proof that the outer step alone caused a delay.

| Detail | How to read it |
| --- | --- |
| `complete` | The recorded step returned normally. |
| `error` | The step raised an error. Check the application log for the cause. |
| `incomplete` | A start was recorded without an end. Its full duration is unknown. |
| Unattributed intervals | Time between launch and the verified response that is not covered by completed recorded steps. These gaps may include work the tool does not track. |
| `instrumentation preparation` | Time spent preparing the extra measurements. This changes the order in which some code is loaded. |
| Application labels | The application doing the work. Casedb can also show seqdb steps when it starts an embedded seqdb application. |

Creating a database engine means preparing the object used to access a database.
It does not by itself show that a database connection was made. Connection
acquisition is recorded separately when it occurs.

Do not add all phase durations together: outer steps already include their
inner steps, and some work can happen at the same time. Do not subtract import
times from phase times or from a normal benchmark result. They come from
different application starts. Use each view to choose what to inspect, then
use a new normal benchmark to measure the effect of any changes.
## Rebuild a report

You can rebuild reports from saved files without starting any applications:

```bash
.venv/bin/python -m scripts.startup_benchmark report \
  BENCHMARK_DIRECTORY/results.json \
  --diagnostics DIAGNOSTIC_DIRECTORY/diagnostics.json \
  --output REPORT_DIRECTORY
```

Replace the capitalized directory names with your saved output locations.
Leave out `--diagnostics` if you only want the benchmark report. Diagnostic
results must match the benchmark's application, Git commit, and saved
configuration checks.

## Compare results fairly

Each run uses a new application process, but the operating system can keep
previously read files in memory. Databases can also retain data and earlier
work. The tool does not clear those caches or reset data. Startup itself may
read or write application data.

Compare runs using the same settings and a similar machine workload. Keep
the first measured run visible, and treat 30 measurements as a useful local
sample rather than a guarantee about every future start.

For further details, see the
[development guide](../../docs/06-Development-Guide.md#startup-benchmark).
