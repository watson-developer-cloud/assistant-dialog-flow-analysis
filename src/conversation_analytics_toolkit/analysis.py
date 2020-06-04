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

from collections import defaultdict
import pandas as pd
import numpy as np
import json
import conversation_analytics_toolkit as cat
from pandas.io.json import json_normalize

class _conversationPathAnalysis:
    def __init__(self, mode, on_column, max_depth, trim_reroutes):
        self.mode = mode
        self.on_column = on_column
        self.max_depth = max_depth
        self.trim_reroutes = trim_reroutes
        self.nodes_paths = defaultdict(list)

    def handle_node_row(self, path, row, step, is_conversation_start, path_length):
        if not path in self.nodes_paths:
            self.nodes_paths[path] = {"flows":0, "rerouted":0, "dropped_off":0, "type": "NODE", "name": row[self.on_column],"is_conversation_start": is_conversation_start, "conversation_log_ids_dropped_off":[], "conversation_log_ids_rerouted":[],"path_length": path_length}
        self.nodes_paths[path]["flows"] += 1
        #if (row.response_branch_exited==True and row.response_branch_exited_reason=='fallback' and row.digression is not True):
        if self.trim_reroutes == True:
            if (row.branch_exited==True and row.branch_exited_reason=='fallback' and row.digression is False):
                self.nodes_paths[path]["rerouted"] += 1
                self.nodes_paths[path]["conversation_log_ids_rerouted"].append((row.conversation_id, row.log_id))
                return 'rerouted'

    def handle_conversation_node_exit(self, path, step, row):
        self.nodes_paths[path]["dropped_off"] += 1
        self.nodes_paths[path]["conversation_log_ids_dropped_off"].append((row.conversation_id, row.log_id))

    def handle_conversation_path(self, df):
        # if data doesn't include digression, add it for downstream dependency.
        if 'digression' not in df.columns:
            df["digression"] = False

        prev_node_path = ""
        prev_row = ""
        delimiter = "\\"
        for i, (index, row) in enumerate(df.iterrows()):
            node_code = row[self.on_column]
            node_id = str(node_code)
            if i==0:
                curr_node_path = node_id
                path_length = 0
                if self.handle_node_row(curr_node_path, row, i, True, path_length) == 'rerouted':
                    # note this will never happen if trim_reroutes=False
                    break
            else:
                curr_node_path = prev_node_path + delimiter + node_id
                path_length += 1
                if (i <= self.max_depth):
                    if self.handle_node_row(curr_node_path, row, i, True, path_length) == 'rerouted':
                        # note this will never happen if trim_reroutes=False
                        break
                else:
                    print("reached depth limit of " + str(i-1) + ", ignoring steps beyond.  You can set max_depth to a larger number")
                    self.handle_conversation_node_exit(prev_node_path, i-1, row)
                    break
            prev_node_path = curr_node_path
            prev_row = row
            if i == len(df) - 1:
                self.handle_conversation_node_exit(curr_node_path, i, row)

class DialogNodesGraph(): 
    # compute visits in dialog nodes
    def __init__(self, workspace, description=""):
        self.steps = None
        df_workspace = json_normalize(workspace)
        # dataframe representation of the workspace
        self.dialog_nodes = df_workspace['dialog_nodes'].values[0]
        # compute map from node to its index in the dialog_nodes_array
        self.dialog_node_index = {}
        for i, element in enumerate(self.dialog_nodes):
            node_id = element["dialog_node"]
            self.dialog_node_index[node_id] = i
        self.description = ""
        # count visits of nodes_visited in each node, prev, and next
        self.nodes_visited_graph = {}
        # map of conversations and their steps
        self.conversation_steps = {}

    def _get_node(self, node_id):
        return self.dialog_nodes[self.dialog_node_index[node_id]]

    def _add_conversation_visits_to_graph(self, nodes_visited):
        for i, node in enumerate(nodes_visited):
            graph = self.nodes_visited_graph
            # add node if not exist
            if node not in graph:
                graph[node] = {'visits': 0, 'prev': {}, 'next': {}}
            # add count to current node
            graph[node]['visits'] += 1
            # add next to every node except last
            if i < len(nodes_visited) - 1:
                next_node = nodes_visited[i+1]
                if next_node not in graph[node]['next']:
                    graph[node]['next'][next_node] = {'visits': 0}
                graph[node]['next'][next_node]['visits']+=1
            # add prev to every node except first
            if i > 0:
                prev_node = nodes_visited[i-1]
                if prev_node not in graph[node]['prev']:
                    graph[node]['prev'][prev_node] = {'visits': 0}
                graph[node]['prev'][prev_node]['visits']+=1
    
    def _slider_update(self, slider, step, step_desc, step_message = None):
        width = 90
        prefix = ""
        long_message = prefix + step_desc + '.' * (width - len(step_desc) - len(prefix))
        slider.update(step)
        if step_message is not None:
            slider.write(step_message)
        slider.set_description(long_message)

    def compute_visits(self, logs):
        if not type(self.steps) == pd.core.frame.DataFrame:
            self.steps = logs
        else:
            self.steps = self.steps.append(logs)
        conversations_grouped =  logs.groupby("conversation_id")
        from tqdm import tqdm, tqdm_notebook
        if cat.use_widgets():
            slider = tqdm_notebook(range(100), desc="processing {} conversations".format(len(conversations_grouped)), ncols=900)
        else:
            slider = tqdm(range(100), desc="processing {} conversations".format(len(conversations_grouped)), ncols=90)
        i=0
        for conversation, steps_df in conversations_grouped:
            i +=1
            if i/100 == int(i/100): # every 100 conversations update the slider
                step = int(100/len(conversations_grouped)*100)
                self._slider_update(slider, step, "Processed {} of {} conversations".format(i, len(conversations_grouped)))
            nodes_visited_in_conversation = []
            steps_df = steps_df.sort_values(["response_timestamp"])
            for index, row in steps_df.iterrows():
                nodes_visited_in_conversation.extend(row["nodes_visited"]) 
            self.conversation_steps[conversation] = nodes_visited_in_conversation
            self._add_conversation_visits_to_graph(nodes_visited_in_conversation)
        self._slider_update(slider, 100, "Processed {} conversations".format(i))

    def get_conversation_steps(self, conversation_id):
        return self.conversation_steps[conversation_id]

    def was_node_visited(self, node_id):
        return True if node_id in self.nodes_visited_graph else False

    def get_nodes_visited(self, node_id):
        return self.nodes_visited_graph[node_id]

    def get_node(self, node_id):
        return self._get_node(node_id)

    def get_node_label(self, node, show_type = True, show_id_if_title_exist = True, show_visits = True):
        node_type = node["type"] if show_type == True else ""
        node_title = node["title"] if "title" in node else ""
        node_id = node["dialog_node"]
        if self.was_node_visited(node_id):
            node_visits = self.get_nodes_visited(node_id)["visits"]
        else: 
            node_visits = 0
        node_label = ""
        if show_type:
            node_label = "[{}]".format(node_type)
        if not show_id_if_title_exist and node_title != "":
            node_label = node_label + " " + node_title
        else: 
            node_label = node_label + " " + node_title + " : " + node_id
        if show_visits == True:
            node_label = node_label + " [ {} ]".format(node_visits)
        return node_label

    def info(self):
        return {
            'converstions': len(self.conversation_steps.keys()),
            'steps': len(self.steps),
            'nodes': len(self.nodes_visited_graph.keys())
        }

    def flows_to_from_node_sankey(self, node_id, arrangement="freeform", orientation='h', pad=10, hovermode='x'):
        import plotly.graph_objects as go 
        current_node_index = self.dialog_node_index[node_id]
        nodes_label = [self.get_node_label(n) for n in self.dialog_nodes]
        sankey_nodes = { "label": nodes_label, "pad": 10}
        #get links for the given node from the graph
        node_graph = self.get_nodes_visited(node_id)
        sankey_links = {"source": [], "target": [], "value": []}
        #iterate on prev
        for prev_node, prev_value in node_graph["prev"].items():
            sankey_links["source"].append(self.dialog_node_index[prev_node])
            sankey_links["target"].append(current_node_index)
            sankey_links["value"].append(prev_value["visits"])
        for next_node, next_value in node_graph["next"].items():
            sankey_links["source"].append(current_node_index)
            sankey_links["target"].append(self.dialog_node_index[next_node])
            sankey_links["value"].append(next_value["visits"])
        
        fig = go.Figure(go.Sankey(
            valuesuffix = " visits",
            orientation = orientation,
            arrangement = arrangement,
            node = {
                "label": sankey_nodes["label"],
                'pad':pad},
            link = {
                "source": sankey_links["source"],

                "target": sankey_links["target"],
                "value": sankey_links["value"]}))
        fig.update_layout(title_text="Nodes visited for node: " + node_id , font_size=10, hovermode = hovermode)
        fig.show()
        return 

    def flows_to_from_node_html(self, node_id):
        node_graph = self.get_nodes_visited(node_id)
        prev_list = []
        for prev_node, prev_value in node_graph["prev"].items():
            prev_list.append({"prev_node": prev_node, "type": self.get_node(node_id)["type"], "visits": prev_value["visits"]})
        prev_df = pd.DataFrame(prev_list)
        next_list = []
        for next_node, next_value in node_graph["next"].items():
            next_list.append({"next_node": next_node, "type": self.get_node(node_id)["type"], "visits": next_value["visits"]})
        next_df = pd.DataFrame(next_list)
        from IPython.display import display, HTML
        display(HTML(prev_df.to_html()))
        display(HTML(next_df.to_html()))

class MilestoneFlowGraph: 
    # data structures
    # { milestones: m1 --> {}}
    # { funnels: funnels --> [m1, m2]} 
    # { mappings: node --> milestone}
    # compute visits in dialog nodes
    def __init__(self, workspace):
        #map of milestones
        self.milestones = {}
        #map of funnels, initialized default
        self.funnels = {
            "default": []
        }
        #nodes mapping to milestones
        self.nodes  = {}
        df_workspace = json_normalize(workspace)
        self.dialog_nodes = df_workspace['dialog_nodes'].values[0]
        # compute map from node to its index in the dialog_nodes_array
        self.dialog_node_index = {}
        for i, element in enumerate(self.dialog_nodes):
            node_id = element["dialog_node"]
            self.dialog_node_index[node_id] = i

    def add_milestones(self, names, funnel="default", atIndex=None):
        # add milestone, warn if already exists
        if atIndex==None:
            atIndex = len(self.funnels[funnel])
        for name in names:
            self.add_milestone(name, funnel, atIndex)            
            atIndex+=1
        return

    def add_milestone(self, name, funnel="default", atIndex=None):
        # add milestone, warn if already exists
        if name in self.milestones:
            print("warning: milestone '{}' is already defined".format(name))
        if atIndex==None:
            atIndex = len(self.funnels[funnel])
        self.funnels[funnel].insert(atIndex, name)
        self.milestones[name] = name
        return

    def add_node_to_milestone(self, dialog_node_id, milestone):
        # validate that node exists and milestone exists, warn if previous mapping exists
        if not dialog_node_id in self.dialog_node_index:
            print("Warning: dialog node '{}' does not exist in workspace".format(dialog_node_id))
        if not milestone in self.milestones:
            print("Error: milestone is not defined.  Use add_milestone() to add milestones")
            return
        if dialog_node_id in self.nodes:
            print("Warning: dialog node '{}' is already defined for milestone '{}', overriding...".format(dialog_node_id,self.nodes[dialog_node_id]))
        self.nodes[dialog_node_id] = milestone  

    def get_funnel(self, funnel="default"):
        if funnel not in self.funnels.keys():
            print("Error: funnel '{}' is not defined.".format(funnel))
            return
        return self.funnels[funnel]

    def get_milestone_in_nodes_visited(self, nodes):
        result = None
        for node in nodes:
            if node in self.nodes.keys():
                result = self.nodes[node]
                break
        return result      

    def enrich_milestones(self, df_logs):
        # take original data, for every nodes_visited, check if one has milestone def, enrich milestone
        # add column: milestone, funnels, 
        df_logs['milestone'] = None
        conversations_grouped =  df_logs.groupby("conversation_id")
        from tqdm import tqdm, tqdm_notebook
        if cat.use_widgets():
            slider = tqdm_notebook(range(100), desc="processing {} conversations".format(len(conversations_grouped)), ncols=900)
        else:
            slider = tqdm(range(100), desc="processing {} conversations".format(len(conversations_grouped)), ncols=900)
        i=0
        #for each conversation 
        for conversation, steps_df in conversations_grouped:
            i +=1
            if i/100 == int(i/100): # every 100 conversations update the slider
                step = int(100/len(conversations_grouped)*100)
                self._slider_update(slider, step, "Processed {} of {} conversations".format(i, len(conversations_grouped)))                  
            #nodes_visited_in_conversation = []
            steps_df= steps_df.sort_values(["response_timestamp"])
            last_index = None
            #for each conversation step, update the milestone in the original data
            for index, row in steps_df.iterrows():
                last_index = index
                nodes_visited = row["nodes_visited"]
                milestone = self.get_milestone_in_nodes_visited(nodes_visited)
                if milestone != None:
                    df_logs.at[index, "milestone"] = milestone   
            # if last step is not a milestone, add the Other node
            if df_logs.loc[last_index]['milestone'] == None:
                df_logs.at[index, "milestone"] = 'Other'
                #df_logs.loc[last_index]['milestone'] = 'Other'
        self._slider_update(slider, 100, "Processed {} conversations".format(i))
                          
    def _slider_update(self, slider, step, step_desc, step_message = None):
        width = 90
        prefix = ""
        long_message = prefix + step_desc + '.' * (width - len(step_desc) - len(prefix))
        slider.update(step)
        if step_message is not None:
            slider.write(step_message)
        slider.set_description(long_message)
        

def compute_flows(df, config):
    """
    DEPRECATED: compute aggregated flows across nodes and corresponding statistics, such as number of dropoffs
    returns results as a df for visualization
    """
    print("Error. compute_flows is deprecated.  Use aggregate_flows instead")
    return
    # check optional config attributes
    if "max_path_limit" not in config:
        print ("Warning, max_path_limit is missing from config.  Default 20 is assumed")
        config["max_path_limit"] = 20

    # check mandatory dataframe fields
    # TODO: check additional mandatory fields , eg log_id
    mandatory_columns = ['conversation_id', 'node_visited', 'response_timestamp']
    for column in mandatory_columns:
        if column not in df.columns.values:
            raise Exception("input data is missing mandatory column: " + column)

    analysis = _conversationPathAnalysis(config)
    for idx, conversation_df in df.groupby(df['conversation_id']):
        conversation_df = conversation_df.sort_values("response_timestamp")
        analysis.handle_conversation_path(conversation_df)

    df_node_out = pd.DataFrame.from_dict(analysis.nodes_paths, orient="index")
    df_node_out.reset_index(inplace=True)
    df_node_out.rename(columns={'index':'path'}, inplace=True)

    return pd.concat([df_node_out])[['path','name','type','is_conversation_start','flows','rerouted','dropped_off','conversation_log_ids_rerouted','conversation_log_ids_dropped_off','path_length']]

def aggregate_flows(df, max_depth=30, mode="turn-based", on_column="turn_label", trim_reroutes=False ):
    """
    compute aggregated flows across nodes and corresponding statistics, such as number of dropoffs
    returns results as a df for visualization
    """
    if mode not in ["turn-based", "milestone-based"]:
        print("invalid mode: {}.  Valid values are either turn-based or milestone-based".format(mode))
        return
    if on_column not in df.columns:
        print("invalid column name: {} does not exist in dataframe".format(column))
        return

    # check mandatory dataframe fields
    # TODO: check additional mandatory fields , eg log_id
    mandatory_columns = ['log_id', 'conversation_id', 'response_timestamp']
    for column in mandatory_columns:
        if column not in df.columns.values:
            raise Exception("input data is missing mandatory column: " + column)

    analysis = _conversationPathAnalysis(mode, on_column, max_depth, trim_reroutes)
    for idx, conversation_df in df.groupby(df['conversation_id']):
        conversation_df = conversation_df.sort_values("response_timestamp")
        analysis.handle_conversation_path(conversation_df)

    df_node_out = pd.DataFrame.from_dict(analysis.nodes_paths, orient="index")
    df_node_out.reset_index(inplace=True)
    df_node_out.rename(columns={'index':'path'}, inplace=True)

    return pd.concat([df_node_out])[['path','name','type','is_conversation_start','flows','rerouted','dropped_off','conversation_log_ids_rerouted','conversation_log_ids_dropped_off','path_length']]
 
def _find_consecutive_flow_states(df, column="milestone"):
    log_ids_to_delete = []
    for idx, conversation_df in df.groupby(df['conversation_id']):
        conversation_df = conversation_df.sort_values("response_timestamp")
        #for each conversation, remove duplicate milestones
        last_milestone = None
        for index, row in conversation_df.iterrows():
            if row[column] != last_milestone:
                last_milestone = row[column]
            else:
                log_ids_to_delete.append(row['log_id'])
    return log_ids_to_delete

def simplify_flow_consecutive_milestones(df):
    """
    remove consecutive milestones from the dataframe, to create a simplified flow visualization.
    """

    rows_to_delete = _find_consecutive_flow_states(df)
    print("Removed {} duplicate milestone rows".format(str(len(rows_to_delete))))
    result = df[~df["log_id"].isin(rows_to_delete)]
    return result