import json
import os
import unittest

from google.protobuf.json_format import MessageToDict

from locust import git, git_pb2

from . import config


class TestLocustGit(unittest.TestCase):
    maxDiff = None

    def test_git_run(self):
        repo_dir = config.TESTCASES_DIR
        initial = f"{config.TESTCASES_REMOTE}/test_git_initial"
        terminal = f"{config.TESTCASES_REMOTE}/test_git_terminal"

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_git.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        expected_result_json = json.loads(expected_result_str)

        result = git.run(repo_dir, initial, terminal)
        result_json = MessageToDict(result, preserving_proto_field_name=True)

        self.assertDictEqual(result_json, expected_result_json)

    def test_git_null_revision(self):
        """
        Tests that the null revision is correctly handled by Locust.
        """
        repo_dir = config.TESTCASES_DIR
        initial = f"null"
        terminal = f"{config.TESTCASES_REMOTE}/test_git_terminal"

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_git_null.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result_str = repo_dir.join(
                ifp.read().strip().split(config.REPO_DIR_TOKEN)
            )
        expected_result_json = json.loads(expected_result_str)

        result = git.run(repo_dir, initial, terminal)
        result_json = MessageToDict(result, preserving_proto_field_name=True)

        self.assertDictEqual(result_json, expected_result_json)
