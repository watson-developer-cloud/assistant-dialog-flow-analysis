# BOILERPLACE
# -------------------------------------->
import sys
sys.path.insert(0, './src')
# -------------------------------------->

import pandas as pd
# reference sources

from conversation_analytics_toolkit import sentiment_analysis

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


def test_sentiment():
    df = _load_test_data_as_df('negative_sentiments.csv')


    df['sentiment_result']=[sentiment_analysis.utterance_sentiment_detailed(user_input) for user_input in df['request_input']]
    df['sentiment']=df['sentiment_result'].str[0]
    df['sentiment_positive_part']=df['sentiment_result'].str[1]
    df['sentiment_negative_part ']=df['sentiment_result'].str[2]
    del df['sentiment_result']

    assert df.iloc[0]["sentiment"] < -0.3
