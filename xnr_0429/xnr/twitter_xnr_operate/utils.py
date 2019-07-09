#-*- coding:utf-8 -*-
import os
import time
import json
import sys
import random
import re

from xnr.global_config import S_DATE_TW,S_TYPE,S_DATE_BCI_TW,SYSTEM_START_DATE, R_BEGIN_TIME
from xnr.global_utils import es_xnr_2 as es,es_xnr, tw_xnr_index_name,tw_xnr_index_type,\
                    tw_xnr_timing_list_index_name, tw_xnr_timing_list_index_type,\
                    tw_xnr_retweet_timing_list_index_name, tw_xnr_retweet_timing_list_index_type,\
                    twitter_flow_text_index_name_pre, twitter_flow_text_index_type,\
                    twitter_user_index_name, twitter_user_index_type, tw_social_sensing_index_name, \
                    tw_social_sensing_index_type, tw_hot_keyword_task_index_name, tw_hot_keyword_task_index_type,\
                    tw_hot_subopinion_results_index_name, tw_hot_subopinion_results_index_type, \
                    es_tw_user_portrait, tw_portrait_index_name, tw_portrait_index_type, \
                    tw_bci_index_name_pre, tw_bci_index_type,tw_xnr_fans_followers_index_name,\
                    tw_xnr_fans_followers_index_type, tw_be_retweet_index_name_pre, tw_be_retweet_index_type,\
                    twitter_feedback_at_index_name_pre, twitter_xnr_relations_index_name,twitter_xnr_relations_index_type, RE_QUEUE as ali_re, twitter_relation_params

from xnr_relations_utils import update_twitter_xnr_relations,load_twitter_user_passwd
from xnr.global_utils import twitter_xnr_save_like_index_name,twitter_xnr_save_like_index_type

from xnr.twitter_publish_func import tw_publish, tw_comment, tw_retweet, tw_follow, tw_unfollow, tw_like, tw_mention, tw_message
from xnr.utils import tw_uid2nick_name_photo,tw_xnr_user_no2uid
from parameter import topic_ch2en_dict, TOP_WEIBOS_LIMIT, HOT_EVENT_TOP_USER, HOT_AT_RECOMMEND_USER_TOP,\
                    BCI_USER_NUMBER, USER_POETRAIT_NUMBER, DAY
from time_utils import datetime2ts, ts2datetime

def get_submit_tweet_tw(task_detail):

    text = task_detail['text']
    tweet_type = task_detail['tweet_type']
    xnr_user_no = task_detail['xnr_user_no']

    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        mark = tw_publish(account_name, password, text, tweet_type, xnr_user_no)

    else:
        mark = False

    return mark

def tw_save_to_tweet_timing_list(task_detail):

    item_detail = dict()

    #item_detail['uid'] = task_detail['uid']
    item_detail['xnr_user_no'] = task_detail['xnr_user_no']
    item_detail['task_source'] = task_detail['tweet_type']
    #item_detail['operate_type'] = task_detail['operate_type']
    item_detail['create_time'] = task_detail['create_time']
    item_detail['post_time'] = task_detail['post_time']
    item_detail['text'] = task_detail['text']
    item_detail['task_status'] = task_detail['task_status'] # 0-尚未发送，1-已发送
    item_detail['remark'] = task_detail['remark']
    #item_detail['task_status'] = 0 

    task_id = task_detail['xnr_user_no'] + '_'+str(item_detail['create_time'])
    # task_id: uid_提交时间_发帖时间

    try:
        es.index(index=tw_xnr_timing_list_index_name,doc_type=tw_xnr_timing_list_index_type,id=task_id,body=item_detail)
        mark = True
    except:
        mark = False

    return mark
    

def get_recommend_at_user(xnr_user_no):
    #_id  = user_no2_id(user_no)
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    #print 'es_result:::',es_result
    if es_result:
        uid = es_result['uid']
        daily_interests = es_result['daily_interests']
    if S_TYPE == 'test':
        now_ts = datetime2ts(S_DATE_TW)    
    else:
        now_ts = int(time.time())
    datetime = ts2datetime(now_ts-24*3600)

    index_name = twitter_flow_text_index_name_pre + datetime
    nest_query_list = []
    daily_interests_list = daily_interests.split('&')

    es_results_daily = es.search(index=index_name,doc_type=twitter_flow_text_index_type,\
                        body={'query':{'match_all':{}},'size':200,\
                        'sort':{'timestamp':{'order':'desc'}}})['hits']['hits']

    uid_list = []
    if es_results_daily:
        for result in es_results_daily:
            result = result['_source']
            uid_list.append(result['uid'])

    ## 根据uid，从weibo_user中得到 nick_name
    uid_nick_name_dict = dict()  # uid不会变，而nick_name可能会变
    es_results_user = es.mget(index=twitter_user_index_name,doc_type=twitter_user_index_type,body={'ids':uid_list})['docs']
    i = 0
    for result in es_results_user:

        if result['found'] == True:
            result = result['_source']
            uid = result['uid']
            nick_name = result['name']
            if nick_name:
                i += 1
                uid_nick_name_dict[uid] = nick_name
        if i >= DAILY_AT_RECOMMEND_USER_TOP:
            break

    return uid_nick_name_dict

def get_daily_recommend_tweets(theme,sort_item):

    if S_TYPE == 'test':
        now_ts = datetime2ts(S_DATE_TW)    
    else:
        now_ts = int(time.time())

    datetime = ts2datetime(now_ts)

    index_name = daily_interest_index_name_pre +'_'+ datetime

    theme_en = daily_ch2en[theme]
    es_results = es_xnr.get(index=index_name,doc_type=daily_interest_index_type,id=theme_en)['_source']
    content = json.loads(es_results['content'])

    results_all = []
    for result in content:
        #result = result['_source']
        uid = result['uid']
        nick_name,photo_url = tw_uid2nick_name_photo(uid)
        result['nick_name'] = nick_name
        result['photo_url'] = photo_url
        results_all.append(result)
    return results_all


def get_hot_sensitive_recommend_at_user(sort_item):

    if S_TYPE == 'test':
        now_ts = datetime2ts(S_DATE_TW)    
    else:
        now_ts = int(time.time())
    datetime = ts2datetime(now_ts-24*3600)

    #sort_item = 'sensitive'
    sort_item_2 = 'timestamp'

    index_name = twitter_flow_text_index_name_pre + datetime

    query_body = {
        'query':{
            'match_all':{}
        },
        'sort':{sort_item:{'order':'desc'}},
        'size':HOT_EVENT_TOP_USER,
        '_source':['uid','user_fansnum','retweeted','timestamp']
    }

    es_results = es.search(index=index_name,doc_type=twitter_flow_text_index_type,body=query_body)['hits']['hits']
    
    uid_fansnum_dict = dict()
    if es_results:
        for result in es_results:
            result = result['_source']
            uid = result['uid']
            uid_fansnum_dict[uid] = {}
            uid_fansnum_dict[uid][sort_item_2] = result[sort_item_2]

    uid_fansnum_dict_sort_top = sorted(uid_fansnum_dict.items(),key=lambda x:x[1][sort_item_2],reverse=True)

    uid_set = set()

    for item in uid_fansnum_dict_sort_top:
        uid_set.add(item[0])

    uid_list = list(uid_set)


    ## 根据uid，从weibo_user中得到 nick_name
    uid_nick_name_dict = dict()  # uid不会变，而nick_name可能会变
    es_results_user = es.mget(index=twitter_user_index_name,doc_type=twitter_user_index_type,body={'ids':uid_list})['docs']
    i = 0
    for result in es_results_user:
        if result['found'] == True:
            result = result['_source']
            uid = result['uid']
            nick_name = result['username']
            if nick_name:
                i += 1
                uid_nick_name_dict[uid] = nick_name
        if i >= HOT_AT_RECOMMEND_USER_TOP:
            break

    return uid_nick_name_dict

def get_hot_recommend_tweets(xnr_user_no,topic_field,sort_item):

    topic_field_en = topic_ch2en_dict[topic_field]

    if sort_item != 'compute_status':
        query_body = {
            'query':{
                'bool':{
                    'must':[
                        {
                            'filtered':{
                                'filter':{
                                    'term':{'topic_field':topic_field_en}
                                }
                            }
                        }
                    ]
                }
                
            },
            'sort':{sort_item:{'order':'desc'}},
            'size':TOP_WEIBOS_LIMIT
        }

        current_time = time.time()

        if S_TYPE == 'test':
            current_time = datetime2ts('2017-10-25')
        #tw_social_sensing_index_name = tw_social_sensing_index_name_pre + ts2datetime(current_time)

        es_results = es.search(index=tw_social_sensing_index_name,doc_type=tw_social_sensing_index_type,body=query_body)['hits']['hits']

        if not es_results:    
            es_results = es.search(index=tw_social_sensing_index_name,doc_type=tw_social_sensing_index_type,\
                                    body={'query':{'match_all':{}},'size':TOP_WEIBOS_LIMIT,\
                                    'sort':{sort_item:{'order':'desc'}}})['hits']['hits']
    results_all = []
    for result in es_results:
        result = result['_source']
        uid = result['uid']
        nick_name,photo_url = tw_uid2nick_name_photo(uid)
        result['nick_name'] = nick_name
        result['photo_url'] = photo_url
        results_all.append(result)
    return results_all

def push_keywords_task(task_detail):

    #print 'task_detail::',task_detail

    try:
        item_dict = {}
        item_dict['task_id'] = task_detail['task_id']
        item_dict['xnr_user_no'] = task_detail['xnr_user_no']
        keywords_string = '&'.join(task_detail['keywords_string'].encode('utf-8').split('，'))
        item_dict['keywords_string'] = keywords_string
        item_dict['compute_status'] = task_detail['compute_status']
        item_dict['submit_time'] = task_detail['submit_time']
        item_dict['submit_user'] = task_detail['submit_user']
        _id = item_dict['xnr_user_no']+'_'+task_detail['task_id']
        es.index(index=tw_hot_keyword_task_index_name,doc_type=tw_hot_keyword_task_index_type,\
                id=_id,body=item_dict)
        mark = True
    except:
        mark = False

    return mark    

def get_hot_subopinion(xnr_user_no,task_id):
    
    task_id_new = xnr_user_no+'_'+task_id
    es_task = []
    try:
        es_task = es.get(index=tw_hot_keyword_task_index_name,doc_type=tw_hot_keyword_task_index_type,\
                    id=task_id_new)['_source']
    except:
        return '尚未提交计算'

    if es_task:
        if es_task['compute_status'] != 2:
            return '正在计算'
        else:
            es_result = es.get(index=tw_hot_subopinion_results_index_name,doc_type=tw_hot_subopinion_results_index_type,\
                                id=task_id_new)['_source']

            if es_result:
                contents = json.loads(es_result['subopinion_tw'])
            
                return contents    

def get_bussiness_recomment_tweets(xnr_user_no,sort_item):
    
    get_results = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    
    monitor_keywords = get_results['monitor_keywords']
    monitor_keywords_list = monitor_keywords.split(',')
    
    if sort_item == 'timestamp':
        sort_item_new = 'timestamp'
        es_results = get_tweets_from_flow(monitor_keywords_list,sort_item_new)
    elif sort_item == 'sensitive_info':
        sort_item_new = 'sensitive'
        es_results = get_tweets_from_flow(monitor_keywords_list,sort_item_new)
    elif sort_item == 'sensitive_user':
        sort_item_new = 'sensitive'
        es_results = get_tweets_from_user_portrait(monitor_keywords_list,sort_item_new)  
    elif sort_item == 'influence_info':
        sort_item_new = 'share'
        es_results = get_tweets_from_flow(monitor_keywords_list,sort_item_new)
    elif sort_item == 'influence_user':
        sort_item_new = 'influence'
        es_results = get_tweets_from_bci(monitor_keywords_list,sort_item_new)
        
    return es_results            

def get_tweets_from_flow(monitor_keywords_list,sort_item_new):

    nest_query_list = []
    for monitor_keyword in monitor_keywords_list:
        nest_query_list.append({'wildcard':{'keywords_string':'*'+monitor_keyword+'*'}})

    query_body = {
        'query':{
            'bool':{
                'should':nest_query_list
            }  
        },
        'sort':[{sort_item_new:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'size':TOP_WEIBOS_LIMIT
    }

    if S_TYPE == 'test':
        now_ts = datetime2ts('2017-10-25')    
    else:
        now_ts = int(time.time())
    datetime = ts2datetime(now_ts-24*3600)

    index_name = twitter_flow_text_index_name_pre + datetime

    es_results = es.search(index=index_name,doc_type=twitter_flow_text_index_type,body=query_body)['hits']['hits']

    if not es_results:
        es_results = es.search(index=index_name,doc_type=twitter_flow_text_index_type,\
                                body={'query':{'match_all':{}},'size':TOP_WEIBOS_LIMIT,\
                                'sort':{sort_item_new:{'order':'desc'}}})['hits']['hits']
    results_all = []
    for result in es_results:
        result = result['_source']
        uid = result['uid']
        nick_name,photo_url = tw_uid2nick_name_photo(uid)
        result['nick_name'] = nick_name
        result['photo_url'] = photo_url
        results_all.append(result)
    return results_all    

def get_tweets_from_user_portrait(monitor_keywords_list,sort_item_new):

    query_body = {
        'query':{
            'match_all':{}
        },
        'sort':{sort_item_new:{'order':'desc'}},
        'size':USER_POETRAIT_NUMBER
    }
    #print 'query_body:::',query_body
    es_results_portrait = es_tw_user_portrait.search(index=tw_portrait_index_name,doc_type=tw_portrait_index_type,body=query_body)['hits']['hits']

    uid_set = set()

    if es_results_portrait:
        for result in es_results_portrait:
            uid = result['_id']
            # result = result['_source']
            # uid = result['uid']
            uid_set.add(uid)
    uid_list = list(uid_set)

    es_results = uid_lists2tw_from_flow_text(monitor_keywords_list,uid_list)
    
    return es_results    


def uid_lists2tw_from_flow_text(monitor_keywords_list,uid_list):

    nest_query_list = []
    for monitor_keyword in monitor_keywords_list:
        nest_query_list.append({'wildcard':{'keywords_string':'*'+monitor_keyword+'*'}})

    query_body = {
        'query':{
            'bool':{
                'should':nest_query_list,
                'must':[
                    {'terms':{'uid':uid_list}}
                ]
            }  
            
        },
        'size':TOP_WEIBOS_LIMIT,
        'sort':{'timestamp':{'order':'desc'}}
    }

    if S_TYPE == 'test':
        now_ts = datetime2ts(S_DATE_TW)    
    else:
        now_ts = int(time.time())
    datetime = ts2datetime(now_ts-24*3600)

    index_name_flow = twitter_flow_text_index_name_pre + datetime

    es_results = es.search(index=index_name_flow,doc_type=twitter_flow_text_index_type,body=query_body)['hits']['hits']

    results_all = []
    for result in es_results:
        result = result['_source']
        uid = result['uid']
        nick_name,photo_url = tw_uid2nick_name_photo(uid)
        result['nick_name'] = nick_name
        result['photo_url'] = photo_url
        results_all.append(result)
    return results_all


def get_tweets_from_bci(monitor_keywords_list,sort_item_new):

    if S_TYPE == 'test':
        now_ts = datetime2ts(S_DATE_BCI_TW)    
    else:
        now_ts = int(time.time())

    datetime = ts2datetime(now_ts-24*3600)
    # datetime_new = datetime[0:4]+datetime[5:7]+datetime[8:10]
    datetime_new = datetime

    index_name = tw_bci_index_name_pre + datetime_new

    query_body = {
        'query':{
            'match_all':{}
        },
        'sort':{sort_item_new:{'order':'desc'}},
        'size':BCI_USER_NUMBER
    }

    es_results_bci = es.search(index=index_name,doc_type=tw_bci_index_type,body=query_body)['hits']['hits']
    #print 'es_results_bci::',es_results_bci
    #print 'index_name::',index_name
    #print ''
    uid_set = set()

    if es_results_bci:
        for result in es_results_bci:
            uid = result['_id']
            uid_set.add(uid)
    uid_list = list(uid_set)

    es_results = uid_lists2tw_from_flow_text(monitor_keywords_list,uid_list)

    return es_results


def get_comment_operate_tw(task_detail):

    text = task_detail['text']
    tweet_type = task_detail['tweet_type']
    xnr_user_no = task_detail['xnr_user_no']
    _id = task_detail['r_fid']
    #_id = ??????
    uid = task_detail['r_uid']
    #nick_name = task_detail['nick_name']

    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        print '123'
        mark = tw_comment(account_name, password, _id, uid, text, tweet_type, xnr_user_no)
    else:
        mark = False

    return mark

def get_retweet_operate_tw(task_detail):

    text = task_detail['text']
    tweet_type = task_detail['tweet_type']
    xnr_user_no = task_detail['xnr_user_no']
    _id = task_detail['r_fid']
    #_id = ??????
    uid = task_detail['r_uid']

    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        mark = tw_retweet(account_name, password, _id, uid, text, tweet_type, xnr_user_no)

    else:
        mark = False

    return mark


def get_at_operate_tw(task_detail):
    
    text = task_detail['text']
    tweet_type = task_detail['tweet_type']
    xnr_user_no = task_detail['xnr_user_no']
    # user_name = task_detail['nick_name']

    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        mark = tw_mention(account_name,password, text, xnr_user_no, tweet_type)

    else:
        mark = False

    return mark

def get_like_operate_tw(task_detail):

    xnr_user_no = task_detail['xnr_user_no']
    _id = task_detail['r_fid']
    #_id = ??????
    #uid = task_detail['r_uid']

    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        mark = tw_like(account_name,password, _id)

    else:
        mark = False

    return mark

def get_follow_operate_tw(task_detail):

    trace_type = task_detail['trace_type']
    xnr_user_no = task_detail['xnr_user_no']
    #nick_name = task_detail['nick_name']
    uid = task_detail['uid']


    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        mark = tw_follow(account_name, password, uid, xnr_user_no, trace_type)

    else:
        mark = False

    return mark

def get_unfollow_operate_tw(task_detail):

    xnr_user_no = task_detail['xnr_user_no']
    uid = task_detail['uid']

    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        mark = tw_unfollow(account_name, password, uid, xnr_user_no)

    else:
        mark = False

    return mark


def get_private_operate_tw(task_detail):

    xnr_user_no = task_detail['xnr_user_no']
    text = task_detail['text']
    uid = task_detail['uid']

    es_xnr_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']

    tw_mail_account = es_xnr_result['tw_mail_account']
    tw_phone_account = es_xnr_result['tw_phone_account']
    password = es_xnr_result['password']

    if tw_phone_account:
        account_name = tw_phone_account
    elif tw_mail_account:
        account_name = tw_mail_account
    else:
        account_name = False

    if account_name:
        mark = tw_message(account_name, password,  text, uid)

    else:
        mark = False

    return mark

def get_show_retweet_timing_list(xnr_user_no,start_ts,end_ts):

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'xnr_user_no':xnr_user_no}},
                    {'range':{'timestamp_set':{'gte':start_ts,'lt':end_ts}}}
                ]
            }
        },
        'size':MAX_SEARCH_SIZE,
        'sort':[
            {'compute_status':{'order':'asc'}},   
            {'timestamp_set':{'order':'desc'}}
        ]
    }
    
    results = es.search(index=tw_xnr_retweet_timing_list_index_name,\
        doc_type=tw_xnr_retweet_timing_list_index_type,body=query_body)['hits']['hits']

    result_all = []
    # print 'results:::',results
    for result in results:
        result = result['_source']
        result_all.append(result)

    return result_alls


def get_show_retweet_timing_list_future(xnr_user_no):

    start_ts = int(time.time())

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'xnr_user_no':xnr_user_no}},
                    {'range':{'timestamp_set':{'gte':start_ts}}}
                ]
            }
        },
        'size':MAX_SEARCH_SIZE,
        'sort':[
            {'compute_status':{'order':'asc'}},   
            {'timestamp_set':{'order':'desc'}}
        ]
    }
    # print 'query_body!!',query_body
    results = es.search(index=tw_xnr_retweet_timing_list_index_name,\
        doc_type=tw_xnr_retweet_timing_list_index_type,body=query_body)['hits']['hits']

    result_all = []

    for result in results:
        result = result['_source']
        result_all.append(result)

    return result_all



def get_show_trace_followers(xnr_user_no):
    # kn 2019-06-28 新的查询关系
    results = []
    query_body = {
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term': {'xnr_no': xnr_user_no}},
                            {'term': {'gensuiguanzhu': 1}}
                        ]
                    }
                }
            }
        },
        'size': MAX_SEARCH_SIZE,
    }
    search_results = es.search(index=twitter_xnr_relations_index_name, doc_type=twitter_xnr_relations_index_type, body=query_body)['hits']['hits']
    print search_results
    for data in search_results:
        data = data['_source']
        r = {
            'uid': data.get('uid', ''),
            'nick_name': data.get('nickname', ''),
            'fansnum': data.get('fensi_num', 0),
            'follownum': data.get('guanzhu_num', 0),
            'sex': data.get('sex', 'unknown'),
            'photo_url': data.get('photo_url', ''),
            'statusnum': 0,
            'user_location': data.get('geo', ''),
        }
        results.append(r)
    return results

    """ 
    # kn 旧的查询关系注销
    try: 
        es_get_result = es.get(index=tw_xnr_fans_followers_index_name,doc_type=tw_xnr_fans_followers_index_type,\
                    id=xnr_user_no)['_source']

        trace_follow_list = es_get_result['trace_follow_list']
    except:
		trace_follow_list = []

    weibo_user_info = []

    if trace_follow_list:
        mget_results = es.mget(index=twitter_user_index_name,doc_type=twitter_user_index_type,\
                            body={'ids':trace_follow_list})['docs']
        # print 'mget_results::',mget_results
        for result in mget_results:
            if result['found']:
                weibo_user_info.append(result['_source'])
            else:
                uid = result['_id']

                weibo_user_info.append({'uid':uid,'statusnum':0,'fansnum':0,'friendsnum':0,'photo_url':'','sex':'','nick_name':uid,'user_location':''})
    else:
        weibo_user_info = []

    return weibo_user_info
    """


def get_trace_follow_operate(xnr_user_no,uid_string,nick_name_string):
    root_uid = tw_xnr_user_no2uid(xnr_user_no)
    if uid_string:
        print 'uid--------------------------------------'
        uid_list = uid_string.encode('utf-8').split('，')
        tw_account, tw_password = load_twitter_user_passwd(root_uid)
        for uid in uid_list:
            data = {}
            data['platform'] = 'twitter'
            data['xnr_no'] = xnr_user_no
            data['xnr_uid'] = root_uid
            data['uid'] = uid
            data['account'] = tw_account
            data['password'] = tw_password
            data['screen_name'] = ''
            data['gensuiguanzhu'] = 1
            data['pingtaiguanzhu'] = 1
            data['operate_type'] = 'follow'
            # push
            ali_re.lpush(twitter_relation_params, json.dumps(data))
            print 'push aliyun successful'
            #if not update_twitter_xnr_relations(root_uid, uid, {'gensuiguanzhu': 1, 'pingtaiguanzhu':1}):
                #return False
    elif nick_name_string:
        print 'nick_name--------------------------------------'
        screen_name_list = nick_name_string.encode('utf-8').split('，')
        tw_account, tw_password = load_twitter_user_passwd(root_uid)
        for screen_name in screen_name_list:
            data = {}
            data['platform'] = 'twitter'
            data['xnr_no'] = xnr_user_no
            data['xnr_uid'] = root_uid
            data['uid'] = ''
            data['account'] = tw_account
            data['password'] = tw_password
            data['screen_name'] = screen_name
            data['gensuiguanzhu'] = 1
            data['pingtaiguanzhu'] = 1
            data['operate_type'] = 'follow'
            # push
            ali_re.lpush(twitter_relation_params, json.dumps(data))
            print 'push aliyun successful'
            #if not update_twitter_xnr_relations(root_uid, uid, {'gensuiguanzhu': 1, 'pingtaiguanzhu':1}):
                #return False
    return True


"""
    # kn 2019-6-28 注销 使用简单的关注关系
    mark = False
    fail_nick_name_list = []
    if uid_string:
        uid_list = uid_string.encode('utf-8').split('，')
        
    elif nick_name_string:
        nick_name_list = nick_name_string.encode('utf-8').split('，')
        uid_list = []
        
        for nick_name in nick_name_list:
            query_body = {
                'query':{
                    'filtered':{
                        'filter':{
                            'term':{'nick_name':nick_name}
                        }
                    }
                },
                '_source':['uid']
            }
            try:
                uid_results = es.search(index=twitter_user_index_name,doc_type=twitter_user_index_type,\
                            body=query_body)['hits']['hits']
                
                uid_result = uid_result[0]['_source']
                uid = uid_result['uid']
                uid_list.append(uid)

            except:
                fail_nick_name_list.append(nick_name)

    try:
        result = es.get(index=tw_xnr_fans_followers_index_name,doc_type=tw_xnr_fans_followers_index_type,\
                        id=xnr_user_no)['_source']

        try:
            trace_follow_list = result['trace_follow_list']
        except:
            trace_follow_list = []

        try:
            followers_list = result['followers_list']
        except:
            followers_list = []

        trace_follow_list = list(set(trace_follow_list) | set(uid_list))

        followers_list = list(set(followers_list)|set(uid_list))

        es.update(index=tw_xnr_fans_followers_index_name,doc_type=tw_xnr_fans_followers_index_type,\
                    id=xnr_user_no,body={'doc':{'trace_follow_list':trace_follow_list,'followers_list':followers_list}})

        mark = True
    
    except:

        item_exists = {}

        item_exists['xnr_user_no'] = xnr_user_no
        item_exists['trace_follow_list'] = uid_list
        item_exists['followers_list'] = uid_list

        es.index(index=tw_xnr_fans_followers_index_name,doc_type=tw_xnr_fans_followers_index_type,\
                    id=xnr_user_no,body=item_exists)

        mark = True

    return [mark,fail_nick_name_list]    

"""

def get_un_trace_follow_operate(xnr_user_no,uid_string,nick_name_string):
    # 新的取消跟随关注的逻辑 kn 2019-06-28
    root_uid = tw_xnr_user_no2uid(xnr_user_no)
    if uid_string:
        print 'uid--------------------------------------'
        uid_list = uid_string.encode('utf-8').split('，')
        for uid in uid_list:
            if not update_twitter_xnr_relations(root_uid, uid, {'gensuiguanzhu': 0, 'pingtaiguanzhu':0}):
                return False
    elif nick_name_string:
        print 'nick_name--------------------------------------'
        uid_list = nick_name_string.encode('utf-8').split('，')
        for uid in uid_list:
            if not update_twitter_xnr_relations(root_uid, uid, {'gensuiguanzhu': 0, 'pingtaiguanzhu':0}):
                return False
    return True
 
    """
    kn 注掉原来的取消关注逻辑
    mark = False
    fail_nick_name_list = []
    fail_uids = []

    if uid_string:
        uid_list = uid_string.encode('utf-8').split('，')
        
    elif nick_name_string:
        nick_name_list = nick_name_string.encode('utf-8').split('，')
        uid_list = []
        
        for nick_name in nick_name_list:
            query_body = {
                'query':{
                    'filtered':{
                        'filter':{
                            'term':{'nick_name':nick_name}
                        }
                    }
                },
                '_source':['uid']
            }
            try:
                uid_results = es.search(index=twitter_user_index_name,doc_type=twitter_user_index_type,\
                            body=query_body)['hits']['hits']
                
                uid_result = uid_result[0]['_source']
                uid = uid_result['uid']
                uid_list.append(uid)

            except:
                fail_nick_name_list.append(nick_name)

    try:
        result = es.get(index=tw_xnr_fans_followers_index_name,doc_type=tw_xnr_fans_followers_index_type,\
                            id=xnr_user_no)['_source']
        
        trace_follow_list = result['trace_follow_list']

        # 共同uids
        comment_uids = list(set(trace_follow_list).intersection(set(uid_list)))

        # 取消失败uid
        fail_uids = list(set(comment_uids).difference(set(uid_list)))

        # 求差
        trace_follow_list = list(set(trace_follow_list).difference(set(uid_list))) 


        es.update(index=tw_xnr_fans_followers_index_name,doc_type=tw_xnr_fans_followers_index_type,\
                            id=xnr_user_no,body={'doc':{'trace_follow_list':trace_follow_list}})

        mark = True
    except:
        mark = False

    return [mark,fail_uids,fail_nick_name_list]    
    """



#####################################################################
##########################韩梦成负责以下内容###########################
#####################################################################
from xnr.global_utils import twitter_feedback_comment_index_name, twitter_feedback_comment_index_type,\
                            twitter_feedback_retweet_index_name, twitter_feedback_retweet_index_type,\
                            twitter_feedback_private_index_name, twitter_feedback_private_index_type,\
                            twitter_feedback_at_index_name, twitter_feedback_at_index_type,\
                            twitter_feedback_fans_index_name, twitter_feedback_fans_index_type,\
                            twitter_feedback_follow_index_name, twitter_feedback_follow_index_type,\
                            twitter_feedback_like_index_name, twitter_feedback_like_index_type
from xnr.time_utils import get_timeset_indexset_list, tw_get_flow_text_index_list as get_flow_text_index_list
from xnr.utils import judge_tw_follow_type, judge_tw_sensing_sensor
from xnr.parameter import TOP_ACTIVE_SOCIAL, MAX_SEARCH_SIZE
trans_path = os.path.join(os.path.abspath(os.getcwd()), 'xnr/cron/trans/')
sys.path.append(trans_path)
from trans_v2 import trans, simplified2traditional

def get_show_comment(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    start_ts = int(task_detail['start_ts'])
    end_ts = int(task_detail['end_ts'])

    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']
    print 'uid'
    print uid
    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'term':{'comment_type':'receive'}}
                ]
            }
        },
        'sort':[{sort_item:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'size':MAX_SEARCH_SIZE
    }
    
    if start_ts < datetime2ts(SYSTEM_START_DATE):
        start_ts = datetime2ts(SYSTEM_START_DATE)

    index_name_pre = twitter_feedback_comment_index_name + '_'
    index_name_list = get_timeset_indexset_list(index_name_pre,ts2datetime(start_ts),ts2datetime(end_ts))
    results_all = []
    for index_name in index_name_list:
        try:
            es_results = es.search(index=index_name,doc_type=twitter_feedback_comment_index_type,\
                                body=query_body)['hits']['hits']
            if es_results:
                for item in es_results:
                    results_all.append(item['_source'])
        except Exception,e:
            # print e
            pass
    return results_all

def get_show_retweet(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    start_ts = int(task_detail['start_ts'])
    end_ts = int(task_detail['end_ts'])
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}}
                ]
            }
        },
        'sort':[{sort_item:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'size':MAX_SEARCH_SIZE
    }

    if start_ts < datetime2ts(SYSTEM_START_DATE):
        start_ts = datetime2ts(SYSTEM_START_DATE)

    index_name_pre = twitter_feedback_retweet_index_name + '_'

    index_name_list = get_timeset_indexset_list(index_name_pre,ts2datetime(start_ts),ts2datetime(end_ts))
    results_all = []
    for index_name in index_name_list:
        try:
            es_results = es.search(index=index_name,doc_type=twitter_feedback_retweet_index_type,\
                                body=query_body)['hits']['hits']
            if es_results:
                for item in es_results:
                    results_all.append(item['_source'])
        except Exception,e:
            # print e
            pass
    return results_all

def get_show_private(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    start_ts = int(task_detail['start_ts'])
    end_ts = int(task_detail['end_ts'])
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'term':{'private_type':'receive'}}
                ],
            }
        },
        'sort':[{sort_item:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'size':MAX_SEARCH_SIZE
    }
  
    if start_ts < datetime2ts(SYSTEM_START_DATE):
        start_ts = datetime2ts(SYSTEM_START_DATE)

    index_name_pre = twitter_feedback_private_index_name + '_'
    index_name_list = get_timeset_indexset_list(index_name_pre,ts2datetime(start_ts),ts2datetime(end_ts))
    results_all = []
    for index_name in index_name_list:
        try:
            es_results = es.search(index=index_name,doc_type=twitter_feedback_private_index_type,\
                                body=query_body)['hits']['hits']
            if es_results:
                for item in es_results:
                    results_all.append(item['_source'])
        except Exception,e:
            # print e
            pass
    return results_all

def get_show_at(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    start_ts = int(task_detail['start_ts'])
    end_ts = int(task_detail['end_ts'])
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']
    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'range':{'timestamp':{'gte':start_ts,'lt':end_ts}}}
                ]
            }
        },
        'sort':[{sort_item:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'size':MAX_SEARCH_SIZE
    }
    '''
    if start_ts < datetime2ts(SYSTEM_START_DATE):
        start_ts = datetime2ts(SYSTEM_START_DATE)

    index_name_pre = twitter_feedback_at_index_name + '_'

    index_name_list = get_timeset_indexset_list(index_name_pre,ts2datetime(start_ts),ts2datetime(end_ts))
    results_all = []
    for index_name in index_name_list:
        try:
            es_results = es.search(index=index_name,doc_type=twitter_feedback_at_index_type,\
                                body=query_body)['hits']['hits']
            if es_results:
                for item in es_results:
                    results_all.append(item['_source'])
        except Exception,e:
            # print e
            pass
    return results_all
    '''
    print query_body
    index_name = twitter_feedback_at_index_name_pre + '*'
    es_results = es.search(index=index_name, doc_type=twitter_feedback_at_index_type, body=query_body)['hits']['hits']
    return [item['_source'] for item in es_results]


def get_show_fans(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    start_ts = int(task_detail['start_ts'])
    end_ts = int(task_detail['end_ts'])
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'range':{'timestamp':{'gte':start_ts,'lt':end_ts}}}
                ]
            }
        },
        # 'sort':[{sort_item:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'sort':[{sort_item:{'order':'desc'}},{'update_time':{'order':'desc'}}],
        'size':MAX_SEARCH_SIZE
    }
    uid_list = []
    results_all = []
    try:
        es_results = es.search(index=twitter_feedback_fans_index_name,doc_type=twitter_feedback_fans_index_type,\
                            body=query_body)['hits']['hits']
        if es_results:
            for item in es_results:
                uid = item['_source']['uid']
                if not uid in uid_list:
                    uid_list.append(uid)
                    results_all.append(item['_source'])
    except Exception,e:
        # print e
        pass
    return results_all

def get_show_follow(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    start_ts = int(task_detail['start_ts'])
    end_ts = int(task_detail['end_ts'])
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'range':{'timestamp':{'gte':start_ts,'lt':end_ts}}}
                ]
            }
        },
        # 'sort':[{sort_item:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'sort':[{sort_item:{'order':'desc'}},{'update_time':{'order':'desc'}}],
        'size':MAX_SEARCH_SIZE
    }
    results_all = []
    uid_list = []
    try:
        es_results = es.search(index=twitter_feedback_follow_index_name,doc_type=twitter_feedback_follow_index_type,\
                            body=query_body)['hits']['hits']
        if es_results:
            for item in es_results:
                uid = item['_source']['uid']
                if not uid in uid_list:
                    uid_list.append(uid)
                    results_all.append(item['_source'])
    except Exception,e:
        # print e
        pass
    return results_all
    
def get_show_like(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    start_ts = int(task_detail['start_ts'])
    end_ts = int(task_detail['end_ts'])
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']
    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'range':{'timestamp':{'gte':start_ts,'lt':end_ts}}}
                ]
            }
        },
        'sort':[{sort_item:{'order':'desc'}},{'timestamp':{'order':'desc'}}],
        'size':MAX_SEARCH_SIZE
    }
        
    if start_ts < datetime2ts(SYSTEM_START_DATE):
        start_ts = datetime2ts(SYSTEM_START_DATE)

    index_name_pre = twitter_feedback_like_index_name + '_'

    index_name_list = get_timeset_indexset_list(index_name_pre,ts2datetime(start_ts),ts2datetime(end_ts))
    results_all = []
    for index_name in index_name_list:
        try:
            es_results = es.search(index=index_name,doc_type=twitter_feedback_like_index_type,\
                                body=query_body)['hits']['hits']
            if es_results:
                for item in es_results:
                    results_all.append(item['_source'])
        except Exception,e:
            # print e
            pass
    return results_all

# 主动社交-直接搜索
def get_direct_search(task_detail):
    return_results_all = []
    xnr_user_no = task_detail['xnr_user_no']
    uid_list = task_detail['uid_list']
    for uid in uid_list:
        query_body = {
            'query':{
                'filtered':{
                    'filter':{
                        'term':{'uid':uid}
                    }
                }
            }
        }
        es_results = es.search(index=tw_portrait_index_name,doc_type=tw_portrait_index_type,body=query_body)['hits']['hits']
        if es_results:
            for item in es_results:
                uid = item['_source']['uid']
                nick_name,photo_url = tw_uid2nick_name_photo(uid)
                item['_source']['nick_name'] = nick_name
                item['_source']['photo_url'] = photo_url
                tw_type = judge_tw_follow_type(xnr_user_no,uid)
                sensor_mark = judge_tw_sensing_sensor(xnr_user_no,uid)

                item['_source']['tw_type'] = tw_type
                item['_source']['sensor_mark'] = sensor_mark

            
                if S_TYPE == 'test':
                    current_time = datetime2ts(S_DATE_TW)
                else:
                    current_time = int(time.time())

                index_name = get_flow_text_index_list(current_time)

                query_body = {
                    'query':{
                        'bool':{
                            'must':[
                                {'term':{'uid':uid}},
                                # {'terms':{'message_type':[1,3]}}
                            ]
                        }
                    },
                    # 'sort':{'retweeted':{'order':'desc'}}
                }

                es_tw_results = es.search(index=index_name,doc_type=twitter_flow_text_index_type,body=query_body)['hits']['hits']

                tw_list = []
                for tw in es_tw_results:
                    tw = tw['_source']
                    tw_list.append(tw)
                item['_source']['tw_list'] = tw_list
                item['_source']['portrait_status'] = True
                return_results_all.append(item['_source'])
        else:
            item_else = dict()
            item_else['uid'] = uid
            nick_name,photo_url = tw_uid2nick_name_photo(uid)
            item_else['nick_name'] = nick_name
            item_else['photo_url'] = photo_url
            tw_type = judge_tw_follow_type(xnr_user_no,uid)
            sensor_mark = judge_tw_sensing_sensor(xnr_user_no,uid)
            item_else['tw_type'] = tw_type
            item_else['sensor_mark'] = sensor_mark
            item_else['portrait_status'] = False
          
            if S_TYPE == 'test':
                current_time = datetime2ts(S_DATE_TW)
            else:
                current_time = int(time.time())

            index_name = get_flow_text_index_list(current_time)

            query_body = {
                'query':{
                    'term':{'uid':uid}
                },
                # 'sort':{'retweeted':{'order':'desc'}}
            }

            es_tw_results = es.search(index=index_name,doc_type=twitter_flow_text_index_type,body=query_body)['hits']['hits']

            tw_list = []
            for tw in es_tw_results:
                item_else['user_fansnum'] = tw['_source']['user_fansnum']
                tw = tw['_source']
                tw_list.append(tw)
            item_else['tw_list'] = tw_list
            return_results_all.append(item_else)
    return return_results_all

begin_ts = datetime2ts(R_BEGIN_TIME)

#use to get db_number which is needed to es
def get_db_num(timestamp):
    date = ts2datetime(timestamp)
    date_ts = datetime2ts(date)
    db_number = 2 - (((date_ts - begin_ts) / (DAY * 7))) % 2
    #run_type
    if S_TYPE == 'test':
        db_number = 1
    return db_number

def xnr_user_no2uid(xnr_user_no):
    try:
        result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
        uid = result['uid']
    except:
        uid = ''
    return uid

## 主动社交- 相关推荐
def get_related_recommendation(task_detail):
    avg_sort_uid_dict = {}
    xnr_user_no = task_detail['xnr_user_no']
    sort_item = task_detail['sort_item']
    es_result = es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']
    monitor_keywords = es_result['monitor_keywords']
    monitor_keywords_list = monitor_keywords.split(',')


    ## 监测词关注
    nest_query_list = []
    #文本中可能存在英文或者繁体字，所以都匹配一下
    monitor_en_keywords_list = trans(monitor_keywords_list, target_language='en')
    for i in range(len(monitor_keywords_list)):
        monitor_keyword = monitor_keywords_list[i]
        monitor_traditional_keyword = simplified2traditional(monitor_keyword)
        
        if len(monitor_en_keywords_list) == len(monitor_keywords_list): #确保翻译没出错
            monitor_en_keyword = monitor_en_keywords_list[i]
            nest_query_list.append({'wildcard':{'keywords_string':'*'+monitor_en_keyword+'*'}})
        
        nest_query_list.append({'wildcard':{'keywords_string':'*'+monitor_keyword+'*'}})
        nest_query_list.append({'wildcard':{'keywords_string':'*'+monitor_traditional_keyword+'*'}})

    # recommend_list_r = es.get(index=tw_xnr_fans_followers_index_name,doc_type=tw_xnr_fans_followers_index_type,id=xnr_user_no)['_source']

    #弃用，改用转发网络
    # recommend_list = []
    # if recommend_list_r.has_key('followers_list'):
    #     recommend_list = recommend_list_r['followers_list']
    # recommend_set_list = list(set(recommend_list))
    #转发网络
    now_ts = time.time()
    now_date_ts = datetime2ts(ts2datetime(now_ts))
    #get redis db number
    db_number = get_db_num(now_date_ts)
    tw_be_retweet_index_name = tw_be_retweet_index_name_pre +str(db_number)
    try:
        recommend_list_r = es.get(index=tw_be_retweet_index_name,doc_type=tw_be_retweet_index_type,id=xnr_user_no2uid(xnr_user_no))['_source']
        recommend_list = []
        if recommend_list_r.has_key('uid_be_retweet'):
            recommend_list = recommend_list_r['uid_be_retweet']
        recommend_set_list = list(set(recommend_list))
    except Exception,e:
        print e
        recommend_set_list = []


    if S_TYPE == 'test':
        current_date = S_DATE_TW
    else:
        current_date = int(time.time()-24*3600)
    flow_text_index_name = twitter_flow_text_index_name_pre + current_date
    if sort_item != 'friend':
        uid_list = []
        if sort_item == 'influence':
            # sort_item = 'user_fansnum'
            sort_item = 'share'
        query_body_rec = {
            'query':{
                'bool':{
                    'should':nest_query_list
                }
            },
            'aggs':{
                'uid_list':{
                    'terms':{'field':'uid','size':TOP_ACTIVE_SOCIAL,'order':{'avg_sort':'desc'} },
                    'aggs':{'avg_sort':{'avg':{'field':sort_item}}}
                }
            }
        }

        es_rec_result = es.search(index=flow_text_index_name,doc_type='text',body=query_body_rec)['aggregations']['uid_list']['buckets']
  
        for item in es_rec_result:
            uid = item['key']
            uid_list.append(uid)
            
            avg_sort_uid_dict[uid] = {}

            # if sort_item == 'user_fansnum':
            if sort_item == 'share':
                avg_sort_uid_dict[uid]['sort_item_value'] = int(item['avg_sort']['value'])
            else:
                avg_sort_uid_dict[uid]['sort_item_value'] = round(item['avg_sort']['value'],2)

    else:
        if S_TYPE == 'test':
            # uid_list = FRIEND_LIST
            uid_list = [] 
        else:
            uid_list = []

            #弃用，改用转发网络
            # friends_list_results = es.mget(index=twitter_user_index_name,doc_type=twitter_user_index_type,body={'ids':recommend_set_list})['_source']
            # for result in friends_list_results:
            #     friends_list = friends_list + result['friend_list']
            # friends_set_list = list(set(friends_list))


        #转发网络
        if recommend_set_list:
            friends_list_results = es.mget(index=tw_be_retweet_index_name,doc_type=tw_be_retweet_index_type,body={'ids':recommend_set_list})['docs']
            for result in friends_list_results:
                friends_list = []
                try:
                    friends_list = friends_list + result['_source']['uid_be_retweet']
                except Exception,e:
                    print e
            friends_set_list = list(set(friends_list))
        else:
            friends_set_list = []
        
        print 'friends_set_list'
        print friends_set_list



        # sort_item_new = 'fansnum'
        sort_item_new = 'share'
        query_body_rec = {
            'query':{
                'bool':{
                    'must':[
                        {'terms':{'uid':friends_set_list}},
                        {'bool':{
                            'should':nest_query_list
                        }}
                    ]
                }
            },
            'aggs':{
                'uid_list':{
                    'terms':{'field':'uid','size':TOP_ACTIVE_SOCIAL,'order':{'avg_sort':'desc'} },
                    'aggs':{'avg_sort':{'avg':{'field':sort_item_new}}}
                }
            }
        }
        es_friend_result = es.search(index=flow_text_index_name,doc_type='text',body=query_body_rec)['aggregations']['uid_list']['buckets']
        
        for item in es_friend_result:
            uid = item['key']
            uid_list.append(uid)
            
            avg_sort_uid_dict[uid] = {}
            avg_sort_uid_dict[uid]['sort_item_value'] = int(item['avg_sort']['value'])

    results_all = []
    for uid in uid_list:
        query_body = {
            'query':{
                'filtered':{
                    'filter':{
                        'term':{'uid':uid}
                    }
                }
            }
        }

        es_results = es.search(index=tw_portrait_index_name,doc_type=tw_portrait_index_type,body=query_body)['hits']['hits']
        if es_results:
            for item in es_results:
                uid = item['_source']['uid']
                nick_name,photo_url = tw_uid2nick_name_photo(uid)
                item['_source']['nick_name'] = nick_name
                item['_source']['photo_url'] = photo_url
                tw_type = judge_tw_follow_type(xnr_user_no,uid)
                sensor_mark = judge_tw_sensing_sensor(xnr_user_no,uid)

                item['_source']['tw_type'] = tw_type
                item['_source']['sensor_mark'] = sensor_mark







                if sort_item == 'friend':
                    if S_TYPE == 'test':
                        # item['_source']['fansnum'] = item['_source']['fansnum']   #暂无
                        item['_source']['share'] = 0
                    else:
                        # item['_source']['fansnum'] = avg_sort_uid_dict[uid]['sort_item_value']
                        item['_source']['share'] = avg_sort_uid_dict[uid]['sort_item_value']
                elif sort_item == 'sensitive':
                    item['_source']['sensitive'] = avg_sort_uid_dict[uid]['sort_item_value']
                    # item['_source']['fansnum'] = item['_source']['fansnum']   #暂无
                    # item['_source']['fansnum'] = 0
                else:
                    item['_source']['fansnum'] = avg_sort_uid_dict[uid]['sort_item_value']
                    item['_source']['share'] = avg_sort_uid_dict[uid]['sort_item_value']








                if S_TYPE == 'test':
                    current_time = datetime2ts(S_DATE_TW)
                else:
                    current_time = int(time.time())

                index_name = get_flow_text_index_list(current_time)
                query_body = {
                    'query':{
                        'bool':{
                            'must':[
                                {'term':{'uid':uid}},
                                # {'terms':{'message_type':[1,3]}}
                            ]
                        }
                    },
                    # 'sort':{'retweeted':{'order':'desc'}}
                }

                es_tw_results = es.search(index=index_name,doc_type=twitter_flow_text_index_type,body=query_body)['hits']['hits']
                tw_list = []
                for tw in es_tw_results:
                    tw = tw['_source']
                    tw_list.append(tw)
                item['_source']['tw_list'] = tw_list
                item['_source']['portrait_status'] = True
                results_all.append(item['_source'])
        else:
            item_else = dict()
            item_else['uid'] = uid
            nick_name,photo_url = tw_uid2nick_name_photo(uid)
            item_else['nick_name'] = nick_name
            item_else['photo_url'] = photo_url
            tw_type = judge_tw_follow_type(xnr_user_no,uid)
            sensor_mark = judge_tw_sensing_sensor(xnr_user_no,uid)
            item_else['tw_type'] = tw_type
            item_else['sensor_mark'] = sensor_mark
            item_else['portrait_status'] = False         

            if S_TYPE == 'test':
                current_time = datetime2ts(S_DATE_TW)
            else:
                current_time = int(time.time())

            index_name = get_flow_text_index_list(current_time)

            query_body = {
                'query':{
                    'term':{'uid':uid}
                },
                # 'sort':{'retweeted':{'order':'desc'}}
            }

            es_tw_results = es.search(index=index_name,doc_type=twitter_flow_text_index_type,body=query_body)['hits']['hits']

            tw_list = []
            for tw in es_tw_results:
                # item_else['fansnum'] = tw['_source']['user_fansnum']    #暂无 
                item_else['fansnum'] = 0
                tw = tw['_source']
                tw_list.append(tw)
            item_else['tw_list'] = tw_list
            item_else['friendsnum'] = 0
            item_else['statusnum'] = 0
            if sort_item == 'sensitive':
                item_else['sensitive'] = avg_sort_uid_dict[uid]['sort_item_value']
            else:
                item_else['fansnum'] = avg_sort_uid_dict[uid]['sort_item_value']
            results_all.append(item_else)
    return results_all





#查询虚拟人uid
def lookup_xnr_uid(xnr_user_no):
    try:
        xnr_result=es.get(index=tw_xnr_index_name,doc_type=tw_xnr_index_type,id=xnr_user_no)['_source']
        xnr_uid=xnr_result['uid']
    except:
        xnr_uid=''
    return xnr_uid

#查询用户昵称
def get_user_nickname(uid):
    try:
        user_result=es.get(index=twitter_user_index_name,doc_type=twitter_user_index_type,id=uid)['_source']
        user_name=user_result['username']
    except:
        user_name=''
    return user_name

def save_oprate_like(task_detail):
    like_id = task_detail['xnr_user_no'] + '_' + task_detail['r_tid']
    like_detail=dict()
    like_detail['update_time'] = int(time.time())
    like_detail['root_tid'] = task_detail['r_tid']
    like_detail['root_uid'] = task_detail['r_uid']
    like_detail['tid'] = like_id

    #查询xnr_user_no的uid
    like_detail['uid'] = lookup_xnr_uid(task_detail['xnr_user_no'])
    #根据mid查询
    flow_text_index_name = twitter_flow_text_index_name_pre + ts2datetime(task_detail['timestamp'])
    try:
        flow_result = es.get(index=flow_text_index_name,doc_type=twitter_flow_text_index_type,id=task_detail['r_tid'])['_source']      
        like_detail['nick_name'] = get_user_nickname(flow_result['uid'])
        like_detail['photo_url'] = ''
        like_detail['timestamp'] = flow_result['timestamp']
        like_detail['text'] = flow_result['text']
        like_detail['twitter_type'] = ''
    except:
        like_detail['nick_name'] = ''
        like_detail['photo_url'] = ''
        like_detail['timestamp'] = int(task_detail['timestamp'])
        like_detail['text'] = ''
        like_detail['twitter_type'] = ''

    try:
        es.index(index=twitter_xnr_save_like_index_name,doc_type=twitter_xnr_save_like_index_type,id=like_id,body=like_detail)
        mark=True
    except:
        mark=False
    return mark


# 存储关注用户关注关系
def save_twitter_follow_operate(xnr_user_no,uid_string,follow_type_string):

    root_uid = xnr_user_no2uid(xnr_user_no)
    print '-------------'
    print uid_string
    print follow_type_string
    print '------------'
    uid_list = uid_string.encode('utf-8').split('，')
    print uid_list
    follow_type_list = follow_type_string.encode('utf-8').split('，')
    print len(follow_type_list)
    follow_data = {}
    # add gensuiguanzhu
    if len(follow_type_list) == 3:
        follow_data={"richangguanzhu":1, "yewuguanzhu":1, "gensuiguanzhu":1, "pingtaiguanzhu":1}
    elif len(follow_type_list) == 1:
        if follow_type_list[0] == 'daily':
            follow_data={"richangguanzhu":1,"pingtaiguanzhu":1}

        elif follow_type_list[0] == 'business':
            follow_data={"yewuguanzhu":1,"pingtaiguanzhu":1}

        elif follow_type_list[0] == 'gensui':
            follow_data={"gensuiguanzhu":1,"pingtaiguanzhu":1}
    elif len(follow_type_list) == 2:
        type_one = follow_type_list[0]
        type_two = follow_type_list[1]
        if type_one == 'daily' and type_two == 'business':
            follow_data = {"richangguanzhu": 1,"yewuguanzhu":1,"pingtaiguanzhu": 1}
        elif type_one == 'business' and type_two == 'gensui':
            follow_data = {"yewuguanzhu": 1,"gensuiguanzhu":1,"pingtaiguanzhu": 1}
        elif type_one == 'daily' and type_two == 'gensui':
            follow_data = {"richangguanzhu": 1, "gensuiguanzhu": 1, "pingtaiguanzhu": 1}

    else:
        follow_data = {"richangguanzhu": 0, "yewuguanzhu": 0, "gensuiguanzhu": 1, "pingtaiguanzhu": 1}
    print follow_data
    for uid in uid_list:
        if not update_twitter_xnr_relations(root_uid, uid, follow_data):
            return {'status':'fail'}
    return {'status':'ok'}

