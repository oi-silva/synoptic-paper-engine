[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "synoptic-paper-engine"
version = "1.0.0"
authors = [
  { name="Your Name", email="your.email@example.com" },
]
description = "An AI-powered command-line toolkit for advanced academic literature review."
readme = "README.md"
requires-python = ">=3.8"
license = { file="LICENSE" }
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering",
    "Environment :: Console",
    "Development Status :: 4 - Beta",
]

dependencies = [
    "requests",
    "colorama",
    "tqdm",
    "llama-cpp-python"
]

[project.urls]
Homepage = "https://github.com/oi-silva/synoptic-paper-engine"
Issues = "https://github.com/oi-silva/"

[project.scripts]
spe = "spe.main:main_menu"