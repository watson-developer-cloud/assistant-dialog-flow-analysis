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

import re

def _events_from_row(canonical_row):
    events_array=[]
    current_request = canonical_row["request_text"]
    current_response = canonical_row["response_text"]
    if current_request!="":
        event={}
        event["agent"]="user"
        event["type"]="request"
        event["timestamp"]=canonical_row["response_timestamp"]
        current_message={}
        current_message["text"]=current_request
        current_messages=[current_message]
        event["messages"]=current_messages
        if "highlight" in canonical_row:
            if canonical_row["highlight"] == True:
                event["highlight"] = True                   
        events_array.append(event)

    # create response object
    event={}
    event["agent"]="bot"
    event["type"]="response"
    event["timestamp"]=canonical_row["response_timestamp"]
    current_message={}
    current_message["text"]=current_response
    if "node_visited" in canonical_row:
        event["node_visited"] = canonical_row["node_visited"]        
    if "bot_response_buttons" in canonical_row:
        # temporary add buttons as 2nd 
        s = canonical_row["bot_response_buttons"]
#         s = s.replace(']','')
#         s = s.replace('[','')
#         s = s.replace("'",'')
        if s != '[]':
            current_message["buttons"] = s
    if "bot_response_action" in canonical_row:
        if canonical_row["bot_response_action"]=="Transfer":
            event["type"]="handoff"
        event["action"] = canonical_row["bot_response_action"]  
    if 'turn_label' in canonical_row:
        event["turn_label"] = canonical_row["turn_label"]  
    if 'nodes_visited_str' in canonical_row:
        event["nodes_visited_str"] = canonical_row["nodes_visited_str"]  
    if 'nodes_visited' in canonical_row:
        event["nodes_visited"] = canonical_row["nodes_visited"]  
    if 'skill_name' in canonical_row:
        event["skill_name"] = canonical_row["skill_name"]  
    
    current_messages=[current_message]
    event["messages"]=current_messages 
    events_array.append(event)

    return events_array        

def _add_insights_tags(existing_tags, canonical_row):
    if "insights_tags" in canonical_row:
        new_tags = canonical_row["insights_tags"]
        for new_tag in new_tags:
            if new_tag in existing_tags:
                existing_tags[new_tag]+=1
            else:
                existing_tags[new_tag]=1            

def to_transcript(df_canonical):
    dict_list=[]
    df_canonical=df_canonical.sort_values(by=["conversation_id", "response_timestamp"])
    conversations=df_canonical.groupby("conversation_id")
    for name, group in conversations:
        current_dict={}
        current_conversation={}
        current_conversation["id"]=name
        current_dict["conversation"]=current_conversation
         
        conversation_events=[]
        insight_tags = {} # map of tags to their counts
        for row_index, row in group.iterrows():
            conversation_events.extend(_events_from_row(row))
            _add_insights_tags(insight_tags, row)
        current_dict["events"] = conversation_events
        current_dict["insight_tags"] = insight_tags
        dict_list.append(current_dict)
        
    return dict_list