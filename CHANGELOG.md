## [1.6.1](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.6.0...v1.6.1) (2021-02-11)


### Bug Fixes

* empty commit - just to trigger a release ([370a124](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/370a124faebeeb21db17f17d58de6ab2cb954194))

# [1.6.0](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.5.1...v1.6.0) (2021-01-27)


### Features

* added consecutive filtering ([30f0c0e](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/30f0c0e4f2ae163dffea44f78680b9fa9c38c42c))

## [1.5.1](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.5.0...v1.5.1) (2021-01-04)


### Bug Fixes

* handle empty nodes_visited in WAVI logs ([2a46d4d](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/2a46d4dea2fb739abb870336a3d16fdaf0af5285))
* limit scipy version to 1.5.3 to support Python 3.6 ([3c6bf47](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/3c6bf476ddf394095ce361cdff93b5827647fe0a))
* remove scipy from the dependency list to solve Python 3.6 installation issue ([e22ef6b](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/e22ef6b44602ebbb657419491397531ac6545236))
* remove support for Python 3.6 as TOX fails to install it due to scipy 1.5.4 dependency which is not supported any more for Python 3.6 ([62017e2](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/62017e2213ef82bef902ac27b225c74e720094be))
* support for python 3.8/3.9 ([1d709fe](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/1d709fee0a0f72b9ffed2571b9a7b8767ecace36))
* support for python 3.8/3.9 ([73d1893](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/73d1893448fa50b60cb5feb431e0cd577b3ed78d))

# [1.5.0](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.4.0...v1.5.0) (2020-12-01)


### Features

* implemented capability to semi automatically create a milestone chart based on regular expression search in the workspace ([a28f27b](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/a28f27b38f1aa02c6fccc5f73be2186b0eaa4e67))

# [1.4.0](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.3.0...v1.4.0) (2020-11-24)


### Features

* removed support for Python 3.5 end of service which doesn't support Pandas 1.1.x ([c5f18d3](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/c5f18d3d312da29d61e84c6d1179c396cbfbbb40))
* support for pandas 1.1.x. stop support for Python 3.5 ([93862c4](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/93862c4dfdfacdf4dba0421c7f0f35d6e437077d))
* upgrade to pandas 1.1.x ([d0b0b8d](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/d0b0b8db43a72d7b2b4a69fe73cf017ee1c64eb3))

# [1.3.0](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.2.1...v1.3.0) (2020-11-01)


### Features

* support for reverse flows and trend flows ([0223af4](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/0223af4df18f9a34679e3b89436b4653da3225e6))

## [1.2.1](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.2.0...v1.2.1) (2020-10-20)


### Bug Fixes

* svg_export button not loading ([bba7271](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/bba7271efd8788ac23b35518003aff4d44a1b6e2))

# [1.2.0](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.1.2...v1.2.0) (2020-10-19)


### Features

* implemented simplify_consecutive_duplicates() to remove duplciate consecutive nodes from the graph ([acccdb9](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/acccdb90943cd3476724e2642f7f1ea67785ab47))

## [1.1.2](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.1.1...v1.1.2) (2020-10-13)


### Bug Fixes

* parsing error when branch_exited is missing from payload ([1ba44ef](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/1ba44ef73445cc9519a6692d09f855ec0560b8b5))

## [1.1.1](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.1.0...v1.1.1) (2020-09-30)


### Bug Fixes

* new release fix ([#22](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/issues/22)) ([bd210a9](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/bd210a925f0c4b68a06c6948af5bcb7d408827a5))

# [1.1.0](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.9...v1.1.0) (2020-09-07)


### Features

* added support for context variables extraction and filtering ([7db2e9e](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/7db2e9e9edbc8485fc0ac99d2df2e1423084aef9))

## [1.0.9](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.8...v1.0.9) (2020-08-06)


### Bug Fixes

* updated pandas dependency to support Python3.8.5 + pandas0.25.3 environments ([0fbfaff](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/0fbfaffb3d311b8b500c77dc973872dc6a84a58e))

## [1.0.8](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.7...v1.0.8) (2020-08-04)


### Bug Fixes

* updated sample logs to original Logs API format ([#17](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/issues/17)) ([916f8fc](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/916f8fc175b4424530594a2f2b616a10d3ce11a8))

## [1.0.7](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.6...v1.0.7) (2020-06-18)


### Bug Fixes

* solve the version inconsistency between package meta and release ([11e399d](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/11e399d94edf0f08db99cd46ceec61503bc54b72))

## [1.0.6](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.5...v1.0.6) (2020-06-17)


### Bug Fixes

* highlighted steps in conversation transcript were highlighting the non negative utterances ([f97043c](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/f97043c5b42cb753f93748976c8913bfe3760f21))

## [1.0.5](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.4...v1.0.5) (2020-06-15)


### Bug Fixes

* pip install on watson studio without a custom environment ([a883c67](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/a883c676a2b294701fe940bb1d503897ee5f3db4))

## [1.0.4](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.3...v1.0.4) (2020-06-11)


### Bug Fixes

* update setup.py to remove invalid content for PyPi ([9eb0ec2](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/9eb0ec204c37f0b9802fd8dcfb95cf359d9e4cd5))

## [1.0.3](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.2...v1.0.3) (2020-06-11)


### Bug Fixes

* remove invalid description from package.json ([676a927](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/676a927318f2ff6f240f329e2e517c23ae43c063))

## [1.0.2](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.1...v1.0.2) (2020-06-11)


### Bug Fixes

* update pypi server url ([20e3383](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/20e3383bc9814163340481a1f5bd20db2809adb6))

## [1.0.1](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/compare/v1.0.0...v1.0.1) (2020-06-11)


### Bug Fixes

* update pypi server ([97bf319](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/97bf3190a66a255638c2108315a9bb00e1dd3aef))

# 1.0.0 (2020-06-11)


### Bug Fixes

* add package.json back ([6b50e67](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/6b50e673f33eaa19402272033ce8fd6299a01974))
* Change publish branch to master ([65163fc](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/65163fc03fd6382b657d83f05a0bd1b606e5aef6))
* remove dry-run mode ([73b5949](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/73b594923b7d90fbc756911e8040c613467fec6b))
* update pypi username ([1419a3a](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/commit/1419a3a2f78fea19b8f0e1660730ddfc7f6a44d7))
