# Withings Public API Client


![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fiandday%2Fwithingpy%2Frefs%2Fheads%2Fmain%2Fpyproject.toml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/iandday/withingpy/ci.yml?label=Build)](https://github.com/iandday/withingpy/actions/workflows/ci.yml)
[![Test PyPi](https://img.shields.io/pypi/v/withingpy?pypiBaseUrl=https%3A%2F%2Ftest.pypi.org&label=test%20pypi
)](https://test.pypi.org/manage/project/withingpy/releases/)[![PyPi](https://img.shields.io/pypi/v/withingpy?pypi)](https://pypi.org/manage/project/withingpy/releases/)


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

