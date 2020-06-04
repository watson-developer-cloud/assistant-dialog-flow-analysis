# BOILERPLACE
# -------------------------------------->
import sys
sys.path.insert(0, './src')
# -------------------------------------->

import numpy as np
import json
import pandas as pd
import os
#

#pwd
from conversation_analytics_toolkit import transformation as pathflow_transformation

def test_to_canonical_empty_input_df():
    df = pd.read_csv('./test/conversation_analytics_toolkit/testdata/df_logs_empty.csv')
    with open("./test/conversation_analytics_toolkit/testdata/workspace.json") as datafile:
        workspace_data = json.load(datafile)
    nodes_dict = pathflow_transformation._extract_dialog_node_name(workspace_data["dialog_nodes"])
    df_logs_canonical = pathflow_transformation._to_canonical(df, nodes_dict)
    assert (len(df_logs_canonical) == 0)



