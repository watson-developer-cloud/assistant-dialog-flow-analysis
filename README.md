# Watson Assistant Dialog Flow Analysis

> Note: help us stay in touch and improve this notebook by clicking on the :star: star icon (top right).

This repository hosts the the Watson Assistant Dialog Flow Analysis Notebook and the underlying conversation analytics toolkit library.

<details>
 <summary>Table of Contents</summary>

 
 [Introduction](#introduction)<br>
 [Getting Started](#getting-started)<br>
 [Guides](#guides)<br>
 [Frequently Asked Questions](#frequently-asked-questions)<br>
 [License](#license)<br>
 [Contributing](#contributing)<br>

</details>

## Introduction

The Watson Assistant Dialog Flow Analysis Notebook can help you assess and analyze user journeys and issues related to the dialog flow of ineffective (low quality) conversations based on production logs.  The notebook can help you with questions such as:
- What are the common conversation steps and flows within the assistant 
- Which flows have low task completion rates and high abandonment (ineffective conversations)
- Where along the dialog steps users lose engagement with your assistant
- What are common terms and steps that may lead to abandonment

This notebook extends the [Measure and Analyze notebooks](https://github.com/watson-developer-cloud/assistant-improve-recommendations-notebook) by providing additional capabilities to assess and analyze effectiveness - focused more on issues related to the dialog flow.  For more details, check out [IBM Watson Assistant Continuous Improvement Best Practices](https://github.com/watson-developer-cloud/assistant-improve-recommendations-notebook/raw/master/notebook/IBM%20Watson%20Assistant%20Continuous%20Improvement%20Best%20Practices.pdf).


<img src="./notebooks/images/flow-vis.png" width="50%">

## Getting Started

The notebook requires a Jupyter Notebook environment and Python 3.6+.   You can either install Jupyter Notebook to run locally or you can use Watson Studio on the cloud.

### Using Jupyter Notebook
1. Install Python 3.6+
2. Install Jupyter notebook. Checkout the [Jupyter/IPython Notebook Quick Start Guide](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/install.html) for more details
3. Download the [notebooks/Dialog Flow Analysis Notebook.ipynb](https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis/blob/master/notebooks/Dialog%20Flow%20Analysis%20Notebook.ipynb) file.   
4. Start jupyter server `jupyter notebook`
5. Run the `Dialog Flow Analysis Notebook.ipynb`

### Using Watson Studio
1. In Watson Studio, select `Add to Project`-->`Notebook`.  Choose `From URL` and paste this [url](https://raw.githubusercontent.com/watson-developer-cloud/assistant-dialog-flow-analysis/master/notebooks/Dialog%20Flow%20Analysis%20Notebook.ipynb).  Alternately you can select `From file` and upload the `notebooks/Dialog Flow Analysis Notebook.ipynb` file.

Alternately, you can import and modify the [sample notebook on Watson Studio Gallery](https://dataplatform.cloud.ibm.com/exchange/public/entry/view/013c690997e27f3a8d9133265327a9e5?context=wdp).


## Guides
* Learn more about the Dialog Flow Analysis in this [blog](https://medium.com/ibm-watson/do-you-know-where-and-why-users-drop-off-the-conversation-6246e99baddc)
* See a live example output of the notebook on [Watson Studio Gallery](https://dataplatform.cloud.ibm.com/exchange/public/entry/view/013c690997e27f3a8d9133265327a9e5?context=wdp)


## Frequently Asked Questions
See [FAQ.md](FAQ.md) for frequently asked questions 

## License
This library is licensed under the [Apache 2.0 license](http://www.apache.org/licenses/LICENSE-2.0).

## Contributing 
See [CONTRIBUTING.md](CONTRIBUTING.md) and [DEVELOPER.MD](DEVELOPER.MD) for more details on how to contribute

## Contributor List


| | | | | |
:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:|
<img src="https://avatars3.githubusercontent.com/u/9696082?s=460&u=459ccd11b224e202f41b5309f6ae881c2714e7ab&v=4" alt="Avi Yaeli" width=80/> <br/> <b>[Avi Yaeli](https://github.com/ayaeli)<b> | <img src="https://avatars1.githubusercontent.com/u/13829603?s=400&u=293450598db5209eb471769b5032776034bfcc27&v=4" alt="Sergey Zeltyn" width=80/> <br/> <b>[Sergey Zeltyn](https://github.com/Sergey-Zeltyn)<b> | <img src="https://avatars0.githubusercontent.com/u/43827532?s=400&u=817665e525cad70970ea6e0319dda98d1f26910d&v=4" alt="Zhe Zhang" width=80/> <br/> <b>[Zhe Zhang](https://github.com/zzhang13)<b> | <img src="https://avatars1.githubusercontent.com/u/24845274?s=400&u=ca3e3ab4bb4c0d6e16b984dc4b4a95fffe53a40c&v=4" alt="Eric Wayne" width=80/> <br/> <b>[Eric Wayne](https://github.com/eric-wayne)<b> | <img src="https://avatars0.githubusercontent.com/u/11946512?s=400&u=379d439244faf5202735603dfa23d72dd07bfa0e&v=4" alt="David Boaz" width=80/> <br/> <b>[David Boaz](https://github.com/boazdavid)<b> |

