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


import pandas as pd
import numpy as np
import decimal
import datetime
import re
import time, sys
from .wa_assistant_skills import DialogNodeNotFound

def ipython_info():
    ip = False
    if 'ipykernel' in sys.modules:
        ip = 'notebook'
    elif 'IPython' in sys.modules:
        ip = 'terminal'
    return ip

if ipython_info() == 'notebook':
    from IPython.display import clear_output


# TODO: the code supose to find last n
def extract_node_from_nodes_visited(nodes_visited, nodes_dict):
    num_nodes=len(nodes_visited)
    # last node is selected by default
    node_visited = nodes_visited[-1]
    for i in range(num_nodes-1, -1, -1):
        current_name = nodes_dict[nodes_visited[i]]
        if type(current_name) == str:
            if not current_name.startswith("node_1"): 
                # if we found another node with a "better" name
                node_visited = nodes_visited[i]
                break
        
    return node_visited
    

def to_canonical_WA(df, nodes_dict):
    """
    transform WA log format into pathflow dataframe canonical data model
    returns a canonical dataframe with the following mandatory columns
    'log_id'
    'conversation_id'
    'node_visited'
    'response_timestamp'
    'branch_exited'
    'branch_exited_reason'
    'intent'
    the following fields are optional:
    'response_type'
    'request_text'
    'response_text'
    """
    print("to_canonical_WA is deprecated and will be removed in a future release. Use to_canonical_WA_v2 instead")
    if df.empty:
        return df
    else:
        df1 = pd.concat([df.drop(['request', 'response'], axis=1).reset_index(drop=True),
                     df['request'].apply(pd.Series).add_prefix('request_').reset_index(drop=True),
                     pd.DataFrame(df['response']
                                  .tolist()).add_prefix('response_')], axis=1)
        df1['request_input'] = pd.io.json.json_normalize(df['request'])['input.text']
        df2 = pd.concat([df1.drop(['response_context', 'response_output'], axis=1), df1['response_context'].apply(pd.Series).add_prefix('response_context_'), pd.DataFrame(df1['response_output'].tolist()).add_prefix('response_output_')], axis=1)
        df3 = pd.concat([df2.drop(['response_context_system'], axis=1), df2['response_context_system'].apply(pd.Series).add_prefix('response_context_system_')], axis=1)

        if 'response_output_generic' in df3:
            df4 = pd.concat([df3.drop(['response_output_generic'], axis=1), df3['response_output_generic'].apply(pd.Series).add_prefix('response_output_generic_')], axis=1)
        else:
            df4 = df3

        cols = ['response_context_conversation_id', 'log_id' ,'response_timestamp', 
                'request_input', 'response_output_text' ,'response_output_nodes_visited', 
                'response_context_system_branch_exited', 'response_context_system_branch_exited_reason','response_intents'
                #,'response_output_generic_response_type']
                ]
        df5 = df4[cols].copy(deep=True)
        df5.rename(columns={'response_output_nodes_visited': 'nodes_visited',
                        'response_context_conversation_id': 'conversation_id',
                        'request_input' : 'request_text',
                        'response_output_text': 'response_text',
                        'response_context_system_branch_exited' : 'branch_exited',
                        'response_context_system_branch_exited_reason' : 'branch_exited_reason',
                        'response_intents' : 'intent'
                        #response_output_generic_response_type' : 'type'
                       }, inplace=True)
        # in the regular to_canonical, we always take the last node regardless if it's standard
        # TODO: consider only standard nodes
        #df5['node_visited']=df5['nodes_visited'].apply(lambda x:x[-1])
        
        # This string searches from the end for node with meaningful name
        df5['node_visited']=df5['nodes_visited'].apply(lambda x: extract_node_from_nodes_visited(x,nodes_dict)) 
        df5['response_timestamp'] = pd.to_datetime(df5['response_timestamp'])
        # TODO: check what happens for multiple and zero intents and reference by name
        df5['intent'] = df5['intent'].apply(lambda x:x[0]['intent'] if x else x)
        df5['node_visited'] = df5['node_visited'].replace(nodes_dict)
        return df5

def get_title_or_condition_or_id(node):
    if 'title' in node:
        return node["title"]
    elif 'conditions' in node:
        return node["conditions"]
    else: 
        return node["dialog_node"]

def extract_best_label(node, include_type=True):
    """
    Best label is defined based on node type as follows:
    response_condition: condition[RC]
    standard: title or condition[SN]
    frame: title[FR]
    event_handler: condition[EH]
    slot: variable[SL]
    folder: title[FOL]
    """
    def format(node_str, node_type):
        if not include_type:
            return node_str
        else:
            return node_str + "[" + node_type + "]"
    
    def get_event_handler_condition_or_type(node):
        if 'conditions' in node:
            return node["conditions"]
        else:
            return "[" + node["event_name"] + "]"

    try:
        if node["type"] == "response_condition":
            return format(get_title_or_condition_or_id(node), "RC")
        elif node["type"] == "standard":
            return format(get_title_or_condition_or_id(node), "SN")
        elif node["type"] == "folder":
            return format(node["title"], "FOL")
        elif node["type"] == "frame":
            return format(node["title"], "FR")
        elif node["type"] == "event_handler":
            return format(get_event_handler_condition_or_type(node), "EH")
        elif node["type"] == "slot":
            return format(node["variable"], "SL")
        else:
            return "?"
    except Exception as e:
        print("node label could not be resolved for ", e)
        return "?" 

def node_visited_to_str(row, wa_skills, include_node_visited_to_str):
    """
    returns a string representation of nodes_visited
    """
    results = []
    for node_id in row['nodes_visited']:
        try:
            node = wa_skills.get_node_by_id(row['skill_id'], node_id)
            results.append(extract_best_label(node, include_node_visited_to_str))
        except:
            results.append("?")
    return results

def extract_turn_label(row, wa_skills, errors, mode="last_standard", match_from_any_skill=False):
    """
    returns a string representation the most significant information in the turn
    mode="last_standard" will seek for the last standard node, and try to extract a meaningful name from it
    """
    #initialize with last node_id
    result=row['nodes_visited'][-1]
    for node_id in reversed(row['nodes_visited']):
        try:
            if match_from_any_skill == False:
                node = wa_skills.get_node_by_id(row['skill_id'], node_id)
            else:
                node = wa_skills.get_node_by_id_any_skill(node_id)
            if node["type"] == "standard":
                result = get_title_or_condition_or_id(node)
                if "title" in node:
                    #if we found a standard node with title we're done.  
                    break
                elif "conditions" in node:
                    if node["conditions"] != 'true':
                        #if we found a condition, check that it isn't true  If not keep on seeking for better name
                        break
            if node["type"] == "frame" or node["type"] == "folder":
                if "title" in node:
                    #if we find a frame or folder with a title, then we're done
                    result = node["title"]
                    break
        except KeyError as e:
            errors["skills_not_found"].add(e.args[0])
            errors["nodes_not_found"].add(node_id)
            #print("turn label could not be resolved for ", e.args[0], ":", node_id)
            result = "?"
            break
    return result

def is_intent_triggered(row, wa_skills, errors, match_from_any_skill=False):
    result = ''
    intent = row["intent_1"]

    for node_id in row['nodes_visited']:
        try:
            if intent == "":
                continue
            # TBD if strict, try to search in skill, if not strict, try to first search the skill, if failed, any skill
            # search in all skills
            #  is single skill, we could search in all skills, via get_node_by_id_anyskill
            if match_from_any_skill == False:
                node = wa_skills.get_node_by_id(row['skill_id'], node_id)
            else:
                node = wa_skills.get_node_by_id_any_skill(node_id)
            if "conditions" in node:
                if intent in node["conditions"]:
                    result = intent
                    break
        except KeyError as e:
            errors["skills_not_found"].add(e.args[0])
            errors["nodes_not_found"].add(node_id)
            #print("is_intent_triggered could not be resolved", e, ":", node_id)
            break
    return result

def to_canonical_WA_v2(df, wa_skills=None, skill_id_field=None, include_nodes_visited_str_types=False):
    """
    Transform WA log format into pathflow dataframe canonical data model

    Parameters:
    df (DataFrame): WA logs
    wa_skills (WA_Assistant_Skills)
    skill_id_field (str): the name of the column in the logs files to use to match with the skill.  If None, then the match will be done against all skills
    include_nodes_visited_str_types: include node type information in the ndoes_visited_str column

    Returns:
    Dataframe with the following mandatory columns
    'conversation_id', 'log_id', 'response_timestamp', 'request_text',
    'response_text', 'nodes_visited', 'branch_exited',
    'branch_exited_reason', 'skill_id', 'intent_1', 'intent_1_confidence',
    'event_type', 'intent_1_dialog_triggered', 'skill_name',
    'nodes_visited_str', 'turn_label'
    """

    # if wa_skills = None, only basic extraction will be performed, no enrichment will be performed
    # for turn_label or nodes_visited_str

    # if wa_skills is provided, the skill_id_field should define which field to match against.
    #  point to the skill_id_fieldno enrichments will b
    
    # if skill_id_field = None, assume single skill mode, and use get_node_by_id_anyskill(node_id) or find_first_skill_id_for_node to match


    should_enrich = True
    # validation
    if df.empty:
        print("Warning: empty dataframe, no logs to transform")
        return df
    if wa_skills == None or wa_skills.__class__.__name__ != 'WA_Assistant_Skills':
        print("Warning: WA assistant skill object not provided. Only basic transformation will be performed")
        should_enrich = False
    #TODO: 
    #if should_enrich == True and skill_id_field not in df.columns:
    #    print("Error: logs do not contain WA assistant skill object not provided.

    # CODE BELOW IMPROVES PERFORMANCE
    
    #expand the request and response objects into additional columns
    df1 = pd.concat([df.drop(['request', 'response'], axis=1).reset_index(drop=True),
            pd.DataFrame(df['request'].tolist()).add_prefix('request_'),
            pd.DataFrame(df['response'].tolist()).add_prefix('response_')], axis=1)
    #parse request_input
    df1['request_input'] = pd.io.json.json_normalize(df['request'])['input.text']
    
    #expand the request_context and response_output into additional columns
    df2 = pd.concat([df1.drop(['response_context', 'response_output'], axis=1), 
        pd.DataFrame(df1['response_context'].tolist()).add_prefix('response_context_'), 
        pd.DataFrame(df1['response_output'].tolist()).add_prefix('response_output_')], axis=1)

    #expand system_context columns (include fields e.g. the output text)
    df3 = pd.concat([df2.drop(['response_context_system'], axis=1), 
        pd.DataFrame(df2['response_context_system'].tolist()).add_prefix('response_context_system_')], axis=1)

    #expand response output generic columns (include fields e.g. the output text)  
    if 'response_output_generic' in df3:
        df4 = pd.concat([df3.drop(['response_output_generic'], axis=1), 
        pd.DataFrame(df3['response_output_generic'].tolist()).add_prefix('response_output_generic_')], axis=1)
    else:
        df4 = df3
    #TODO: consider to extract response_output_action too

    if skill_id_field != None:
        cols = ['response_context_conversation_id', 'log_id' ,'response_timestamp', 
        'request_input', 'response_output_text' ,'response_output_nodes_visited', 
        'response_context_system_branch_exited', 'response_context_system_branch_exited_reason',
        'response_intents',skill_id_field]
        #'response_output_generic_response_type']
    else: 
        cols = ['response_context_conversation_id', 'log_id' ,'response_timestamp', 
        'request_input', 'response_output_text' ,'response_output_nodes_visited', 
        'response_context_system_branch_exited', 'response_context_system_branch_exited_reason',
        'response_intents',"workspace_id"]
        #'response_output_generic_response_type']

    #if in_place == True:
    #    df5 = df4[cols]
    #else:
    df5 = df4[cols].copy(deep=True)
    
    if skill_id_field != None:
        df5.rename(columns={'response_output_nodes_visited': 'nodes_visited',
                        'response_context_conversation_id': 'conversation_id',
                        'request_input' : 'request_text',
                        'response_output_text': 'response_text',
                        'response_context_system_branch_exited' : 'branch_exited',
                        'response_context_system_branch_exited_reason' : 'branch_exited_reason',
                        'response_intents' : 'intent',
                        skill_id_field : 'skill_id'
                        #response_output_generic_response_type' : 'type'
                        }, inplace=True)
    else:
        df5.rename(columns={'response_output_nodes_visited': 'nodes_visited',
                        'response_context_conversation_id': 'conversation_id',
                        'request_input' : 'request_text',
                        'response_output_text': 'response_text',
                        'response_context_system_branch_exited' : 'branch_exited',
                        'response_context_system_branch_exited_reason' : 'branch_exited_reason',
                        'response_intents' : 'intent',
                        "workspace_id" : 'skill_id'
                        #response_output_generic_response_type' : 'type'
                        }, inplace=True)
    
    df5['response_timestamp'] = pd.to_datetime(df5['response_timestamp'])
    # TODO: check what happens for multiple and zero intents and reference by name
    df5['intent_1'] = df5['intent'].apply(lambda x:x[0]['intent'] if x else '')
    df5['intent_1_confidence'] = df5['intent'].apply(lambda x:x[0]['confidence'] if x else '')
    df5['event_type'] = "REQUEST_REPONSE"
    #df5['skill_id'] = pd.DataFrame(df[skill_id_field].to_list())
    
    errors = {
        "skills_not_found": set(),
        "nodes_not_found": set()
    }

    if should_enrich:
        if skill_id_field == None:
            df5['intent_1_dialog_triggered'] = df5.apply(lambda row: is_intent_triggered(row, wa_skills, errors, match_from_any_skill=True), axis=1)
        else:
            df5['intent_1_dialog_triggered'] = df5.apply(lambda row: is_intent_triggered(row, wa_skills, errors, match_from_any_skill=False), axis=1)
        
        if skill_id_field == None:
            df5['skill_name'] = df5['skill_id'].apply(lambda x: wa_skills.get_skill_name_by_id(x, False))
        else:
            try: 
                df5['skill_name'] = df5['skill_id'].apply(lambda x: wa_skills.get_skill_by_id(x)["name"])
            except KeyError as e:
                print("The skill_id: {} appears in the logs, but there is no corresponding skill_id in WA_Assistant_Skills object\n".format(str(e)))
                print("You should either add the missing skill, or set skill_id_field=None to try to match globally by node_ids that are part of WA_Assistant_Skill regatdless of the skill_id")
                raise e
        df5['nodes_visited_str']=df5.apply(lambda row: node_visited_to_str(row, wa_skills, include_nodes_visited_str_types), axis=1)
        
        if skill_id_field == None:
            df5['turn_label']=df5.apply(lambda row: extract_turn_label(row, wa_skills, errors, match_from_any_skill=True), axis=1)
        else:
            df5['turn_label']=df5.apply(lambda row: extract_turn_label(row, wa_skills, errors, match_from_any_skill=False), axis=1)
    df5.drop(['intent'], axis=1, inplace=True)
    if len(errors["skills_not_found"]) >0 or len(errors["nodes_not_found"]) > 0:
        print("Warning, transformation completed, but some values in the logs were not found in the corresponding WA_Assistant_Skills object:")
        print("skills not found: ", errors["skills_not_found"] )
        print("nodes not found: ", errors["nodes_not_found"] )

    return df5

def progress_bar(progress):
    bar_length = 30
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
    if progress < 0:
        progress = 0
    if progress >= 1:
        progress = 1
    block = int(round(bar_length * progress))
    if ipython_info() == 'notebook':
        clear_output(wait = True)
    text = "Progress: [{0}] {1:.1f}%".format( "#" * block + "-" * (bar_length - block), progress * 100)
    print(text)

def _to_canonical(df, nodes_dict):
    """
    The function does the following:
    1. manipulate the values in nodes_visted to not include brackets [] and apostrophes '' resulting in comma seperated list of dialog_node values
    2. Iterates over the nodes_visited array
    """
    if df.empty:
        return df
    else:
        cols = ['document_id', 'response_timestamp', 'conversation_id',
       'request_input', 'response_text', 'nodes_visited', 'response_intent',
       'branch_exited','branch_exited_reason', 'digression'] #,'node_visited'
        df_results = df[cols].copy(deep=True)

        import ast
        #transform string representation of nodes_visited into a list of nodes (array).  Note we're not using json.loads since
        #the data contains single quoted strings, so not valid json
        df_results['nodes_visited']=df_results['nodes_visited'].apply(lambda x:ast.literal_eval(x))
        df_results['node_visited']=df_results['nodes_visited']   
        for idx, element in enumerate(df_results['node_visited']):
            # extract a list of nodes_name (node_title) and list of node_types
            # if the node is not found in the dictionary (either bug, or wrong json workspace) then use the dialog_node
            # nodes_dict is a map between node_id --> (node_name, node_type)
            nodes_name = list(map(lambda x: nodes_dict[x][0] if x in nodes_dict else x, element))
            nodes_type = list(map(lambda x: nodes_dict[x][1] if x in nodes_dict else x, element))
        
            # if we have ["Login Issues", "node_12_lhagsdkljhsdlkg"]
            # the indcice_standard would produce [0]
            indice_standard = [i for i, y in enumerate(nodes_type) if y == "standard"]
            # check how many value are there in nodes_visited
            # special case, if last standard node (index -2) is Handoff or More Help - TBD double check with Erica
            # if we have  ["More Help", "Login Issues"], then select More Help
            if len (nodes_name)>2 and (nodes_name[-2]=='Handoff' or nodes_name[-2]=='More Help'):
                df_results.loc[idx, 'node_visited'] = nodes_name[-2]
            elif len (indice_standard) > 0:  # take the last standard node
                df_results.loc[idx, 'node_visited'] = nodes_name[indice_standard[-1]]  ## logs will compare ids to the title
            else:
                df_results.loc[idx, 'node_visited'] = nodes_name[-1]
        df_results.rename(columns={
                        'document_id': 'log_id',
                        'response_intent' : 'intent',
                        'request_input' : 'request_text'
                       }, inplace=True)
        df_results.rename(columns={'document_id': 'log_id'}, inplace=True)
        return df_results


# import re
# def _to_canonical(df, nodes_dict):
#     """
#     The function does the following:
#     1. manipulate the values in nodes_visted to not include brackets [] and apostrophes '' resulting in comma seperated list of dialog_node values
#     2. Iterates over the nodes_visited array
#     """

#     if df.empty:
#         return df
#     else:
#         # remove special characters.but the space could be a bug
#         # however in this example, ["Login Issues", "node_12_lhagsdkljhsdlkg"]
#         # the algorithm would remove the space
#         # ["LoginIssues", "node_12_lhagsdkljhsdlkg"] which is an issue since
#         # nodes_name includes the key "Login Issues"
#         #sym_list = str.maketrans("", "", "'[]' ")
#         sym_list = str.maketrans("", "", "'[]")
#         df['node_visited']=[x.translate(sym_list) for x in df['nodes_visited'].tolist()]
#         pattern = re.compile(",")
#         df['node_visited']=df['node_visited'].apply(lambda x:pattern.split(x))

#         for idx, element in enumerate(df['node_visited']):
#             # extract a list of nodes_name (node_title) and list of node_types
#             # if the node is not found in the dictionary (either bug, or wrong json workspace) then use the dialog_node
#             nodes_name = list(map(lambda x: list(nodes_dict[x])[0].lstrip() if x in nodes_dict else x.lstrip(), element))
#             nodes_type = list(map(lambda x: list(nodes_dict[x])[1].lstrip() if x in nodes_dict else x.lstrip(), element))
#             # if we have ["Login Issues", "node_12_lhagsdkljhsdlkg"]
#             # the indcice_standard would produce [0]
#             indice_standard = [i for i, y in enumerate(nodes_type) if y == "standard"]
#             # check how many value are there in nodes_visited
#             # special case, if last standard node (index -2) is Handoff or More Help - TBD double check with Erica
#             # if we have  ["More Help", "Login Issues"], then select More Help
#             if len (nodes_name)>2 and (nodes_name[-2]=='Handoff' or nodes_name[-2]=='More Help'):
#                 df.loc[idx, 'node_visited'] = nodes_name[-2]
#             elif len (indice_standard) > 0:  # take the last standard node
#                 df.loc[idx, 'node_visited'] = nodes_name[indice_standard[-1]]  ## logs will compare ids to the title
#             else:
#                 df.loc[idx, 'node_visited'] = nodes_name[-1]

#      # TODO: consider uncomment
#      #   if ipython_info() == 'notebook':
#             progress_bar(idx / len(df['node_visited']))
#         cols = ['document_id', 'response_timestamp', 'conversation_id',
#        'request_input', 'response_text', 'nodes_visited', 'response_intent',
#        'branch_exited','branch_exited_reason', 'digression','node_visited']
#         df1 = df[cols].copy(deep=True)
#         # TODO: talk with Doug on intent field. Does it always exist?
#         df1.rename(columns={
#                         'document_id': 'log_id',
#                         'response_intent' : 'intent',
#                         'request_input' : 'request_text'
#                        }, inplace=True)
#         df1.rename(columns={'document_id': 'log_id'}, inplace=True)
#         return df1


def conv_id_dict (df_logs_formated):
    UniqueConv = df_logs_formated.conversation_id.unique()
    ConvDict = {elem : pd.DataFrame for elem in UniqueConv}
    for key in ConvDict.keys():
        ConvDict[key] = df_logs_formated[:][df_logs_formated.conversation_id == key]
    return ConvDict

# TODO: consider using a single implementation for all cases
def extract_dialog_node_name_WA(workspace_nodes):
    """
    Extract more friendly dialog node names from the Watson Assistant workspace
    return a nodes dictionary object.
    """

    nodes_dict = {}
    nodes_type = {}
    for idx,obj in workspace_nodes.iterrows():
        if (obj['type']=='standard') and not (obj['title'] is np.nan or obj['title'] != obj['title']):
            nodes_dict[obj['dialog_node']]=obj['title']
        elif ('conditions' in obj) and (obj['conditions'] != "true"):
            nodes_dict[obj['dialog_node']]=obj['conditions']
        else:
            nodes_dict[obj['dialog_node']]=obj['dialog_node']
    return nodes_dict


def _extract_dialog_node_name(dialog_nodes):
    """
    For each dialog_node (node_id) of type *standard*, check if *title exists*.
    If exists, use the title for the node_name. otherwise, use the dialog_node
    For all other cases, use the dialog_node

    dialog_node: (dialog_node_title, dialog_node_type)

    In the case of Login Issues,
    "title": "Login Issue",
    "dialog_node": "Login Issues",

    the record will be created as:
    "Login Issues": ("Login Issue", "standard")
    """
    nodes_dict = {}
    nodes_type = {}
    for obj in dialog_nodes:
        if (obj['type']=='standard') and ('title' in obj):
            if (obj['title'] is not None):
                nodes_dict[obj['dialog_node']] = (obj['title'],obj['type'])
            else:
                nodes_dict[obj['dialog_node']] = (obj['dialog_node'],obj['type'])
        else:
            nodes_dict[obj['dialog_node']] = (obj['dialog_node'],obj['type'])
    return nodes_dict
