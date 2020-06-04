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

###################################################################
from textblob import TextBlob
import re

########################################################################
def add_sentiment_columns(df_logs_canonical):
    df_logs_canonical['sentiment_result']=\
        [utterance_sentiment_detailed(user_input) for user_input in df_logs_canonical['request_text']]
    
    df_logs_canonical['sentiment']=df_logs_canonical['sentiment_result'].str[0]        
    df_logs_canonical['sentiment_positive_part']=df_logs_canonical['sentiment_result'].str[1]  
    df_logs_canonical['sentiment_negative_part']=df_logs_canonical['sentiment_result'].str[2]  
    
    del df_logs_canonical['sentiment_result']
    
    return df_logs_canonical

#################################################
def is_thanks(str):

    list_thanks =['thank']

    list_words=str.split()
    num_words=len(list_words)

    if num_words<5:

        for i in range(0,num_words):
            current_word=list_words[i].lower()
            current_word=re.sub("[^a-zA-Z]+", "",current_word)
            if current_word in list_thanks:
                return True, current_word

    return False, ""

########################################################

def utterance_sentiment_detailed(user_input):
    
    sentiment = TextBlob(user_input)
    
    current_blob_polarity=sentiment.sentiment.polarity
    current_blob_assessment = sentiment.sentiment_assessments.assessments
    
    num_assessments =len(current_blob_assessment)
    
    positive_list=""
    negative_list=""
    
    for i in range(0,num_assessments):
        current_sent = current_blob_assessment[i][1]
        current_words = current_blob_assessment[i][0]
        num_words=len(current_words)
        
        if current_sent>0:
            for j in range(0, num_words):
                positive_list += (current_words[j]+" ")
        elif current_sent<0:
            for j in range(0, num_words):
                negative_list += (current_words[j]+" ")           
    
    if current_blob_polarity==0:
        is_th = is_thanks(user_input)
        if is_th[0]: 
            current_blob_polarity=0.2
            positive_list += (is_th[1]+" ")
    
    return current_blob_polarity, positive_list, negative_list

###########################################################

def utterance_sentiment(user_input):
    
    sentiment = TextBlob(user_input)
    
    current_blob_estimate=sentiment.sentiment.polarity
    
    if current_blob_estimate==0:
        if is_thanks(user_input):
            current_blob_estimate=0.5
    
    return current_blob_estimate

#############################################

def normalize_sentiment(sentiment):
    
    if sentiment<-1:
        return -1
    elif sentiment>1:
        return 1
    else: 
        return sentiment     
