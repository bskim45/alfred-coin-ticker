# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

## [2.0.0](https://github.com/bskim45/alfred-coin-ticker/compare/1.1.0...2.0.0) (2022-05-08)

### Breaking changes

Python 2 has been removed from macOS 12.3 Monterey,
and default system Python is now Python 3.8.
(https://www.alfredapp.com/help/kb/python-2-monterey/)

This is first version that supports macOS 12.3+ (Python 3.8+).

Please note that **Python 2 and Alfred 3 is no longer supported.**
If you are using macOS 12.2 or below, please do not upgrade to 2.0.0+
and keep using 1.1.0.

Special thanks to @NorthIsUp for porting [alfred-workflow](https://github.com/NorthIsUp/alfred-workflow-py3) to Python 3.

### Features

* support python3 (macOS 12.3+) ([#2](https://github.com/bskim45/alfred-coin-ticker/issues/2)) ([0593613](https://github.com/bskim45/alfred-coin-ticker/commit/0593613b9e279e63148f4bdbdfcf2071121ddea0))


## [1.1.0](https://github.com/bskim45/alfred-coin-ticker/compare/1.0.1...1.1.0) (2022-02-02)

### Features

* add modifier actions to ticker items ([f90c62a](https://github.com/bskim45/alfred-coin-ticker/commit/f90c62ac97f586511e09c4decab148afb740ed74))


### [1.0.1](https://github.com/bskim45/alfred-coin-ticker/compare/1.0.0...1.0.1) (2022-01-29)

### Bug Fixes

* Use normalized coin names for coinmarketcap urls ([1c90752](https://github.com/bskim45/alfred-coin-ticker/commit/1c90752d64840ebd98f3bae26287d4699b872328))
