# BOILERPLACE
# -------------------------------------->
import sys
sys.path.insert(0, './src')
# -------------------------------------->

import pandas as pd
# reference sources

from conversation_analytics_toolkit import filtering as pathflow_filtering

def setup_module(module):
    # called before this modeule
    print ("setup_module      module:%s" % module.__name__)

def teardown_module(module):
    # called after this module
    print ("teardown_module   module:%s" % module.__name__)

def setup_function(function):
    # called before each function
    print ("setup_function    function:%s" % function.__name__)

def teardown_function(function):
    # called after each function
    print ("teardown_function function:%s" % function.__name__)

def _load_test_data_as_df(file):
    """
    loads test data from current directory
    """
    path = './test/conversation_analytics_toolkit/testdata/' + file
    dtype_dict={
        'conversation_id': str,
        'log_id':str,
        'request_input':str,
        'response_text':str,
        'response_branch_exited':bool,
        'response_branch_exited_reason':str,
        'node_visited':str
    }
    return pd.read_csv(path, encoding='utf-8',parse_dates=['response_timestamp'], dtype=dtype_dict, keep_default_na=False)


def test_filter_by_included_node():
    df = _load_test_data_as_df('four_conversations.csv')
    node ='4'
    filtered_df = pathflow_filtering.by_included_node(node, df)
    assert set(list(filtered_df['conversation_id'].unique())) == set(['10','21'])

def test_filter_by_included_node_empty_input_df():
    df = _load_test_data_as_df('empty_df.csv')
    included_node ='4'
    filtered_df = pathflow_filtering.by_included_node (included_node, df)
    assert (len(filtered_df['node_visited']) == 0)

def test_filter_by_included_node_substring():
    df = _load_test_data_as_df('one_conversation_sorted.csv')
    included_node ='7'
    filtered_df = pathflow_filtering.by_included_node (included_node, df)
    assert (len(filtered_df['node_visited']) == 0)

def test_filter_by_included_node_empty_result():
    df = _load_test_data_as_df('one_conversation_sorted.csv')
    included_node ='not_existing_node'
    filtered_df = pathflow_filtering.by_included_node (included_node, df)
    assert (len(filtered_df['node_visited']) == 0), "expecting empty dataframe (received None or Excpetion?)"
