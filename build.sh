#!/bin/bash

#1. minify js/css
npm run minify

#2. build a wheel file for the release
python setup.py bdist_wheel --universal

#3. copy distribution file to testing locations
cp dist/conversation_analytics_toolkit-1.0.latest-py2.py3-none-any.whl release/1.0.latest
cp dist/conversation_analytics_toolkit-1.0.latest-py2.py3-none-any.whl notebooks

#4. copy latest notebook 

cp "notebooks/Dialog Flow Analysis Notebook(MASTER).ipynb" ./release/1.0.latest/Dialog\ Flow\ Analysis\ Notebook.ipynb

#5 copy images 
cp notebooks/images/*.png ./release/1.0.latest/images