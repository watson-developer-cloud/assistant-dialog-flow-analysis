# BOILERPLACE
# -------------------------------------->
import sys
sys.path.insert(0, './src')
# -------------------------------------->

import numpy as np
import json
import pandas as pd
import os
# reference sources

#pwd
from conversation_analytics_toolkit import transformation as pathflow_transformation

def test_extract_dialog_node_name_WA_empty_work_space():
    workspace_nodes_sample = pd.read_csv('./test/conversation_analytics_toolkit/testdata/workspace_nodes_empty.csv')
    wa_nodes_dict = pathflow_transformation.extract_dialog_node_name_WA(workspace_nodes_sample)
    assert (len(wa_nodes_dict) == 0)

 