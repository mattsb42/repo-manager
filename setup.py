"""repo-manager."""
import io
import os
import re

from setuptools import find_packages, setup

VERSION_RE = re.compile(r"""__version__ = ['"]([0-9b.]+)['"]""")
HERE = os.path.abspath(os.path.dirname(__file__))


def read(*args):
    """Read complete file contents."""
    return io.open(os.path.join(HERE, *args), encoding="utf-8").read()


def get_version():
    """Read the version from this module."""
    init = read("src", "repo_manager", "__init__.py")
    return VERSION_RE.search(init).group(1)


def get_requirements():
    """Read the requirements file."""
    raw_requirements = read("requirements.txt")
    requirements = []
    dependencies = []

    for req in raw_requirements.splitlines():
        req = req.strip()
        if not req:
            continue

        if req.startswith("#"):
            continue

        if "+" in req:
            dependencies.append(req)
        else:
            requirements.append(req)

    return requirements, dependencies


INSTALL_REQUIRES, DEPENDENCY_LINKS = get_requirements()

setup(
    name="github-repo-manager",
    version=get_version(),
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/mattsb42/repo-manager",
    author="Matt Bullock",
    author_email="m@ttsb42.com",
    maintainer="Matt Bullock",
    description="repo-manager",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    keywords="repo-manager repo_manager",
    data_files=["README.md", "CHANGELOG.md", "LICENSE", "requirements.txt"],
    license="Apache 2.0",
    install_requires=INSTALL_REQUIRES,
    dependency_links=DEPENDENCY_LINKS,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points=dict(console_scripts=["repo-manager=repo_manager:cli"]),
)
