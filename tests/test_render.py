import json
import os
import unittest

from google.protobuf.json_format import Parse

from locust import parse, render

from . import config


class TestLocustRender(unittest.TestCase):
    maxDiff = None

    def test_render_run(self):
        repo_dir = config.TESTCASES_DIR
        initial = f"{config.TESTCASES_REMOTE}/test_git_initial"
        terminal = f"{config.TESTCASES_REMOTE}/test_git_terminal"

        test_input_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_parse.json"
        )
        with open(test_input_fixture) as ifp:
            test_input = Parse(ifp.read(), parse.ParseResult())

        expected_result_fixture = os.path.join(
            config.TESTS_DIR, "fixtures", "test_render.json"
        )
        with open(expected_result_fixture) as ifp:
            expected_result = json.load(ifp)

        result = json.loads(render.run(test_input, "json", None))

        self.assertDictEqual(result, expected_result)
