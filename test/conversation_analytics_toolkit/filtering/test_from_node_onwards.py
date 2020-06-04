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
    import os
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


def test_filter_from_node_onward_one_conversation_sorted():
    df = _load_test_data_as_df('one_conversation_sorted.csv')
    onwards_node ='4'
    filtered_df = pathflow_filtering.from_node_onwards (onwards_node, df)
    assert (list(filtered_df['node_visited']) == ['4','5','6', '77','8'])

def test_filter_from_node_onward_one_conversation_unsorted():
    df = _load_test_data_as_df('one_conversation_unsorted.csv')
    onwards_node ='4'
    filtered_df = pathflow_filtering.from_node_onwards (onwards_node, df)
    assert (list(filtered_df['node_visited']) == ['4','5'])

def test_filter_from_node_onward_empty_input_df():
    df = _load_test_data_as_df('empty_df.csv')
    onwards_node ='4'
    filtered_df = pathflow_filtering.from_node_onwards (onwards_node, df)
    assert (len(filtered_df['node_visited']) == 0)

def test_filter_from_node_onward_empty_result():
    df = _load_test_data_as_df('one_conversation_sorted.csv')
    onwards_node ='not_existing_node'
    filtered_df = pathflow_filtering.from_node_onwards (onwards_node, df)
    assert (len(filtered_df['node_visited']) == 0), "expecting empty dataframe (received None or Excpetion?)"

def test_filter_from_node_onward_substring():
    df = _load_test_data_as_df('one_conversation_sorted.csv')
    onwards_node ='7'
    filtered_df = pathflow_filtering.from_node_onwards (onwards_node, df)
    assert (len(filtered_df['node_visited']) == 0), "expecting empty df"

def test_filter_from_node_onward_with_repetitions():
    df = _load_test_data_as_df('two_conversations_with_repetition.csv')
    onwards_node ='3'
    filtered_df = pathflow_filtering.from_node_onwards (onwards_node, df)

    assert (list(filtered_df['node_visited']) == ['3','4','1','2','3','3','4','1','2'])
