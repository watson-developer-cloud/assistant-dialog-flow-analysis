# (C) Copyright IBM Corp. 2019, 2020.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
#import requests
from IPython.display import display, Javascript, HTML
import json
import datetime
import os
import os.path
import pkgutil
import inspect
import conversation_analytics_toolkit as cat

def read_file(filename):    
    with open(filename, 'r') as file:
        data = file.read().replace('<style>', '').replace('</style>', '')
        #print(data)
    return data

def add_style_to_header(css_string):
    display(Javascript("""
        var newStyle = document.createElement("style");
        newStyle.innerHTML = `%s`;
        document.getElementsByTagName("head")[0].appendChild(newStyle);
    """ % (css_string)))

if not cat.is_production() and not cat.is_forced_production_mode():
    project_folder = cat._get_src_project_folder()
    
    #add CSS to header instead of in body cell (prevent styling from disappearing even if output cell is deleted)
    add_style_to_header(read_file(os.path.join(project_folder, "src", "conversation_analytics_toolkit", "flowchart.css")))
    add_style_to_header(read_file(os.path.join(project_folder, "src", "conversation_analytics_toolkit", "transcript.css")))
    add_style_to_header(read_file(os.path.join(project_folder, "src", "conversation_analytics_toolkit", "wordpackchart.css")))
    add_style_to_header(read_file(os.path.join(project_folder, "src", "conversation_analytics_toolkit", "wa_dialog_chart.css")))

    display(Javascript("require.config({paths: {d3: 'https://cdnjs.cloudflare.com/ajax/libs/d3/4.13.0/d3.min'}});"))
    display(Javascript("require.config({paths: {lodash: 'https://cdn.jsdelivr.net/npm/lodash@4.17.15/lodash.min'}});"))
    display(Javascript(filename=os.path.join(project_folder, "src","conversation_analytics_toolkit", "flowchart2.js")))
    display(Javascript(filename=os.path.join(project_folder, "src","conversation_analytics_toolkit", "transcript.js")))
    display(Javascript(filename=os.path.join(project_folder, "src","conversation_analytics_toolkit", "wordpackchart.js")))   
   
    display(Javascript(filename=os.path.join(project_folder, "src", "conversation_analytics_toolkit", "wa_model.js")))
    display(Javascript(filename=os.path.join(project_folder, "src", "conversation_analytics_toolkit", "wa_tree.js")))
    display(Javascript(filename=os.path.join(project_folder, "src", "conversation_analytics_toolkit", "wa_node_details.js")))
    display(Javascript(filename=os.path.join(project_folder, "src", "conversation_analytics_toolkit", "wa_dialog_chart.js")))
else:
    flowchart_css = pkgutil.get_data(__package__, 'flowchart.min.css').decode('utf-8')
    flowchart_js = pkgutil.get_data(__package__, 'flowchart2.min.js').decode('utf-8')
    transcript_css = pkgutil.get_data(__package__, 'transcript.min.css').decode('utf-8')
    transcript_js = pkgutil.get_data(__package__, 'transcript.min.js').decode('utf-8')
    wordpackchart_css = pkgutil.get_data(__package__, 'wordpackchart.min.css').decode('utf-8')
    wordpackchart_js = pkgutil.get_data(__package__, 'wordpackchart.min.js').decode('utf-8')

    wa_model_js = pkgutil.get_data(__package__, 'wa_model.min.js').decode('utf-8')
    wa_tree_js = pkgutil.get_data(__package__, 'wa_tree.min.js').decode('utf-8')
    wa_node_details_js =  pkgutil.get_data(__package__, "wa_node_details.min.js").decode('utf-8')
    wa_dialog_chart_js = pkgutil.get_data(__package__, 'wa_dialog_chart.min.js').decode('utf-8')
    wa_dialog_chart_css = pkgutil.get_data(__package__, 'wa_dialog_chart.min.css').decode('utf-8')

    #add CSS to header instead of in body cell (prevent styling from disappearing even if output cell is deleted)
    add_style_to_header(flowchart_css)
    add_style_to_header(transcript_css)
    add_style_to_header(wordpackchart_css)
    add_style_to_header(wa_dialog_chart_css)
    
    display(Javascript("require.config({paths: {d3: 'https://cdnjs.cloudflare.com/ajax/libs/d3/4.13.0/d3.min'}});"))
    display(Javascript("require.config({paths: {lodash: 'https://cdn.jsdelivr.net/npm/lodash@4.17.15/lodash.min'}});"))
    display(Javascript(data=flowchart_js))
    display(Javascript(data=transcript_js))
    display(Javascript(data=wordpackchart_js))
    display(Javascript(data=wa_model_js))
    display(Javascript(data=wa_tree_js))
    display(Javascript(data=wa_node_details_js))
    display(Javascript(data=wa_dialog_chart_js))

def draw_flowchart(config, json_data, python_selection_var="selection", width=600, height=400):
    display(Javascript("""
        (function(element){
            require(['flowchart2'], function(flowchart2) {
                var config = %s;
                if (config["debugger"]===true){
                   debugger;
                };
                var chart = flowchart2(element.get(0), config, %s);

                chart.on("export",function(e){
                    var selection = JSON.stringify(e.selection).replace(/"/g , "'");
                    //var selection = JSON.stringify(e).replace(/"/g , "'");
                    IPython.notebook.kernel.execute("%s = " + selection);
                });
            });
        })(element);
    """ % (json.dumps(config), json.dumps(json_data), python_selection_var)))


def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (datetime.date, datetime.datetime)):
        return item_date_object.isoformat()

def draw_transcript(config, json_data, width=600, height=400):
    display(Javascript("""
        (function(element){
            require(['transcript'], function(transcript) {
                var config = %s;
                if (config["debugger"]===true){
                   debugger;
                };
                var chart = transcript(element.get(0), config, %s);
            });
        })(element);
    """ % (json.dumps(config), json.dumps(json_data, default=convert_timestamp))))
    
def draw_wordpackchart(config, json_data, width=600, height=400):
    display(Javascript("""
        (function(element){
            require(['wordpackchart'], function(wordpackchart) {
                var config = %s;
                var chart = wordpackchart(element.get(0), config, %s);
            });
        })(element);
    """ % (json.dumps(config), json.dumps(json_data, default=convert_timestamp))))

def draw_wa_dialog_chart(config, json_data, width=600, height=400):
    display(Javascript("""
        (function(element){
            require(['wa_dialog_chart'], function(wa_dialog_chart) {
                var config = %s;
                var chart = wa_dialog_chart(element.get(0), config, %s);
            });
        })(element);
    """ % (json.dumps(config), json.dumps(json_data))))