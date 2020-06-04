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

#first clean the build directory
shutil.rmtree('./build',ignore_errors=True)

with open("README.md", "r") as fh:
    long_description = fh.read()

# Meta information
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)

# increment version by revision
_major, _minor, _revision= version.split('.',3)[:3]
version = _major + '.' + _minor + '.' + str(int(_revision)+1)

# Save version and author to __meta__.py
path = os.path.join(dirname, 'src', 'conversation_analytics_toolkit', '__meta__.py')
data = '''# Automatically created. Please do not edit.
__version__ = u'%s'

__author__ = u'Avi Yaeli'
''' % version
with open(path, 'wb') as F:
    F.write(data.encode())

setuptools.setup(
    # Basic info
    name='conversation_analytics_toolkit',
    version=version,
    author='IBM Watson',
    author_email='watdevex@us.ibm.com',
    maintainer='Avi Yaeli',
    maintainer_email='aviy@il.ibm.com',
    url='https://github.com/watson-developer-cloud/assistant-dialog-flow-analysis',
    description='Dialog Flow Analysis Tool for Watson Assistant',
    license='Apache 2.0',
    long_description=long_description,
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

file = open('VERSION', 'w')
file.write(version)
file.close()

minor_stable =  _major + '.' + _minor + '.latest'
shutil.copyfile("./dist/conversation_analytics_toolkit-" + version + "-py2.py3-none-any.whl",
        "./dist/conversation_analytics_toolkit-" + minor_stable + "-py2.py3-none-any.whl")

print("")
print("****************************************")
print("* generated wheel for revision: " + version + " * ")
print("****************************************")
