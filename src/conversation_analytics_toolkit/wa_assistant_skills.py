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
import re

def build_dialog_node_index(workspace):
    dialog_nodes_by_id = {}
    for dialog_node in workspace['dialog_nodes']:
        dialog_nodes_by_id[dialog_node["dialog_node"]] = dialog_node     
    return dialog_nodes_by_id

class DialogNodeNotFound(KeyError):
    def __init___(self,skill, node):
        KeyError.__init__(self,"Skill or Node not found in Dialog {0}:{1}".format(skill, node))
        self.skill = skill
        self.node = node

class WA_Assistant_Skills:
    def __init__(self, name=""):
        self._assistant_name = name
        self._skills = {}
        
    def add_skill(self, skill_id, workspace):
        """Add a skill and create an index to fast lookup nodes by id

        The index field named "dialog_nodes_by_id" and it will be added to the rest of the WA fields:
        name, intents, entities, language, metadata, description, dialog_nodes, workspace_id, counter_examples. learning_opt_out, status
        
        Parameters
        ----------
        skill_id : str
            The file location of the spreadsheet
        workspace : dictionary
            the workspace object as received by WA v1 API
        """

        if skill_id in self._skills.keys():
            raise ValueError("Duplicate skill id: {} ".format(skill_id))
        workspace["dialog_nodes_by_id"] = build_dialog_node_index(workspace)
        self._skills[skill_id] = workspace

    def get_skill_by_id(self, skill_id):
        return self._skills[skill_id]
    
    def get_skill_name_by_id(self, skill_id, strict=False):
        if strict == True: 
            return self._skills[skill_id]["name"]
        if skill_id in self._skills:
            return self.get_skill_by_id(skill_id)["name"]
        else: 
            return "?"
    def get_name(self):
        return self._assistant_name

    def is_single_skill(self):
        return len(self._skills.keys()) == 1
    
    def get_single_skill(self):
        if not self.is_single_skill():
            raise ValueError("found more than one skill. This function supports only a single skill assistant")
        for value in self._skills.values():
            first_skill = value
            return first_skill

    def get_node_by_id(self, skill_id, node_id):
        skill = self.get_skill_by_id(skill_id)
        node = skill["dialog_nodes_by_id"][node_id]
        return node


    def find_first_skill_id_for_node(self, node_id):
        """
        Return the first skill_id that includes the node, otherwise None
        """
        for skill_id in self._skills:
            skill = self.get_skill_by_id(skill_id)
            if node_id in skill["dialog_nodes_by_id"]:
                return skill_id
        return None

    def get_node_by_id_any_skill(self, node_id):
        """
        find the first skill that includes the node_id definition and return the node in that skill.
        This function is useful for checking for nodes in multiple versiosn of skills, or when a user does not 
        want to match against the skill_id field, e.g. if he doesn't have access to all workspaces files
        """
        for skill_id in self._skills:
            skill = self.get_skill_by_id(skill_id)
            if node_id in skill["dialog_nodes_by_id"]:
                return skill["dialog_nodes_by_id"][node_id]
        #TBD return None or throw exception?
        raise DialogNodeNotFound("", node_id)

    def list_skills(self):
        return [self.get_skill_summary(skill_id) for skill_id in self._skills.keys()]
        #return list(self._skills.keys()) 
    
    def get_skill_summary(self, skill_id):
        skill = self.get_skill_by_id(skill_id)
        return { 
            'skill_id': skill_id, 
            'name': skill["name"], 
            'description': skill["description"] if "description" in skill else "", 
            'metadata': skill['metadata'], 
            'workspace_id': skill["workspace_id"] if "workspace_id" in skill else "",
            'num_of_intents': len(skill["intents"]),
            'num_of_entities': len(skill["entities"]),
            'num_of_dialog_nodes': len(skill["dialog_nodes"]),
            }
    
    def _get_nested_value_in_node(self, node, key):
        """returns the value a nested key (e.g. context.current_step, output.text.values)

        Parameters:
        node (Dictionary): The dialog node to search in
        key (string): The attribute key 

        Returns:
        None:if the key doesn't exist
        string: if the value is string
        string[]: if the value is an array
        """
        result = None
        key_attributes = key.split(".")
        obj = node
        for i in range(len(key_attributes)):
            if not isinstance(obj,dict):
                # can't drill down into a non dict type
                obj = None
                break
            obj = obj.get(key_attributes[i])
            if obj == None:
                # if attribute is missing, then break out of the loop and result will be None
                break
        if isinstance(obj,dict):
            # final object must be a primitive or list
            result = None
        else:
            result = obj
        return result

    def re_search_in_dialog_nodes(self, regex_str, keys=["title", "conditions", "dialog_node"], in_skill=None):
        """Find regular expression case insensitive search in nodes across the skills
        """
        results=[]
        columns=["skill_id", "dialog_node", "type", "title", "conditions", "matched_in","matched_location"]
        for skill_id in self._skills:
            if in_skill != None:
                if skill_id != in_skill:
                    continue 
            for node in self._skills[skill_id]["dialog_nodes"]:
                for key in keys:
                    if key not in columns:
                        columns.append(key)
                    value = self._get_nested_value_in_node(node, key)
                    #if key in node.keys():
                    if value != None:
                        #print (node[key])
                        #match = re.search(regex_str, node[key], re.IGNORECASE)
                        match = re.search(regex_str, value, re.IGNORECASE)
                        if match:
                            #result = node.copy()
                            result = {}
                            result["title"] = node.get("title", "")
                            result["conditions"] = node.get("conditions", "")
                            result["type"] = node.get("type", "")
                            result["dialog_node"] = node.get("dialog_node", "")
                            result["skill_id"] = skill_id
                            result["matched_in"] = key 
                            result["matched_location"] = str(match.regs[0])
                            if "." in key:
                                # for nested keys, e.g. output.text.values, create a first level attribute "output.text.values"
                                result[key] = value
                            elif key not in ["dialog_node", "type", "title", "conditions"]:
                                #required otherwise the parsing into dataframe will fail
                                result[key] = ""
                            results.append(result)

        df = pd.DataFrame(columns=columns)
        df = df.append(pd.DataFrame(results))
        
        return df[columns]

    def to_milestone_dict(self, search_results_df, prefered_milestone_labels):
        """converts a search result into a milestone dictionary, that can be used in a milestone chart
        
        Parameters:
        search_results_df (DataFrane): The result of calling re_search_in_dialog_nodes
        prefered_milestone_labels (string[]): a list of columns from which to take the label.  The first one with a non empty value will be used
        
        Returns:
        Dict: a mapping from node --> milestone label
        """
        def determine_milestone(row):
            milestone_label = ""
            for column in prefered_milestone_labels:
                milestone_label = row[column]
                if len(milestone_label) > 0:
                    break;
            return milestone_label
        search_results_df['milestones'] = search_results_df.apply(determine_milestone, axis = 1) 
        df = search_results_df[["dialog_node", "milestones"]]
        df = df.set_index("dialog_node")
        return df.to_dict(orient='dict')["milestones"]
