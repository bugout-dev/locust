from setuptools import find_packages, setup

from locust.version import LOCUST_VERSION

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="bugout-locust",
    version=LOCUST_VERSION,
    packages=find_packages(),
    install_requires=["pygit2", "PyYAML", "lxml", "pydantic"],
    extras_require={
        "dev": ["black", "mypy", "wheel"],
        "distribute": ["twine"],
    },
    description="Locust: Track changes to Python code across git refs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Neeraj Kashyap",
    author_email="neeraj@bugout.dev",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
    ],
    url="https://github.com/simiotics/locust",
    entry_points={
        "console_scripts": [
            "locust=locust.cli:main",
            "locust.git=locust.git:main",
            "locust.parse=locust.parse:main",
            "locust.render=locust.render:main",
            "locust.github=locust.ci_helpers.github:main",
        ]
    },
)
