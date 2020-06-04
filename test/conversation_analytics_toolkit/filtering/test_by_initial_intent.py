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


def test_filter_by_initial_intent_1():
    df = pd.read_csv('./test/conversation_analytics_toolkit/testdata/df_logs_to_analyze_sample.csv')
    initial_intent ='greetings'
    filtered_df = pathflow_filtering.by_initial_intent(initial_intent, df.loc[0:5])
    assert set(list(filtered_df['conversation_id'].unique())) == set(['1097b76c-4125-4f21-832e-99c718996e61','28b7bdf0-c72a-4503-8f34-ca2a9907a974', '8e842901-e259-497a-b699-2f5919331a47'])

def test_filter_by_initial_intent_2():
    df = pd.read_csv('./test/conversation_analytics_toolkit/testdata/df_logs_to_analyze_sample.csv')
    initial_intent ='turn_on'
    filtered_df = pathflow_filtering.by_initial_intent(initial_intent, df)
    assert (len (filtered_df) == 4)

def test_filter_by_initial_intent_empty_dataframe():
    df = pd.read_csv('./test/conversation_analytics_toolkit/testdata/df_logs_to_analyze_empty.csv')
    initial_intent ='xyz'
    filtered_df = pathflow_filtering.by_initial_intent(initial_intent, df)
    assert (len (filtered_df) == 0)
