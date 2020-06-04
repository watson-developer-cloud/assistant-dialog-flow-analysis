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

from IPython.display import display, HTML
import pandas as pd
from numpy import nan
import time

class ChainFilter(): 

    def __init__(self, df, description="<<ALL-DATA>>"):
        self.df = df
        self.description = ""
        self.filters = []
        self._append_filter(self.df, "<<ALL-DATA>>", 0)

    def _append_filter(self, df, filter_name, duration_sec):       
        users = conversations = logs = timestamp_from = timestamp_to = nan
        if "conversation_id" in df.columns:
            conversations = len(df["conversation_id"].unique())
        if "log_id" in df.columns:
            logs = len(df["log_id"].unique())
        if "user_id" in df.columns:
            users = len(df["user_id"].unique())
        if len(df) > 0:
            if "response_timestamp" in df.columns:
                timestamp_from = min(df["response_timestamp"])
            if "response_timestamp" in df.columns:
                timestamp_to = max(df["response_timestamp"])
        self.filters.append({"filter_name": filter_name, 
                             "filter_duration_sec": duration_sec,
                             "rows":len(df), 
                             "users": users, 
                             "conversations": conversations,
                             "timestamp_from": timestamp_from,
                             "timestamp_to": timestamp_to,
                             "df": df})
        self.df = df

    def setDescription(self, description):
        self.description = description
        return self

    def printConversationFilters(self):
        display(HTML("<h1>" + self.description + "</h1>"))
        display(HTML(pd.DataFrame(self.filters)[["filter_name", "filter_duration_sec", "rows", "users", "conversations", "timestamp_from","timestamp_to"]].to_html()))
        return self

    def getDataFrame(self, i=-1):
        return self.filters[i]["df"]   

    def getLineageDetails(self, i=-1):
        if i == -1:
            i = len(self.filters)-1
        result = ""
        for j in range(0,i+1):
            if j >0:
                result+= " --> "
            result+= self.filters[j]["filter_name"] + "(" + str(self.filters[j]["conversations"]) + ")"
        return result             
        
    def by_dialog_node_id(self, dialog_node_id):
        """
        filters conversations that include node_id in nodes_visited list
        """
        now = time.time()
        filtered_df = self.df
        #find which rows include the dialog node
        rows = filtered_df[filtered_df.apply(lambda x: dialog_node_id in x["nodes_visited"], axis=1)]
        #find their conversation_id
        unique_conversations = rows["conversation_id"].unique()  
        #filter by conversation
        filtered_df = filtered_df[filtered_df.apply(lambda x: x["conversation_id"] in unique_conversations, axis=1)]
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "by_dialog_node_id (" + dialog_node_id + ")", duration_sec)
        return self

    def by_dialog_node_str(self, dialog_node_str):
        """
        filters conversations that include a node string (title/condition) value in the nodes_visited_str list
        """
        now = time.time()
        filtered_df = self.df
        #find which rows include the dialog node str
        rows = filtered_df[filtered_df.apply(lambda x: dialog_node_str in x["nodes_visited_str"], axis=1)]
        #find their conversation_id
        unique_conversations = rows["conversation_id"].unique()  
        #filter by conversation
        filtered_df = filtered_df[filtered_df.apply(lambda x: x["conversation_id"] in unique_conversations, axis=1)]
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "by_dialog_node_str (" + dialog_node_str + ")", duration_sec)
        return self
    
    def by_turn_label(self, label):
        """
        return the rows of conversations that include a value in turn_label
        """
        now = time.time()
        filtered_df = self.df
        #find which rows include the dialog node
        #rows = filtered_df[filtered_df.apply(lambda x: turn_label in x["node_visited"], axis=1)]
        rows = filtered_df[filtered_df["turn_label"] == label]
        #find their conversation_id
        unique_conversations = rows["conversation_id"].unique()  
        #filter by conversation
        filtered_df = filtered_df[filtered_df.apply(lambda x: x["conversation_id"] in unique_conversations, axis=1)]
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "by_turn_label (" + label + ")", duration_sec)
        return self

    def by_node_name(self, node_name, force_deprecation=False):
        """
        DEPRECATED: return the rows of conversations that include node in node_visited
        """
        if force_deprecation == False:
            print("Error: by_node_name() is deprecated and will be removed in the future. Use by_turn_label() or by_node_id() instead")
            print("For back compatibility, you can use the force_deprecation=True parameter, but make sure to have a 'node_visited' column in your data frame")
            return
        else:
             print("Warning: by_node_name() is deprecated and will be removed in the future. Use by_turn_label() or by_node_id() instead")
        now = time.time()
        filtered_df = self.df
        #find which rows include the dialog node
        rows = filtered_df[filtered_df.apply(lambda x: node_name in x["node_visited"], axis=1)]
        #find their conversation_id
        unique_conversations = rows["conversation_id"].unique()  
        #filter by conversation
        filtered_df = filtered_df[filtered_df.apply(lambda x: x["conversation_id"] in unique_conversations, axis=1)]
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "by_node_name (" + node_name + ")", duration_sec)
        return self
    
    def trim_from_turn_label(self, turn_label):
        """
        filter and trim conversations steps prior to first step that includes a turn label
        """
        now = time.time()
        # create an empty dataframe with the same column names and types
        filtered_df = pd.DataFrame(data=None, columns=self.df.columns)
        for column in filtered_df.columns:
            filtered_df[column] = filtered_df[column].astype(self.df[column].dtypes.name)
        df_by_conversation_id = self.df.groupby(by="conversation_id")
        for conversation_id, conversation_df in df_by_conversation_id:
            i=0
            conversation_df = conversation_df.sort_values(by=["response_timestamp"])
            for index, row in conversation_df.iterrows():
                i=i+1
                if turn_label == row["turn_label"]:
                    num_of_elements_to_copy = len(conversation_df)-i+1
                    filtered_df = pd.concat([filtered_df,conversation_df.tail(num_of_elements_to_copy)])
                    break
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "trim_from_turn_label (" + turn_label + ")", duration_sec)
        return self

    def trim_from_node_id(self, node_id):
        """
        filter and trim conversations steps prior to first step that includes node_id in nodes_visited.
        """
        now = time.time()
     
        # create an empty dataframe with the same column names and types
        filtered_df = pd.DataFrame(data=None, columns=self.df.columns)
        for column in filtered_df.columns:
            filtered_df[column] = filtered_df[column].astype(self.df[column].dtypes.name)
        df_by_conversation_id = self.df.groupby(by="conversation_id")
        for conversation_id, conversation_df in df_by_conversation_id:
            i=0
            conversation_df = conversation_df.sort_values(by=["response_timestamp"])
            for index, row in conversation_df.iterrows():
                i=i+1
                nodes_visited = row["nodes_visited"]
                if node_id in nodes_visited:
                    num_of_elements_to_copy = len(conversation_df)-i+1
                    filtered_df = pd.concat([filtered_df,conversation_df.tail(num_of_elements_to_copy)])
                    break
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "trim_from_node_id (" + node_id + ")", duration_sec)
        return self

    def from_node_onwards(self, node_name):
        """
        DEPCRECATED: filter & trim conversations starting from node_id (in node_visited) 
        """
        print("Error: from_node_onwards() is deprecated. Use trim_from_turn_label() or trim_from_node_id() instead")
        return
        now = time.time()
     
        # create an empty dataframe with the same column names and types
        filtered_df = pd.DataFrame(data=None, columns=self.df.columns)
        for column in filtered_df.columns:
            filtered_df[column] = filtered_df[column].astype(self.df[column].dtypes.name)
        df_by_conversation_id = self.df.groupby(by="conversation_id")
        #df_by_conversation_id = filtered_df.sort_values(by=["response_timestamp"]).groupby(by="conversation_id")
        for conversation_id, conversation_df in df_by_conversation_id:
            i=0
            conversation_df = conversation_df.sort_values(by=["response_timestamp"])
            for index, row in conversation_df.iterrows():
                i=i+1
                node_visited = row["node_visited"]
                if node_name == node_visited:
                    num_of_elements_to_copy = len(conversation_df)-i+1
                    filtered_df = pd.concat([filtered_df,conversation_df.tail(num_of_elements_to_copy)])
                    break
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "from_node_onwards (" + node_name + ")", duration_sec)
        return self
    
    def by_date_range(self, start_date, end_date):
        now = time.time()        
        mask = (self.df['response_timestamp'] >= start_date) & (self.df['response_timestamp'] <= end_date)
        filtered_df = self.df.loc[mask]
        later = time.time()
        duration_sec = int(later - now)
        self._append_filter(filtered_df, "by_date_range (" + str(start_date) + ", " + str(end_date) + ")", duration_sec)
        return self
