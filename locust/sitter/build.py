"""
Builds locust-sitter.so library which will be used to add language support to locust using Tree-Sitter.
"""

import os
from typing import Dict

from tree_sitter import Language

SUPPORTED_LANGUAGES: Dict[str, str] = {"go": "tree-sitter-go"}


def main() -> None:
    script_dir = os.path.realpath(os.path.dirname(__file__))
    build_path = os.path.join(script_dir, "locust-sitter.so")
    locust_root_dir = os.path.dirname(os.path.dirname(script_dir))
    vendor_dir = os.path.join(locust_root_dir, "vendor")
    language_dirs = [os.path.join(vendor_dir, v) for v in SUPPORTED_LANGUAGES.values()]
    Language.build_library(build_path, language_dirs)


if __name__ == "__main__":
    main()
