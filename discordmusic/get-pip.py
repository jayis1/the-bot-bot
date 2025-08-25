#!python
# -*- coding: utf-8 -*-
# Copyright (c) 2008-2021 The pip developers (see AUTHORS.txt)
# Copyright (c) 2005-2008 Ian Bicking and contributors (see AUTHORS.txt)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""Bootstraps pip development installations.

This is a vendored script that can be used to install pip in a development
environment. It is not recommended to use this script for production
installations, as it may install an outdated version of pip.
"""

import os
import sys
import shutil
import subprocess
import tempfile
import textwrap
import zipfile


def _create_standalone_pip(version):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Create a standalone pip distribution
    pip_dir = os.path.join(temp_dir, "pip")
    os.makedirs(pip_dir)

    # Copy pip files
    for item in os.listdir(os.path.dirname(__file__)):
        if item.startswith("pip") and os.path.isdir(item):
            shutil.copytree(item, os.path.join(pip_dir, item))

    # Create a setup.py file
    with open(os.path.join(pip_dir, "setup.py"), "w") as f:
        f.write(textwrap.dedent("""
            from setuptools import setup, find_packages

            setup(
                name='pip',
                version='{version}',
                packages=find_packages(),
            )
        """.format(version=version)))

    # Create a wheel
    subprocess.check_call([sys.executable, "setup.py", "bdist_wheel"],
                            cwd=pip_dir)

    # Find the wheel file
    wheel_dir = os.path.join(pip_dir, "dist")
    wheel_file = [f for f in os.listdir(wheel_dir) if f.endswith(".whl")][0]
    wheel_path = os.path.join(wheel_dir, wheel_file)

    # Extract the wheel
    extract_dir = os.path.join(temp_dir, "extracted_pip")
    os.makedirs(extract_dir)
    with zipfile.ZipFile(wheel_path, "r") as zf:
        zf.extractall(extract_dir)

    # Return the path to the extracted pip
    return extract_dir


def _install_pip(target_dir, version):
    pip_path = _create_standalone_pip(version)

    # Install pip
    subprocess.check_call([sys.executable, "-m", "pip", "install", pip_path],
                            target=target_dir)


def main():
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="23.0.1")
    parser.add_argument("--target", default=None)
    args = parser.parse_args()

    # Install pip
    _install_pip(args.target, args.version)


if __name__ == "__main__":
    main()
