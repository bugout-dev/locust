# <img src="./img/locust-black.svg" height="20" width="20"/> locust

"It's `git diff --stat` on steroids!" - [@scottmilliken](https://gitlab.com/scottmilliken)

## What is Locust?

Locust helps you reason about your code base as it evolves over time.

Locust provides a semantic layer on top of `git diff`. It emits metadata describing
[AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree)-level changes to your
code base between git revisions.

This metadata is useful to both humans and computers. For example:

1. (Humans) Locust can generate
   [much more humane summaries of changes](https://github.com/bugout-dev/locust/pull/34) than the
   standard git diff.

2. (Computers) [Bugout.dev](https://alpha.bugout.dev) uses Locust metadata to learn high level
   abstractions about code.

## Installation

Locust requires Python3 (specifically, it was written in Python3.8).

### Install from PyPI

```bash
pip install -U setuptools
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

## Usage

### CLI

Locust is a command line tool, and you can invoke it as:

```bash
locust 22dd7fd6adf392bb29d13d10f10e7dbb1d97bfce c9813bd5871a9919551ccd917712135c40367c5c --format yaml
```

This produces the following output:

```yaml
locust:
  - file: locust/ci_helpers/github.py
    changes:
      - name: generate_argument_parser
        type: function
        line: 11
        changed_lines: 9
        total_lines: 9
        children: []
      - name: helper_push
        type: function
        line: 22
        changed_lines: 13
        total_lines: 13
        children: []
      - name: helper_pr
        type: function
        line: 37
        changed_lines: 14
        total_lines: 14
        children: []
      - name: main
        type: function
        line: 53
        changed_lines: 29
        total_lines: 29
        children: []
refs:
  initial: 22dd7fd
  terminal: c9813bd
```

### Language plugins

To use Locust to process a code base containing Python (>3.5) and Javascript, use the Javascript
plugin (written in Node 14).

If you are running Locust from the root of this project, you would do this as follows:

```
locust -r <path to repo> <initial revision> <terminal revision> --plugins "node js/out/index.js"
```

A Locust language plugin is simply a program that you can invoke from the shell (like
`node js/out/index.js`) which takes two arguments:

- `-i` - an input file containing a `locust.git.RunResponse` object

- `-o` - path to an output file into which it writes a list of tuples consisting of
  `locust.git.PatchInfo` objects and their corresponding list of `locust.parse.RawDefinition`
  objects.

The [Javascript plugin](./js/) provides a rubric for how to build your own plugin.

You can add custom plugins to a Locust invocation like this:

```
locust -r <path to repo> <initial revision> <terminal revision> \
  --plugins "node js/out/index.js" "<custom plugin invocation 1>" "<custom plugin invocation 2>"
```

### CI/CD

Locust is easy to use in CI/CD pipelines:

- [Locust GitHub Action](https://github.com/simiotics/locust-action)

### Docker

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

## Contributing

### Running tests

Make sure to clone [simiotics/locust-test-cases](https://github.com/simiotics/locust-test-cases)
repo to your machine.

Run:

```bash
git -c <path to locust-test-cases repo> fetch origin
```

Then, from the root of this repo:

```bash
LOCUST_TESTCASES_DIR=<path to locust-test-cases repo> ./test.sh
```

## Similar projects

### Kythe

[Kythe](https://kythe.io) is a Google open source project. It grew out of the need to semantically
link different parts of Google's code base.

The goals of Locust are different from those of Kythe. Locust is specifically about generating
metadata describing _changes_ to code.

Kythe on GitHub: https://github.com/kythe/kythe
