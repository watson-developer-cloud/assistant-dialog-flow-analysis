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

# The source code for this program is not published or otherwise divested of its trade secrets, irrespective of what has been depos-ited with the U.S. Copyright Office.
########################################################################
# Functions that process flows

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

########################################################################
def get_nodes_list(main_list):
    global descendant_list
    if type(main_list) == list:
        for i in main_list:
            if type(i) == str:
                descendant_list.append(i)
            else:
                get_nodes_list(i)
    elif type(main_list) == dict:
        for i in main_list:
            if type(main_list[i]) == str:
                descendant_list.append(i)
            else:
                descendant_list.append(i)
                get_nodes_list(main_list[i])

##########################################################################
def find_node_in_tree(node_name, main_list):
    global descendant_list
    for i in main_list:
        if i == node_name:
            descendant_list.append(i)
            if type(main_list) == dict:
                get_nodes_list(main_list[i])
            elif type(main_list) == list:
                get_nodes_list(i)
    else:
        if type(main_list) == list:
            for i in main_list:
                find_node_in_tree(node_name, i)
        elif type(main_list) == dict:
            for i in main_list:
                find_node_in_tree(node_name, main_list[i])

####################################################################
def get_descendants(nodes_tree, nodes_names, skill=None):
    
    global descendant_list
    descendant_list = []
    
    for node in nodes_names:
        if skill == "all":
            for i in nodes_tree:
                find_node_in_tree(node, nodes_tree[i])
        elif skill is not None:
            find_node_in_tree(node, nodes_tree[skill])
    return descendant_list

#############################################################################
def detect_flow_state(nodes, flows):

    if type(nodes) != list:
        return None

    processed_found=False
    for flow in flows:
        for node in nodes:
            if node in flow['completion_nodes']:
                return "completed"
            elif node in flow['nodes']:
                processed_found=True
        if processed_found:
            return "processed"
    
    return None

#############################################################################
def detect_flow(nodes, flows):
#give to it flow_defs['flows'] and node as list, for example ['node_xxxxxxxxx']
# return latest one
    if type(nodes) != list:
        return None
    
    for flow in flows:
        for node in nodes:
            if node in flow['nodes']:
                return flow['name']
    
    return None

###########################################################################################
# add internal flow content to initial definition
def enrich_flows_by_workspace(flow_defs, workspace, workspace_name="Some workspace"):

    workspace_edited={}
    workspace_edited[workspace_name]={}
    workspace_edited[workspace_name]["workspace_name"]=workspace["name"]
    workspace_edited[workspace_name]['indexed_dialog_nodes']={}

    for i in range(0,len(workspace["dialog_nodes"])):
        workspace_edited[workspace_name]['indexed_dialog_nodes'][workspace["dialog_nodes"][i]["dialog_node"]] =\
            workspace["dialog_nodes"][i]   
    
    tree_dict = {}
    for key in workspace_edited.keys():
        par = got_parent_nodes_for_skill(key, workspace_edited)  
        tree_dict[key] = create_nodes_tree(par, workspace_edited)
    
    for i in range (0, len(flow_defs["flows"])):        
        flow_defs["flows"][i]["nodes"] = get_descendants(tree_dict, flow_defs["flows"][i]["parent_nodes"], 'all')
    
    return flow_defs
    
#######################################################################################
# add two flow columns to canonical dataframe
def enrich_canonical_by_flows(df_all, flow_defs):
    df_all["flow"] = df_all.nodes_visited.map(lambda x: detect_flow(x, flow_defs["flows"]))
    df_all["flow_state"] = df_all.nodes_visited.map(lambda x: detect_flow_state(x, flow_defs["flows"]))
    
    return df_all

#######################################################################################
def got_parent_nodes_for_skill(skill,workspaces):
    nodes_parents = {}
    for i in workspaces[skill]['indexed_dialog_nodes']:
        if "parent" in workspaces[skill]['indexed_dialog_nodes'][i].keys():
            if workspaces[skill]['indexed_dialog_nodes'][i]['parent'] not in nodes_parents:
                nodes_parents[workspaces[skill]['indexed_dialog_nodes'][i]['parent']] = []
            nodes_parents[workspaces[skill]['indexed_dialog_nodes'][i]['parent']].append(workspaces[skill]['indexed_dialog_nodes'][i]['dialog_node'])
    return nodes_parents

def create_nodes_tree(parents_dict,workspaces):
    global delete_list
    delete_list = []
    new_dict = {}
    delete_list = []
    for i in parents_dict:
        values = parents_dict[i]
        #check if master
        new_values = check_if_master(values, parents_dict)
        new_dict[i] = new_values
    
    
    for z in set(delete_list):
        del new_dict[z]
        
    return new_dict

 
def check_if_master(values, parents_dict):
    new_values = []
    for i in values:
        if i in parents_dict:
            #it's master
            new_values.append({i : check_if_master(parents_dict[i], parents_dict)})
            global delete_list
            delete_list.append(i)
        else:
            #not a master
            new_values.append(i)
    return new_values
 

##########################################################################################################
 # compute flow statistics
def count_flows(df_logs, flow_defs): 
    
    df_logs = df_logs.sort_values(["conversation_id", "response_timestamp"]) 
    
    flow_outcome_summary={}
    flow_names=[]
    
    for i in range(0,len(flow_defs["flows"])):
        flow_names.append(flow_defs["flows"][i]["name"])
        flow_outcome_summary[flow_names[i]] = {}
        flow_outcome_summary[flow_names[i]]["completed"]=0
        flow_outcome_summary[flow_names[i]]["abandoned"]=0
        flow_outcome_summary[flow_names[i]]["rerouted"]=0
        #flow_outcome_summary[flow_names[i]]["escalated"]=0 
        
    num_flows=len(flow_names) 
    
    previous_conversation_id=""
    previous_flow_state=""
    previous_flow=""
    # state of each flow will be monitored
    current_conversation_flow_state = {}
    for i in range(0, num_flows):
        current_conversation_flow_state[flow_names[i]] = ""

    for i in range(0,len(df_logs)):
       
        current_conversation_id = df_logs.iloc[i,df_logs.columns.get_loc("conversation_id")]
        current_flow =  df_logs.iloc[i,df_logs.columns.get_loc("flow")]  
        current_flow_state =  df_logs.iloc[i,df_logs.columns.get_loc("flow_state")]  
        
              
        if current_conversation_id!=previous_conversation_id:
            # resetting states of all flows
            for j in range(0, num_flows):
                current_conversation_flow_state[flow_names[j]] = ""
        
            previous_conversation_id=current_conversation_id 
            new_session=True
        else:
            new_session=False
        
        if current_flow is not None:

            if current_flow_state=="processed":
                if current_conversation_flow_state[current_flow]=="" or new_session: # started now
                    current_conversation_flow_state[current_flow]="processed"
                    flow_outcome_summary[current_flow]["abandoned"]+=1  # abandonment is initial default
                elif current_conversation_flow_state[current_flow]=="rerouted": # return of digression
                    current_conversation_flow_state[current_flow]="processed"
                    flow_outcome_summary[current_flow]["abandoned"]+=1  # abandonment is initial default
                    flow_outcome_summary[current_flow]["rerouted"]-=1

            elif current_flow_state=="completed":        
                flow_outcome_summary[current_flow]["completed"]+=1
                if current_conversation_flow_state[current_flow]=="processed":
                    flow_outcome_summary[current_flow]["abandoned"]-=1
                elif current_conversation_flow_state[current_flow]=="rerouted":
                    flow_outcome_summary[current_flow]["rerouted"]-=1
                current_conversation_flow_state[current_flow]=""   
            
            else:
                print("Error! Wrong flow state.")
            
        # TODO: Check that dashboard code is fine
        if not new_session:
            if (previous_flow!=current_flow or current_flow is None) and previous_flow_state=="processed":
                flow_outcome_summary[previous_flow]["rerouted"]+=1
                current_conversation_flow_state[previous_flow]="rerouted"
                flow_outcome_summary[previous_flow]["abandoned"]-=1 
                                        
        previous_flow=current_flow      
        previous_flow_state=current_flow_state   
    
    # Temporarily we will not have escalated
             
    for key in flow_outcome_summary.keys():
        flow_outcome_summary[key]["overall"] = flow_outcome_summary[key]["completed"] +\
            flow_outcome_summary[key]["rerouted"] + flow_outcome_summary[key]["abandoned"]
            
    df=pd.DataFrame.from_dict(flow_outcome_summary, orient='index',
                       columns=['overall','completed', 'abandoned', 'rerouted'])

    df.index.name="flow name"

    df.reset_index(inplace=True)
        
    return df

################################################################################################
# flow chart for flow completion / abandonment / rerouting
def plot_flow_outcomes(df_flow_outcome_summary):
 
    flow_names =  df_flow_outcome_summary["flow name"].tolist()
    num_flows=len(flow_names)
    
    flow_outcome_summary = df_flow_outcome_summary.set_index('flow name').T.to_dict() 
    category_names=["Completed", "Rerouted", "Abandoned"]
    
    for key in flow_outcome_summary.keys():
        flow_outcome_summary[key]["overall"] = flow_outcome_summary[key]["completed"] +\
            flow_outcome_summary[key]["rerouted"] + flow_outcome_summary[key]["abandoned"]
    
    labels=[]
    for i in range(0, num_flows):
        labels.append(flow_names[i] + (" ("+str(flow_outcome_summary[flow_names[i]]["overall"])+")"))
        
    data = np.zeros([num_flows,3])    
    
    for i in range(0, num_flows):
        data[i,0] = (flow_outcome_summary[flow_names[i]]["completed"] / flow_outcome_summary[flow_names[i]]["overall"]) * 100.0
        data[i,1] = (flow_outcome_summary[flow_names[i]]["rerouted"] / flow_outcome_summary[flow_names[i]]["overall"]) * 100.0
        data[i,2] = (flow_outcome_summary[flow_names[i]]["abandoned"] / flow_outcome_summary[flow_names[i]]["overall"]) * 100.0
        
    data_cum = data.cumsum(axis=1)

    alpha = 0.7
    category_colors = [(0.102, 0.596, 0.314,alpha),(0.878, 0.878, 0.878, alpha),(0.843, 0.188, 0.152, alpha)]
    fig, ax = plt.subplots(figsize=(12, 2))
    ax.invert_yaxis()
    #ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())
    
    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        
        ax.barh(labels, widths, left=starts, height=0.8,
                label=colname, color=color)
        xcenters = starts + widths / 2
 
        text_color = 'black'
        for y, (x, c) in enumerate(zip(xcenters, widths)):
            ax.text(x, y, str(int(c))+ "%", ha='center', va='center',
                    color=text_color, fontsize='large')
    
    ax.set_xlabel("Percentage", fontsize="large")
    ax.set_yticklabels(labels, fontsize="large")
     
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='large')
    
    return
    