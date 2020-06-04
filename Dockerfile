FROM continuumio/anaconda3
MAINTAINER Avi Yaeli <aviy@il.ibm.com>

RUN /opt/conda/bin/conda install jupyter -y --quiet
RUN mkdir /release & mkdir /data
ADD data/ /data

WORKDIR /release

ADD notebooks/images/*.png images/
RUN [ "python", "-c", "import nltk; nltk.download('words')" ]
RUN [ "python", "-c", "import nltk; nltk.download('punkt')" ]
RUN [ "python", "-c", "import nltk; nltk.download('stopwords')" ]

ADD ["notebooks/Dialog Flow Analysis Notebook(MASTER).ipynb","/release/Dialog Flow Analysis Notebook.ipynb"]
ADD ./notebooks/conversation_analytics_toolkit-1.0.latest-py2.py3-none-any.whl .
RUN pip install conversation_analytics_toolkit-1.0.latest-py2.py3-none-any.whl

RUN jupyter trust *.ipynb

# run jupyter notebook on port 7777
ENTRYPOINT ["/bin/bash", "-c", " /opt/conda/bin/jupyter notebook --notebook-dir=/release --ip='*' --port=7777 --NotebookApp.token='' --no-browser --allow-root"]