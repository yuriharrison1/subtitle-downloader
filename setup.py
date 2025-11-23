#!/usr/bin/env python3
"""
Setup script for Subtitle Downloader
"""

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from pathlib import Path

# Read the contents of README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
def read_requirements():
    requirements_path = Path("requirements.txt")
    if requirements_path.exists():
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

# Get version from package init or use setuptools_scm
def get_version():
    try:
        # Try to get version from setuptools_scm
        from setuptools_scm import get_version as scm_get_version
        return scm_get_version()
    except (ImportError, LookupError):
        # Fallback to static version
        init_path = Path("src") / "subtitle_downloader" / "__init__.py"
        if init_path.exists():
            with open(init_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("__version__"):
                        return line.split("=")[1].strip().strip('"').strip("'")
        return "1.0.0"

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches the version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG', '')
        version = get_version()

        if tag != f'v{version}':
            info = f"Git tag: {tag} does not match the version of this app: v{version}"
            sys.exit(info)

setup(
    name="subtitle-downloader",
    version=get_version(),
    description="Automatic subtitle downloader with file manager integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your@email.com",
    maintainer="Your Name",
    maintainer_email="your@email.com",
    url="https://github.com/yourusername/subtitle-downloader",
    project_urls={
        "Homepage": "https://github.com/yourusername/subtitle-downloader",
        "Documentation": "https://github.com/yourusername/subtitle-downloader#readme",
        "Bug Reports": "https://github.com/yourusername/subtitle-downloader/issues",
        "Source": "https://github.com/yourusername/subtitle-downloader",
        "Changelog": "https://github.com/yourusername/subtitle-downloader/releases",
    },
    package_dir={"": "src"},
    packages=find_packages(
        where="src",
        include=["subtitle_downloader", "subtitle_downloader.*"],
        exclude=["tests", "tests.*", "*.tests", "*.tests.*"]
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX :: Linux :: Ubuntu",
        "Operating System :: POSIX :: Linux :: Debian", 
        "Operating System :: POSIX :: Linux :: Fedora",
        "Operating System :: POSIX :: Linux :: openSUSE",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Multimedia :: Video",
        "Topic :: Desktop Environment",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "qt": [
            "PyQt5>=5.15,<6.0",
            "PyQt5-Qt5>=5.15,<6.0",
            "PyQt5-sip>=12.0,<13.0",
        ],
        "gtk": [
            "PyGObject>=3.42,<4.0",
        ],
        "full": [
            "PyQt5>=5.15,<6.0",
            "PyQt5-Qt5>=5.15,<6.0",
            "PyQt5-sip>=12.0,<13.0",
            "PyGObject>=3.42,<4.0",
        ],
        "dev": [
            "pytest>=7.0,<8.0",
            "pytest-cov>=4.0,<5.0",
            "pytest-mock>=3.0,<4.0",
            "black>=23.0,<24.0",
            "flake8>=6.0,<7.0",
            "mypy>=1.0,<2.0",
            "pre-commit>=3.0,<4.0",
            "build>=0.10,<1.0",
            "twine>=4.0,<5.0",
        ],
        "test": [
            "pytest>=7.0,<8.0",
            "pytest-cov>=4.0,<5.0",
            "pytest-mock>=3.0,<4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "download-subtitle=subtitle_downloader.__main__:main",
        ],
        "subtitle_downloader.providers": [
            "opensubtitles=subtitle_downloader.core:SubtitleDownloader",
        ],
    },
    include_package_data=True,
    package_data={
        "subtitle_downloader": [
            "*.json",
            "*.desktop", 
            "*.py",
        ],
    },
    data_files=[
        ("share/applications", ["share/file-manager/actions/download-subtitle.desktop"]),
        ("share/kio/servicemenus", ["share/file-manager/servicemenus/download-subtitle.desktop"]),
    ],
    keywords=[
        "subtitle",
        "download", 
        "video",
        "opensubtitles",
        "file-manager",
        "linux",
        "desktop",
    ],
    zip_safe=False,
    cmdclass={
        'verify': VerifyVersionCommand,
    },
    # Platform specific dependencies
    platforms=["Linux"],
    license="GPL-3.0-or-later",
    # Metadata for PyPI
    options={
        "bdist_wheel": {
            "universal": False,  # Pure Python but platform-specific due to Qt/GTK
        }
    },
)
