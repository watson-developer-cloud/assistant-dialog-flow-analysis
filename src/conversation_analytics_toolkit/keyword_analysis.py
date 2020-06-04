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

from nltk.corpus import stopwords  
#####################################################################

##############################################################
import re 
import pandas as pd

#######################################################################
from sklearn.feature_extraction.text import CountVectorizer 
 

def order_ngram(ngram): 
    words = ngram.split()
    # sort the list.
    words.sort()
    return " ".join(words)

##############################################################
# returns clean string
def clean_text(text, custom_stop_words = []):
    
    REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
    BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_:]') 
    text = text.lower() # lowercase text
    text = REPLACE_BY_SPACE_RE.sub(' ', text) # replace REPLACE_BY_SPACE_RE symbols by space in text
    text = BAD_SYMBOLS_RE.sub('', text) # delete symbols which are in BAD_SYMBOLS_RE from text
    
    STOPWORDS = set(stopwords.words('english'))
    STOPWORDS = STOPWORDS | set(custom_stop_words)
    
    text = ' '.join(word for word in text.split() if word not in STOPWORDS) 
    
    return text
 
def get_frequent_words_bigrams(utterances, num_unigrams,num_bigrams,custom_stop_words):
    
    utterances = [clean_text(x,custom_stop_words) for x in utterances]
    
    if len(utterances)==0:
        print("Warning! List of utterances is empty")
        return {"name": "","children": []}
    
    unigrams_found = False
    bigrams_found = False
    
    for i in range(0, len(utterances)):
        current_length=len(utterances[i].split())
        if current_length>1:
            unigrams_found = True
            bigrams_found = True
            break
        elif current_length>0:
            unigrams_found = True
    
    if not unigrams_found:
        print("Warning! List of utterances is empty. Perhaps the documents only contain stop words")
        return {"name": "","children": []}
    
    cv_words = CountVectorizer(ngram_range=(1,1))
    
    cv_fit_words=cv_words.fit_transform(utterances)     
    word_list = cv_words.get_feature_names();    
    word_count_list  = cv_fit_words.toarray().sum(axis=0)    
    words_zip = sorted(zip(word_count_list, word_list),reverse=True)
    words_zip=words_zip[0:min(len(words_zip), num_unigrams)]
    
    if bigrams_found:
        cv_bigrams = CountVectorizer(ngram_range=(2,2))
        
        cv_fit_bigrams=cv_bigrams.fit_transform(utterances)     
        bigram_list = cv_bigrams.get_feature_names();    
        bigram_count_list  = cv_fit_bigrams.toarray().sum(axis=0)    
        bigram_zip = sorted(zip(bigram_count_list, bigram_list),reverse=True)
        bigram_zip=bigram_zip[0:num_bigrams]
        
    else:
        print("Warning! List of bigrams is empty.")

    children = []
    for i in range(0, min(len(words_zip), num_unigrams)):
        children.append({"name": words_zip[i][1], "value": int(words_zip[i][0])})
    if bigrams_found:
        for i in range(0, min(len(bigram_zip), num_bigrams)):
            children.append({"name": bigram_zip[i][1], "value": int(bigram_zip[i][0])})
    data = {"name": "","children": children}

    return data
 
##########################################################################################################
def get_df_frequencies(neg_dict, pos_dict, neg_list, pos_list, table_title1, table_title2):
    neg_list_neg_freq=[]
    neg_list_pos_freq=[]
    pos_list_neg_freq=[]
    pos_list_pos_freq=[]
     
    num_neg_features = len(neg_list)
    if num_neg_features==0:
        print("Warning! No significant keywords were found.")
        
    num_pos_features = len(pos_list)
    
    for i in range(0, num_neg_features):
        neg_list_neg_freq.append(neg_dict[neg_list[i]][0])              
        neg_list_pos_freq.append(neg_dict[neg_list[i]][2]) 
        
    for i in range(0, num_pos_features):        
        pos_list_pos_freq.append(pos_dict[pos_list[i]][0])              
        pos_list_neg_freq.append(pos_dict[pos_list[i]][2])
                
    if num_neg_features>num_pos_features:
        D = [None]*(num_neg_features-num_pos_features)
        pos_list.extend(D)
        pos_list_pos_freq.extend(D)
        pos_list_neg_freq.extend(D)
    
    if num_pos_features>num_neg_features:
        D = [None]*(num_pos_features-num_neg_features)
        neg_list.extend(D)
        neg_list_neg_freq.extend(D)
        neg_list_pos_freq.extend(D)
    
    df_frequencies = pd.DataFrame() 
    df_frequencies[table_title1] = neg_list 
    df_frequencies["Failure keywords: negative corpus frequencies, %"] = neg_list_neg_freq
    df_frequencies["Failure keywords: positive corpus frequencies, %"] = neg_list_pos_freq
    df_frequencies[table_title2] = pos_list
    df_frequencies["Success keywords: positive corpus frequencies, %"] = pos_list_pos_freq
    df_frequencies["Success keywords: negative corpus frequencies, %"] = pos_list_neg_freq

    return df_frequencies    


########################################################################
def get_features(text_negative, text_positive, num_features, n_range=(1,2)):    
    
    PRINT_MODE = False
    
    #no_shows=["account","number"]
    no_shows=[]
    
    ratio_parameter=2.0
    num_negative=len(text_negative)
    num_positive=len(text_positive)
     
    cv_negative = CountVectorizer(ngram_range=n_range)
    
    cv_fit=cv_negative.fit_transform(text_negative)     
    word_list_negative = cv_negative.get_feature_names();    
    count_list_negative = cv_fit.toarray().sum(axis=0)    
    negative_count_unigrams = sorted(zip(count_list_negative, word_list_negative),reverse=True)  
    dict_negative = {word_list_negative[i]: count_list_negative[i] for i in range(len(word_list_negative))} 
 
    cv_positive = CountVectorizer(ngram_range=n_range)
             
    cv_fit=cv_positive.fit_transform(text_positive)     
    word_list_positive = cv_positive.get_feature_names();    
    count_list_positive = cv_fit.toarray().sum(axis=0)    
    positive_count_unigrams = sorted(zip(count_list_positive, word_list_positive),reverse=True)  
    dict_positive = {word_list_positive[i]: count_list_positive[i] for i in range(len(word_list_positive))} 
    
    ##############################
    # perform frequence check, print warnings
    counter_neg_features=0
    counter=0
    neg_list_sorted=[]
    neg_list=[]
    neg_dict={}
    while counter_neg_features<num_features:
        current_neg_feature=negative_count_unigrams[counter][1] 
        current_neg_count=negative_count_unigrams[counter][0]
            
        get_neg_freq=current_neg_count / num_negative 
        
        if current_neg_feature in dict_positive.keys():
            current_pos_count = dict_positive[current_neg_feature]
            get_pos_freq = (current_pos_count + 0.0) / num_positive 
        else:
            current_pos_count = 0
            get_pos_freq = 1.0 / num_positive 
         
        if ratio_parameter*get_pos_freq>=get_neg_freq:
            if PRINT_MODE:
                print("Frequencies for negative feature "+current_neg_feature+" are not appropriate. Feature is omitted")
                print("Negative frequency: "+str(get_neg_freq))
                print("Positive frequency: "+str(get_pos_freq))
                
        elif current_neg_feature not in no_shows:
            S = order_ngram(current_neg_feature)
            if S in neg_list_sorted:
                ind = neg_list_sorted.index(S)
                prev = neg_list[ind] 
                neg_dict[prev][0] += current_neg_count
                neg_dict[prev][1] += current_pos_count
                neg_dict[prev][2] += ((current_neg_count + neg_dict[prev][0]) / max(current_pos_count + neg_dict[prev][1],1)) *\
                    (num_positive/num_negative)
            else:
                neg_list.append(current_neg_feature)
                neg_list_sorted.append(S)

                neg_dict[current_neg_feature] = [current_neg_count, current_pos_count, get_neg_freq / get_pos_freq]
                counter_neg_features+=1
        
        counter+=1 
        
        if counter==len(negative_count_unigrams):
            break
        
    counter_pos_features=0
    counter=0
    pos_list_sorted=[]
    pos_list=[]
    pos_dict={}
    while counter_pos_features<num_features:
        current_pos_feature = positive_count_unigrams[counter][1] 
        current_pos_count = positive_count_unigrams[counter][0]
        
        get_pos_freq=current_pos_count / num_positive
        
        if current_pos_feature in dict_negative.keys():
            current_neg_count = dict_negative[current_pos_feature]
            get_neg_freq = dict_negative[current_pos_feature]
        else:
            current_neg_count = 0
            get_neg_freq = 1.0 / num_negative         
        
        if get_pos_freq<=ratio_parameter*get_neg_freq:
            if PRINT_MODE:
                print("Frequencies for positive feature '"+current_pos_feature+"' are not appropriate. Feature is omitted.")
                print("Negative frequency: "+str(get_neg_freq))
                print("Positive frequency: "+str(get_pos_freq))
        elif current_pos_feature not in no_shows:
            S = order_ngram(current_pos_feature)
            if S in pos_list_sorted:
                ind = pos_list_sorted.index(S)
                prev = pos_list[ind] 
                pos_dict[prev][0] += current_pos_count
                pos_dict[prev][1] += current_neg_count
                pos_dict[prev][2] += ((current_pos_count + pos_dict[prev][0]) / max(current_neg_count + pos_dict[prev][1],1)) *\
                    (num_negative/num_positive )
            else:
                pos_list.append(current_pos_feature)
                pos_list_sorted.append(S)
                
                pos_dict[current_pos_feature] = [current_pos_count, current_neg_count, get_pos_freq / get_neg_freq]
                counter_pos_features+=1
        
        counter+=1    
        
        if counter==len(positive_count_unigrams):
            break  
    
    return neg_dict, pos_dict, neg_list, pos_list 



########################################################################
def keyword_table_detailed(text_negative, text_positive, num_keywords, custom_stop_words, title1="Title 1", title2="Title 2"):
    
    COEFF = [0.4, 0.4, 0.2]
    
    text_positive = [clean_text(x,custom_stop_words) for x in text_positive]
    text_negative = [clean_text(x,custom_stop_words) for x in text_negative]
    
    if len(text_positive)==0 or len(text_negative)==0:
        print("Warning! At least one of List of utterances is empty")
        neg_dict = {}
        pos_dict = {}
        neg_list = [] 
        pos_list = []
        
    else:        
        
        unigrams_found_negative = False
        bigrams_found_negative = False
        trigrams_found_negative = False
        
        for i in range(0, len(text_negative)):
            current_length=len(text_negative[i].split())
            if current_length>2:
                unigrams_found_negative = True
                bigrams_found_negative = True
                trigrams_found_negative = True
                break
            elif current_length>1:
                unigrams_found_negative = True
                bigrams_found_negative = True
            elif current_length>0:
                unigrams_found_negative = True
        
        ################################################################        
        unigrams_found_positive = False
        bigrams_found_positive = False
        trigrams_found_positive = False
        
        for i in range(0, len(text_positive)):
            current_length=len(text_positive[i].split())
            if current_length>2:
                unigrams_found_positive = True
                bigrams_found_positive = True
                trigrams_found_positive = True
                break
            elif current_length>1:
                unigrams_found_positive = True
                bigrams_found_positive = True
            elif current_length>0:
                unigrams_found_positive = True        
        
        ####################################################################
        unigrams_found = unigrams_found_negative and unigrams_found_positive
        bigrams_found = bigrams_found_negative and bigrams_found_positive
        trigrams_found = trigrams_found_negative and trigrams_found_positive
        
        if not unigrams_found:
            print("Warning! At least one of utterance lists is empty. Perhaps the documents only contain stop words")
            neg_dict = {}
            pos_dict = {}
            neg_list = [] 
            pos_list = []
        else:
            num_keywords1 = round(num_keywords*COEFF[0])
        
            neg_dict, pos_dict, neg_list, pos_list =  get_features(text_negative,text_positive,num_keywords1,n_range=(1,1))
            
            if not bigrams_found:
                print("Warning! No bigrams for at least one of utterance lists.")  
            else:
     
                num_keywords2 = round(num_keywords*COEFF[1])
            
                neg_dict2, pos_dict2, neg_list2, pos_list2 =  get_features(text_negative,text_positive,num_keywords2,n_range=(2,2))
                
                neg_list.extend(neg_list2)  
                pos_list.extend(pos_list2) 
                
                neg_dict.update(neg_dict2) 
                pos_dict.update(pos_dict2) 
                
                if not trigrams_found:
                    print("Warning! No trigrams for at least one of utterance lists.")    
                else:  
                    num_keywords3 = num_keywords - num_keywords1 - num_keywords2 
    
                    neg_dict3, pos_dict3, neg_list3, pos_list3 =  get_features(text_negative,text_positive,num_keywords3,n_range=(3,3))
     
                    neg_list.extend(neg_list3)                      
                    pos_list.extend(pos_list3)                     
                   
                    neg_dict.update(neg_dict3)                   
                    pos_dict.update(pos_dict3)
  
    ####################################################################################################   
    df_frequencies = get_df_frequencies(neg_dict, pos_dict, neg_list, pos_list, title1, title2) 
    
    df_frequencies.rename(columns={"Failure keywords: negative corpus frequencies, %": title1+": Frequency",\
                                   "Failure keywords: positive corpus frequencies, %": title1+": Power",\
                                   "Success keywords: positive corpus frequencies, %": title2+": Frequency",\
                                   "Success keywords: negative corpus frequencies, %": title2+": Power"}, inplace=True)
     
    return df_frequencies

################################################################################################
def get_data_for_comparison_visual(user_input_abandoned, user_input_completed, num_keywords, custom_stop_words=[]):
        
    df_keywords_detailed = keyword_table_detailed(user_input_abandoned, user_input_completed, num_keywords, custom_stop_words)
    
    #print(df_keywords_detailed.head(n=25))
    
    data={}
    data["name"]=""
    data["children"]=[]
    for i in range(0,len(df_keywords_detailed)):
        if  df_keywords_detailed.iloc[i,1] is None:
            data["children"].append({"name": df_keywords_detailed.iloc[i,0], "value": df_keywords_detailed.iloc[i,1]})
        else:
            data["children"].append({"name": df_keywords_detailed.iloc[i,0], "value": int(df_keywords_detailed.iloc[i,1])})
        
    return data  