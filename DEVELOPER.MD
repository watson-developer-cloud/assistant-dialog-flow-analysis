# DEVELOPER ZONE

- [Development environment](#devenv)
- [Setup and Configuration](#setup)
- [Build](#build-script)
- [Unit tests](#unit-test)
- [System test](#sys-test)
- [Release process](#release)


<a id="devenv"></a> 

## Development Environment 
Prerequisite installations:
* Python 3.6+
* Jupyter notebook (peferably Anaconda)

Repo structure
|
|-- build - temporary folder for the build process
|-- data - sample datasets for testing
|-- dist - output of the build process
|-- notebooks - the main Dailog Flow Analaysis notebook for dev/test is here
|-- src - the sources of the conversation-analytics-toolkit library
|-- test - tests for the conversation-analytics-toolkit library

<a id="setup"></a> 

## Setup and Configuration
### Versioning
We use [SemVer](https://semver.org/) versioning scheme.  Set major and minor version manually in `VERSION` file.  Patch versioning are autoincremented by the builg process.

### Dependencies
Update list of package dependencies in `requirements.txt` (for local tests) and `install_requires` section in `setup.py` for package distribution.

<a id="build-script"></a> 

## Build
To run a full build  run the automated build:
```
npm run build
```

Per need, you can run specific build steps: 
1. minify js and css
```
npm run minify
```
2. build a wheel file for the release
```
python setup.py bdist_wheel --universal
```

<a id="unit-test"></a> 

## Unit Testing 
1. create virtualenv for testing
`python -m venv .py36`
2. invoke the virual environment
`source .py36/bin/activate`
3. install the dev environment
`pip install -r dev_requirements.txt`
4. run the tests (optionally with verbose flag)
`pytest -v`
5. exit from the virtual environment
`deactivate`

<a id="sys-test"></a> 

## System Testing 
We use a docker that builds on a clean Anaconda/Python 3 distribution
1. Build the systest docker
`docker build -t "systest" .`
3. Run the systest docker
This will start the Jupyter server and will open the browser at the Jupyter client
`open http://127.0.0.1:7777/ & docker run -i -t -p 7777:7777 systest`

> Note, the docker jupyter server requires a few seconds to load, so initially the web page will not show anything. Click page reload after 2-3 seconds to see the Jupyter client.
  
<a id="release"></a> 

## release
Under construction
### 1. update latest version of Release Candidate notebook
- make a copy of MASTER notebook(Master), save as `Dialog Flow Analysis Notebook(RC)`
- remove the development cells:  
    - remove section 2.0 from TOC
    - remove section 2.0 
- test it
- export standalone-demo.html
- Cleanup all outputs and save the notebook
### 2. update version for Watson Studio
- make a copy of MASTER notebook(RC), save as `Dialog Flow Analysis Notebook(WS)`
- change to use !pip install option
- add 1.4 to TOC, remove 2.4
- add section 1.4
- remove section 2.4
- replace final export
### 2. Run the full build
```
npm run build
```
### 3. Sync with assistant-dialog-flow-analysis repo (local)  
in `assistant-dialog-flow-analysis git:(master)` run
```
git pull
git checkout -b "<feature>"
```
from `conversation-analytics-toolkit` run
```
./sync-repos.sh
```
in `assistant-dialog-flow-analysis git:(master)` run
```
git add .
git commit -m "<comment>"
```
### 4. Create a PR against remote repo.
```
git push -u origin <feature>
```
from github.com, create a PR and merge.