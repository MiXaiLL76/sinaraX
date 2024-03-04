#!/usr/bin/python3
import setuptools
from setuptools import setup

version_file = "sinaraX/_version.py"


def get_version():
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"], locals()["__author__"]

def readme():
    with open("README.md", encoding="utf-8") as f:
        content = f.read()
    return content


def parse_requirements(fname="requirements/runtime.txt", with_version=True):
    """Parse the package dependencies listed in a requirements file but strips
    specific versioning information.
    Args:
        fname (str): path to requirements file
        with_version (bool, default=False): if True include version specs
    Returns:
        List[str]: list of requirements items
    CommandLine:
        python -c "import setup; print(setup.parse_requirements())"
    """
    import re
    import sys
    from os.path import exists

    require_fpath = fname

    def parse_line(line):
        """Parse information from a line in a requirements text file."""
        if line.startswith("-r "):
            # Allow specifying requirements in other files
            target = line.split(" ")[1]
            for info in parse_require_file(target):
                yield info
        else:
            info = {"line": line}
            if line.startswith("-e "):
                info["package"] = line.split("#egg=")[1]
            else:
                # Remove versioning from the package
                pat = "(" + "|".join([">=", "==", ">"]) + ")"
                parts = re.split(pat, line, maxsplit=1)
                parts = [p.strip() for p in parts]

                info["package"] = parts[0]
                if len(parts) > 1:
                    op, rest = parts[1:]
                    if ";" in rest:
                        # Handle platform specific dependencies
                        # http://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-platform-specific-dependencies
                        version, platform_deps = map(str.strip, rest.split(";"))
                        info["platform_deps"] = platform_deps
                    else:
                        version = rest  # NOQA
                    info["version"] = (op, version)
            yield info

    def parse_require_file(fpath):
        with open(fpath) as f:
            for line in f.readlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    yield from parse_line(line)

    def gen_packages_items():
        if exists(require_fpath):
            for info in parse_require_file(require_fpath):
                parts = [info["package"]]
                if with_version and "version" in info:
                    parts.extend(info["version"])
                if not sys.version.startswith("3.4"):
                    # apparently package_deps are broken in 3.4
                    platform_deps = info.get("platform_deps")
                    if platform_deps is not None:
                        parts.append(";" + platform_deps)
                item = "".join(parts)
                yield item

    packages = list(gen_packages_items())
    return packages

__version__, __author__ = get_version()

setup(
    name="sinaraX",
    version=__version__,
    description="sinaraX - TUI for sinaraml cli",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/MiXaiLL76/sinaraX",
    author=__author__,
    author_email="mike.milos@yandex.ru",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.6",
    install_requires=parse_requirements("requirements.txt"),
    data_files=[
        "requirements.txt",
    ],
    include_package_data=True,
    entry_points="""
        [console_scripts]
        sinaraX=sinaraX.__main__:main
    """,
)
