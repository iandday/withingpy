# Withings Public API Client


![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fiandday%2Fwithingpy%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/iandday/withingpy/ci.yml?label=Build)](https://github.com/iandday/withingpy/actions/workflows/ci.yml)
[![PyPi](https://img.shields.io/pypi/v/withingpy?pypi)](https://pypi.org/manage/project/withingpy/releases/)
[![Release](https://github.com/iandday/withingpy/actions/workflows/release.yml/badge.svg)](https://github.com/iandday/withingpy/actions/workflows/release.yml)
[![Generate Documentation](https://github.com/iandday/withingpy/actions/workflows/generate_docs.yml/badge.svg)](https://github.com/iandday/withingpy/actions/workflows/generate_docs.yml)

A python package designed to utilize the [Withings Public API](https://developer.withings.com/api-reference) to collect health data from [supported devices](https://developer.withings.com/developer-guide/v3/data-api/all-available-health-data).

<p align="center">
  <img src="docs/img/logo.svg" alt="Withings Logo" width="200"/>
</p>


## Documentation

This README is just a short intro to the package.
For a quick start and detailed information please see the [documentation](https://iandday.github.io/withingpy/).
The documentation is also available in the `docs` folder of the source code and can be built locally with [MkDocs](https://www.mkdocs.org/) using the command `just docs`.

## Supported Measurements

- [x] Weight
- [x] Fat Mass
- [x] Muscle Mass
- [x] Water Mass
- [x] Visceral Fat
- [x] Bone Mass
- [x] Lean Mass
- [ ] Standing Heart Rate
- [ ] Vascular Age
- [ ] Basal Metabolic Rate

