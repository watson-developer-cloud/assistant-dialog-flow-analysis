# -*- coding: utf8 -*-
#
# This file were created by Python Boilerplate. Use Python Boilerplate to start
# simple, usable and best-practices compliant Python projects.
#
# Learn more about it at: http://github.com/fabiommendes/python-boilerplate/
#

import os
import setuptools
import shutil

__version__ = '1.0.3'

# Convert README.md to README.rst for pypi
try:
    from pypandoc import convert_file

    def read_md(f):
        return convert_file(f, 'rst')

    # read_md = lambda f: convert(f, 'rst')
except:
    print('warning: pypandoc module not found, '
          'could not convert Markdown to RST')

    def read_md(f):
        return open(f, 'rb').read().decode(encoding='utf-8')
    # read_md = lambda f: open(f, 'rb').read().decode(encoding='utf-8')

setuptools.setup(
    # Basic info
    name='conversation_analytics_toolkit',
    version=__version__,
    author='IBM Watson',
    author_email='watdevex@us.ibm.com',
    maintainer='Avi Yaeli',
    maintainer_email='aviy@il.ibm.com',
    url='https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis',
    description='Dialog Flow Analysis Tool for Watson Assistant',
    license='Apache 2.0',
    long_description=read_md('README.md'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    # Packages and depencies
    package_dir={'': 'src'},
    packages=setuptools.find_packages('src'),
    install_requires=[
        'pandas~=0.24.0',
        'nltk>=3.4.0',
        'textblob>=0.15.3',
        'scikit-learn>=0.21.3',
        'tqdm>=4.31.1',
        'ipywidgets>=7.4.2',
        'ibm-watson>=4.3.0',
        'plotly>=4.5.0',
        'requests>=2.18.4'
    ],

    # extras_require={
    #     'dev': [
    #     ]
    # },

    # Data files
    package_data={
        'conversation_analytics_toolkit': [
            #'images/*.*',
            '*.min.css',
            '*.min.js'
        ],
    },

    zip_safe=False,
    platforms='any',
)
