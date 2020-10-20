# locust

## What is Locust?

Locust reduces turnaround time on code reviews.

It can take a lot of effort for a reviewer to relate the line-by-line changes in a patch to
their mental model of the code base. This is a consistent impediment to fast responses on code
reviews.

Locust provides a semantic layer on top of `git diff`. Where `git diff` describes changes in terms
of the lines in the code base, Locust summarizes changes by the effect on modules, classes, and
functions.

## How does it work?

Locust is a command line tool, and you can invoke it as:
```bash
locust main docker --format yaml
```

This produces the following output:
```yaml
locust:
- file: locust/ci_helpers/github.py
  changes:
  - name: generate_argument_parser
    type: function
    line: 11
    changed_lines: 19
    total_lines: 9
    children: []
  - name: helper_push
    type: function
    line: 22
    changed_lines: 34
    total_lines: 13
    children: []
  - name: helper_pr
    type: function
    line: 37
    changed_lines: 50
    total_lines: 14
    children: []
  - name: main
    type: function
    line: 53
    changed_lines: 81
    total_lines: 29
    children: []
refs:
  initial: 22dd7fd
  terminal: c9813bd
```

Locust is easy to use in CI/CD pipelines:
+ [Locust GitHub Action](https://github.com/simiotics/locust-action)

## Installation

Locust requires Python3 (specifically, it was written in Python3.8).

### Install from PyPI

```bash
pip install bugout-locust
```

### Install from source

Clone this repository and run from the project root:
```bash
python setup.py install
```

### Docker

You can also use the Locust docker image:
```bash
docker pull bugout/locust
```

To run Locust using docker:
```bash
docker run -v $ABSOLUTE_PATH_TO_GIT_REPO:/usr/src/app bugout/locust -r /usr/src/app \
    $INITIAL_REVISION \
    $TERMINAL_REVISION \
    --format yaml
```

## Output formats

Locust can produce output in many formats. The currently supported formats are:

1. JSON (`--format json`)

2. YAML (`--format yaml`)

3. HTML (`--format html`)

4. GitHub-flavored HTML, meant to be used with GitHub styles (`--format html-github`)
