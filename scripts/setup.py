from setuptools import setup, find_packages
import os
import os.path as op
from glob import glob
from hub_manager import __version__

# Source dependencies from requirements.txt file.
try:
    with open("requirements.txt", "r") as f:
        lines = f.readlines()
        install_packages = [line.strip() for line in lines]
except FileNotFoundError:
    install_packages = []

setup(
    name="hub_manager",
    version=__version__,
    install_requires=install_packages,
    include_package_data=True,
    python_requires=">=3.7",
    author="Sarah Gibson",
    author_email="drsarahlgibson@gmail.com",
    url="https://sgibson91.github.io",
    # this should be a whitespace separated string of keywords, not a list
    keywords="development cli-tool management",
    description="CLI tool to interact with a BinderHub deployment",
    long_description=open("./README.md", "r").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    use_package_data=True,
    entry_points={"console_scripts": ["hub-manager = hub_manager.cli:main"]},
)
