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
import datetime

def by_included_node(node, df_logs_formated):
    """
    return subset of conversations that contains specific node
    """
    print("filtering.by_included_node() is DEPRECATED and will be removed in a future release.  Use filtering2.by_node_id() instead ")
    
    # create an empty dataframe with the same column names and types
    filtered_df_logs = pd.DataFrame(data=None, columns=df_logs_formated.columns)
    for column in filtered_df_logs.columns:
        filtered_df_logs[column] = filtered_df_logs[column].astype(df_logs_formated[column].dtypes.name)

    # TODO: should we sort?
    df_by_conversation_id = df_logs_formated.sort_values(by=["response_timestamp"]).groupby(by="conversation_id")
    # TODO: potentially iterate over groupby
    ConvDict = {}
    for key, group in df_by_conversation_id:
        ConvDict[key] = group

    for i, (k, v) in enumerate(ConvDict.items()):
        # consider if we need to sort
        dfP1=pd.DataFrame(v, columns=v.columns).sort_values(by=['response_timestamp'])
        if any(dfP1['node_visited'] == node):
            filtered_df_logs = pd.concat([filtered_df_logs,dfP1])

    if filtered_df_logs.empty:
        print('Filtering yielded an empty dataframe. Path flow analysis requires a non-empty dataframe.')

    print('Initial amount of records (before filtering):', len(df_logs_formated))
    print('Amount of filtered records:', len(df_logs_formated)-len(filtered_df_logs))
    print('Final amount of records (after filtering):', len(filtered_df_logs))

    return filtered_df_logs


def by_included_absolute_path(path, df_logs_formated):
    """
    return subset of conversations that contains specific node
    @param path path: array
    """
    print("filtering.by_included_absolute_path() is DEPRECATED and will be removed in a future release. ")
    # create an empty dataframe with the same column names and types
    filtered_df_logs = pd.DataFrame(data=None, columns=df_logs_formated.columns)
    for column in filtered_df_logs.columns:
        filtered_df_logs[column] = filtered_df_logs[column].astype(df_logs_formated[column].dtypes.name)

    # TODO: should we sort?
    df_by_conversation_id = df_logs_formated.sort_values(by=["response_timestamp"]).groupby(by="conversation_id")
    # TODO: potentially iterate over groupby
    ConvDict = {}
    for key, group in df_by_conversation_id:
        ConvDict[key] = group

    for i, (k, v) in enumerate(ConvDict.items()):
        # consider if we need to sort
        dfP1=pd.DataFrame(v, columns=v.columns).sort_values(by=['response_timestamp'])
        # length of conversation is at least length of path
        if len(dfP1) >= len(path):
            for i in range(len(path)):
                if path[i] != dfP1.iloc[i]['node_visited']:
                    break
                # last element
                if i == len(path)-1:
                     filtered_df_logs = pd.concat([filtered_df_logs,dfP1])

    if filtered_df_logs.empty:
        print('Filtering yielded an empty dataframe. Path flow analysis requires a non-empty dataframe.')

    print('Initial amount of records (before filtering):', len(df_logs_formated))
    print('Amount of filtered records:', len(df_logs_formated)-len(filtered_df_logs))
    print('Final amount of records (after filtering):', len(filtered_df_logs))

    return filtered_df_logs

def by_initial_intent(intent, df_logs_formated):
    """
    filter conversations starting with initial intent
    """
    print("filtering.by_initial_intent() is DEPRECATED and will be removed in a future release. Use filtering2.by_node_id() instead.")
    
    # create an empty dataframe with the same column names and types
    filtered_df_logs = pd.DataFrame(data=None, columns=df_logs_formated.columns)
    for column in filtered_df_logs.columns:
        filtered_df_logs[column] = filtered_df_logs[column].astype(df_logs_formated[column].dtypes.name)
    df_by_conversation_id = df_logs_formated.sort_values(by=["response_timestamp"]).groupby(by="conversation_id")

    ConvDict = {}
    for key, group in df_by_conversation_id:
        ConvDict[key] = group

    for i, (k, v) in enumerate(ConvDict.items()):
        dfP1=pd.DataFrame(v, columns=v.columns).sort_values(by=['response_timestamp'])
        if (dfP1['intent'].iloc[0] == intent):
            filtered_df_logs = pd.concat([filtered_df_logs,dfP1])
    if filtered_df_logs.empty:
        print('Filtering yielded an empty dataframe. Path flow analysis requires a non-empty dataframe.')

    print('Initial amount of records (before filtering):', len(df_logs_formated))
    print('Amount of filtered records:', len(df_logs_formated)-len(filtered_df_logs))
    print('Final amount of records (after filtering):', len(filtered_df_logs))

    return filtered_df_logs

def from_node_onwards(node, df_logs_formated):
    """
    filtering by truncating conversations from selected node onwards
    """
    print("filtering.from_node_onwards is DEPRECATED and will be removed in a future release. Use filtering2.trim_from_node_id instead.")
    # create an empty dataframe with the same column names and types
    filtered_df_logs = pd.DataFrame(data=None, columns=df_logs_formated.columns)
    for column in filtered_df_logs.columns:
        filtered_df_logs[column] = filtered_df_logs[column].astype(df_logs_formated[column].dtypes.name)

    ## TODO: should we move sorting into the loop? 
    df_by_conversation_id = df_logs_formated.sort_values(by=["response_timestamp"]).groupby(by="conversation_id")
    for conversation_id, conversation_df in df_by_conversation_id:
        i=0
        for index, row in conversation_df.iterrows():
            i=i+1
            node_visited = row["node_visited"]

            if node == node_visited:
                num_of_elements_to_copy = len(conversation_df)-i+1
                filtered_df_logs = pd.concat([filtered_df_logs,conversation_df.tail(num_of_elements_to_copy)])
                break
    if filtered_df_logs.empty:
        print('Filtering yielded an empty dataframe. Path flow analysis requires a non-empty dataframe.')

    print('Initial amount of records (before filtering):', len(df_logs_formated))
    print('Amount of filtered records:', len(df_logs_formated)-len(filtered_df_logs))
    print('Final amount of records (after filtering):', len(filtered_df_logs))

    return filtered_df_logs

def by_date_range(df, start_date, end_date):
    print("filtering.by_date_range is DEPRECATED and will be removed in a future release. Use filtering2.by_date_range instead.")

    mask = (df['response_timestamp'] >= start_date) & (df['response_timestamp'] <= end_date)
    df_1 = df.loc[mask].reset_index()

    if df_1.empty:
        print('Filtering yielded an empty dataframe. Path flow analysis requires a non-empty dataframe.')

    print('Initial amount of records (before filtering):', len(df))
    print('Amount of filtered records:', len(df)-len(df_1))
    print('Final amount of records (after filtering):', len(df_1))

    return df_1