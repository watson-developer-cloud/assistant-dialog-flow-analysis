# BOILERPLACE
# -------------------------------------->
import sys
sys.path.insert(0, './src')
# -------------------------------------->

import numpy as np
import json
import pandas as pd

from conversation_analytics_toolkit import transformation as pathflow_transformation

def _load_test_logs_file(file):
    with open('./test/conversation_analytics_toolkit/testdata/'+ file) as f:
        try:
            data = json.load(f)
        except ValueError:
            data = []
    df = pd.DataFrame.from_records(data)
    return df

def test_to_canonical_WA_empty_input_df():
    df = _load_test_logs_file('df_logs_empty.json')
    workspace_nodes = pd.read_csv('./test/conversation_analytics_toolkit/testdata/workspace_nodes.csv')
    wa_nodes_dict = pathflow_transformation.extract_dialog_node_name_WA(workspace_nodes)
    df_logs_canonical = pathflow_transformation.to_canonical_WA(df, wa_nodes_dict)
    assert (len(df_logs_canonical) == 0)

