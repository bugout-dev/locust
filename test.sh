#!/usr/bin/env sh

set -e

if [ -z "$LOCUST_TESTCASES_DIR" ]
then
	echo "Error: LOCUST_TESTCASES_DIR environment variable not set"
	echo
	echo "Please:"
	echo "- Clone https://github.com/simiotics/locust-test-cases to your machine, to <clone path>"
	echo "- git -c <clone path> fetch origin"
	echo "- Set LOCUST_TESTCASES_DIR to the value of your <clone path>"
	echo
	echo "The Locust tests run against various branches of the simiotics/locust-test-cases repo"
	exit 1
fi

python -m unittest discover -v
