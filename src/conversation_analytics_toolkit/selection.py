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

def to_dataframe(selection):
    """convert selection tuples to dataframe
    """
    result = {}

    if len(selection["rerouted"]) == 0:
        result['rerouted'] = pd.DataFrame(columns=['conversation_id','log_id'], dtype='object')
    else:
        result['rerouted'] = pd.DataFrame({'conversation_id': np.array(list(zip(*selection["rerouted"]))[0]), 'log_id': np.array(list(zip(*selection["rerouted"]))[1])})

    if len(selection["dropped_off"]) == 0:
        result['dropped_off'] = pd.DataFrame(columns=['conversation_id','log_id'], dtype='object')
    else:
        result['dropped_off'] = pd.DataFrame({'conversation_id': np.array(list(zip(*selection["dropped_off"]))[0]), 'log_id': np.array(list(zip(*selection["dropped_off"]))[1])})
    #return pd.DataFrame({'conversation_id': np.array(list(zip(*selection))[0]), 'log_id': np.array(list(zip(*selection))[1])})
    return result

def extract_conversation_transcript(df_logs, selection_df, index):
    """extract conversation transcript from logs, based on selection df, and index of interest
    """
    selected_by_index = selection_df.iloc[index]
    transcript = df_logs[df_logs['conversation_id'] == selected_by_index['conversation_id']]
    transcript = transcript.sort_values(by='response_timestamp')
    transcript['you_are_here'] = ""
    transcript.loc[transcript['log_id'] == selected_by_index['log_id'], 'you_are_here'] = '--->'
    return transcript[['you_are_here','response_timestamp','request_text','response_text','log_id','conversation_id','nodes_visited', 'node_visited',
       'branch_exited', 'branch_exited_reason']]


def fetch_logs(logs_df, selection_df):
    """fetch all logs from conversations in selection_df
    """
    print("Deprecated.  Use fetch_logs_by_selection or fetch_logs_by_id")
    return logs_df[logs_df['conversation_id'].isin(list(selection_df['conversation_id']))]

def fetch_logs_by_selection(logs_df, selection_df):
    """fetch all logs from conversations in selection_df
    """
    return logs_df[logs_df['conversation_id'].isin(list(selection_df['conversation_id']))]
    
def fetch_logs_by_id(logs_df, conversation_id):
    """fetch logs by conversation id
    """
    return logs_df[logs_df['conversation_id'] == conversation_id] 

##############################################################################
# fetching utterances from pathflow or milestone chart selection
def get_all_utterances_from_selection(selection, df_logs):
    
    selection_df = to_dataframe(selection)
 
    dropped_off_df = selection_df["dropped_off"]

    dropped_off_conversations = fetch_logs_by_selection(df_logs, dropped_off_df)
    
    input_list=dropped_off_conversations[dropped_off_conversations.request_text!=""].request_text.tolist()
    
    return input_list

def get_last_utterances_from_selection(selection, df_logs):
    
    selection_df = to_dataframe(selection)
 
    dropped_off_df = selection_df["dropped_off"]

    dropped_off_conversations = fetch_logs_by_selection(df_logs, dropped_off_df).sort_values(by=["conversation_id","response_timestamp"])  
    
    input_list=[]
    
    previous_conversation_id=""
    
    for i in range(0,len(dropped_off_conversations)):         
         
        current_conversation_id = dropped_off_conversations.iloc[i,dropped_off_conversations.columns.get_loc("conversation_id")]
        
        if current_conversation_id != previous_conversation_id and i>0:
            input_list.append(dropped_off_conversations.iloc[i-1,dropped_off_conversations.columns.get_loc("request_text")])
                 
        previous_conversation_id = current_conversation_id 
     
    input_list.append(dropped_off_conversations.iloc[len(dropped_off_conversations)-1,dropped_off_conversations.columns.get_loc("request_text")])
           
    return input_list