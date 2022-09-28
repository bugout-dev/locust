import os

from . import build

from tree_sitter import Language, Parser

assert (
    "go" in build.SUPPORTED_LANGUAGES
), "Golang is not supported by the current build of locust"

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
LIB_PATH = os.path.join(SCRIPT_DIR, build.LIBNAME)

GOLANG = Language(LIB_PATH, "go")

GOLANG_PARSER = Parser()
GOLANG_PARSER.set_language(GOLANG)


class TreeSitterAnalyzer:
    pass
