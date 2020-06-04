# BOILERPLACE
# -------------------------------------->
import sys
sys.path.insert(0, './src')
# -------------------------------------->

import pandas as pd
import datetime
# reference sources

from conversation_analytics_toolkit import filtering

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


# def test_filter_by_date():
#     df = _load_test_data_as_df('df_logs_to_analyze_sample.csv')
#     start_date = datetime.datetime(2018, 9, 17)
#     end_date = datetime.datetime(2018, 9, 18)    

#     filtered_df = filtering.by_date_range (df, start_date, end_date)
#     assert len(filtered_df) == 99

def test_filter_by_timestamp_range():
    # test that all data is in this date range (number of records) 2018-09-17 18:54:17.000 and 18:54:19.000 contains 2 records
    df = _load_test_data_as_df('df_logs_to_analyze_sample.csv')

    start_date = datetime.datetime(2018, 9, 17, 18, 54, 17)
    end_date = datetime.datetime(2018, 9, 17, 18, 54, 19)   

    filtered_df = filtering.by_date_range (df, start_date, end_date)
    print(filtered_df["response_timestamp"])
    assert len(filtered_df) == 3

def test_filter_by_date_range():
    df = _load_test_data_as_df('df_logs_to_analyze_sample.csv')

    start_date = datetime.datetime(2018, 9, 17)
    end_date = datetime.datetime(2018, 9, 18)  

    filtered_df = filtering.by_date_range (df, start_date, end_date)
    assert len(filtered_df) == 99
