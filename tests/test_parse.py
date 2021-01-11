import json
import os
import unittest

from google.protobuf.json_format import MessageToDict, Parse

from locust import git, parse

from . import config


class TestLocustParse(unittest.TestCase):
    maxDiff = None

    def test_parse_run(self):
        repo_dir = config.TESTCASES_DIR
        test_input_fixture = os.path.join(config.TESTS_DIR, "fixtures", "test_git.json")
        with open(test_input_fixture) as ifp:
            test_input_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        test_input = Parse(test_input_str, git.GitResult())

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_parse.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        expected_result_json = json.loads(expected_result_str)

        result = parse.run(test_input, [])
        result_json = MessageToDict(result, preserving_proto_field_name=True)

        self.assertDictEqual(result_json, expected_result_json)

    def test_parse_dependencies(self):
        repo_dir = config.TESTCASES_DIR
        test_input_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_git_dependencies.json"
        )
        with open(test_input_fixture) as ifp:
            test_input_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        test_input = Parse(test_input_str, git.GitResult())

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_parse_dependencies.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        expected_result_json = json.loads(expected_result_str)

        result = parse.run(test_input, [])
        result_json = MessageToDict(result, preserving_proto_field_name=True)

        self.assertDictEqual(result_json, expected_result_json)
