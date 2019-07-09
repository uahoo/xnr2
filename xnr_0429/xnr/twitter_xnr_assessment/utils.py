# -*-coding:utf-8-*-

import json
import time
from collections import Counter
import random
from xnr.global_utils import es_xnr as es
es_flow_text = es
es_user_portrait = es
es_user_profile = es
from xnr.global_utils import R_WEIBO_XNR_FANS_FOLLOWERS as r_fans_followers ,\
                            twitter_xnr_count_info_index_name,twitter_xnr_count_info_index_type
from xnr.global_config import S_TYPE,S_DATE_TW as S_DATE, S_UID_TW as S_UID, S_DATE_BCI_TW as S_DATE_BCI
from xnr.utils import tw_xnr_user_no2uid as xnr_user_no2uid,tw_uid2nick_name_photo as uid2nick_name_photo
from xnr.global_utils import twitter_feedback_comment_index_name,twitter_feedback_comment_index_type,\
                        twitter_feedback_retweet_index_name,twitter_feedback_retweet_index_type,\
                        twitter_feedback_private_index_name,twitter_feedback_private_index_type,\
                        twitter_feedback_at_index_name,twitter_feedback_at_index_type,\
                        twitter_feedback_like_index_name,twitter_feedback_like_index_type,\
                        twitter_feedback_fans_index_name,twitter_feedback_fans_index_type,\
                        twitter_feedback_follow_index_name,twitter_feedback_follow_index_type,\
                        tw_xnr_fans_followers_index_name as twitter_xnr_fans_followers_index_name,\
                        tw_xnr_fans_followers_index_type as twitter_xnr_fans_followers_index_type,\
                        twitter_flow_text_index_type as flow_text_index_type,\
                        tw_bci_index_name_pre as twitter_bci_index_name_pre,tw_bci_index_type as twitter_bci_index_type,\
                        twitter_flow_text_index_name_pre as flow_text_index_name_pre,\
                        twitter_report_management_index_name,twitter_report_management_index_type,\
                        tw_portrait_index_name as portrait_index_name,tw_portrait_index_type as portrait_index_type,\
                        tw_xnr_flow_text_index_type as xnr_flow_text_index_type,\
                        twitter_xnr_assessment_index_name,twitter_xnr_assessment_index_type,\
                        twitter_xnr_count_info_index_name,twitter_xnr_count_info_index_type,\
                        twitter_xnr_count_info_index_name,twitter_xnr_count_info_index_type,\
                        tw_xnr_flow_text_index_name_pre as xnr_flow_text_index_name_pre,\
                        twitter_feedback_at_index_name_pre, twitter_feedback_retweet_index_name_pre,\
                        twitter_feedback_comment_index_name_pre,\
                        new_tw_xnr_flow_text_index_type as new_xnr_flow_text_index_type

from xnr.time_utils import ts2datetime,datetime2ts,tw_get_flow_text_index_list as get_flow_text_index_list,\
                        get_tw_xnr_flow_text_index_list as get_xnr_flow_text_index_list,\
                        get_new_tw_xnr_flow_text_index_list as get_new_xnr_flow_text_index_list
from xnr.parameter import WEEK,DAY,MAX_SEARCH_SIZE,TOP_ASSESSMENT_NUM,TOP_WEIBOS_LIMIT,\
                        tw_domain_en2ch_dict as domain_en2ch_dict, tw_domain_ch2en_dict as domain_ch2en_dict








from xnr.global_utils import user_domain_index_name,user_domain_index_type
from xnr.global_utils import r_fans_uid_list_datetime_pre,r_fans_count_datetime_xnr_pre,r_fans_search_xnr_pre,\
                r_followers_uid_list_datetime_pre,r_followers_count_datetime_xnr_pre,r_followers_search_xnr_pre



from xnr.parameter import PORTRAIT_UID_LIST,PORTRAI_UID,FOLLOWERS_TODAY,ACTIVE_UID

def get_influence_total_trend(xnr_user_no,start_time,end_time):

    total_dict = {}
    total_dict['total_trend'] = {}
    total_dict['day_num'] = {}
    total_dict['growth_rate'] = {}

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'xnr_user_no':xnr_user_no}},
                    {'range':{
                        'timestamp':{'gte':start_time,'lt':end_time}
                    }}
                ]
            }
        },
        'size':MAX_SEARCH_SIZE
    }
    try:
        search_results = es.search(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,\
            body=query_body)['hits']['hits']
    except:
        search_results = []

    fans_dict = {}
    fans_dict['total_num'] = {}
    fans_dict['day_num'] = {}
    fans_dict['growth_rate'] = {}

    retweet_dict = {}
    retweet_dict['total_num'] = {}
    retweet_dict['day_num'] = {}
    retweet_dict['growth_rate'] = {}

    comment_dict = {}
    comment_dict['total_num'] = {}
    comment_dict['day_num'] = {}
    comment_dict['growth_rate'] = {}

    like_dict = {}
    like_dict['total_num'] = {}
    like_dict['day_num'] = {}
    like_dict['growth_rate'] = {}

    at_dict = {}
    at_dict['total_num'] = {}
    at_dict['day_num'] = {}
    at_dict['growth_rate'] = {}

    private_dict = {}
    private_dict['total_num'] = {}
    private_dict['day_num'] = {}
    private_dict['growth_rate'] = {}


    for result in search_results:
        result = result['_source']
        timestamp = result['timestamp']

        fans_dict['total_num'][timestamp] = result['fans_total_num']
        fans_dict['day_num'][timestamp] = result['fans_day_num']
        fans_dict['growth_rate'][timestamp] = result['fans_growth_rate']

        retweet_dict['total_num'][timestamp] = result['retweet_total_num']
        retweet_dict['day_num'][timestamp] = result['retweet_day_num']
        retweet_dict['growth_rate'][timestamp] = result['retweet_growth_rate']

        comment_dict['total_num'][timestamp] = result['comment_total_num']
        comment_dict['day_num'][timestamp] = result['comment_day_num']
        comment_dict['growth_rate'][timestamp] = result['comment_growth_rate']

        like_dict['total_num'][timestamp] = result['like_total_num']
        like_dict['day_num'][timestamp] = result['like_day_num']
        like_dict['growth_rate'][timestamp] = result['like_growth_rate']

        private_dict['total_num'][timestamp] = result['private_total_num']
        private_dict['day_num'][timestamp] = result['private_day_num']
        private_dict['growth_rate'][timestamp] = result['private_growth_rate']
        
        at_dict['total_num'][timestamp] = result['at_total_num']
        at_dict['day_num'][timestamp] = result['at_day_num']
        at_dict['growth_rate'][timestamp] = result['at_growth_rate']


    total_dict['total_trend']['fans'] = fans_dict['total_num']
    total_dict['total_trend']['retweet'] = retweet_dict['total_num']
    total_dict['total_trend']['comment'] = comment_dict['total_num']
    total_dict['total_trend']['like'] = like_dict['total_num']
    total_dict['total_trend']['at'] = at_dict['total_num']
    total_dict['total_trend']['private'] = private_dict['total_num']

    total_dict['day_num']['fans'] = fans_dict['day_num']
    total_dict['day_num']['retweet'] = retweet_dict['day_num']
    total_dict['day_num']['comment'] = comment_dict['day_num']
    total_dict['day_num']['like'] = like_dict['day_num']
    total_dict['day_num']['at'] = at_dict['day_num']
    total_dict['day_num']['private'] = private_dict['day_num']

    total_dict['growth_rate']['fans'] = fans_dict['growth_rate']
    total_dict['growth_rate']['retweet'] = retweet_dict['growth_rate']
    total_dict['growth_rate']['comment'] = comment_dict['growth_rate']
    total_dict['growth_rate']['like'] = like_dict['growth_rate']
    total_dict['growth_rate']['at'] = at_dict['growth_rate']
    total_dict['growth_rate']['private'] = private_dict['growth_rate']

    return total_dict

def get_influence_total_trend_today(xnr_user_no):

    current_time = int(time.time())

    fans_dict = get_influ_fans_num(xnr_user_no,current_time)
    retweet_dict = get_influ_retweeted_num(xnr_user_no,current_time)
    comment_dict = get_influ_commented_num(xnr_user_no,current_time)
    like_dict = get_influ_like_num(xnr_user_no,current_time)
    at_dict = get_influ_at_num(xnr_user_no,current_time)
    private_dict = get_influ_private_num(xnr_user_no,current_time)

    total_dict = {}
    total_dict['total_trend'] = {}
    total_dict['day_num'] = {}
    total_dict['growth_rate'] = {}


    total_dict['total_trend']['fans'] = fans_dict['total_num']
    total_dict['total_trend']['retweet'] = retweet_dict['total_num']
    total_dict['total_trend']['comment'] = comment_dict['total_num']
    total_dict['total_trend']['like'] = like_dict['total_num']
    total_dict['total_trend']['at'] = at_dict['total_num']
    total_dict['total_trend']['private'] = private_dict['total_num']

    total_dict['day_num']['fans'] = fans_dict['day_num']
    total_dict['day_num']['retweet'] = retweet_dict['day_num']
    total_dict['day_num']['comment'] = comment_dict['day_num']
    total_dict['day_num']['like'] = like_dict['day_num']
    total_dict['day_num']['at'] = at_dict['day_num']
    total_dict['day_num']['private'] = private_dict['day_num']

    total_dict['growth_rate']['fans'] = fans_dict['growth_rate']
    total_dict['growth_rate']['retweet'] = retweet_dict['growth_rate']
    total_dict['growth_rate']['comment'] = comment_dict['growth_rate']
    total_dict['growth_rate']['like'] = like_dict['growth_rate']
    total_dict['growth_rate']['at'] = at_dict['growth_rate']
    total_dict['growth_rate']['private'] = private_dict['growth_rate']

    return total_dict

def compute_growth_rate_total(day8_dict,total8_dict):
    total_dict = {}
    total_dict['growth_rate'] = {}
    total_dict['day_num'] = {}
    total_dict['total_num'] = {}
    # print 'day8_dict::',day8_dict
    # print 'total8_dict:::',total8_dict
    for timestamp, num in day8_dict.iteritems():
        total_timestamp = timestamp - DAY
        day_num = day8_dict[timestamp]
        try:
            total_num_lastday = total8_dict[total_timestamp]
            # print 'total_num_lastday:::',total_num_lastday
            if not total_num_lastday:
                total_num_lastday = 1
            total_dict['growth_rate'][timestamp] = round(float(day_num)/total_num_lastday,2)
            total_dict['day_num'][timestamp] = day8_dict[timestamp]
            total_dict['total_num'][timestamp] = total8_dict[timestamp]
        except:
            continue

    return total_dict

# 影响力粉丝数
def get_influ_fans_num(xnr_user_no,current_time):
    fans_dict = {}

    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    r_fans_count = r_fans_count_datetime_xnr_pre + current_date + '_' + xnr_user_no
    r_fans_uid_list = r_fans_uid_list_datetime_pre + current_date

    datetime_count = r_fans_followers.get(r_fans_count)
    fans_uid_list = r_fans_followers.hget(r_fans_uid_list,xnr_user_no)

    if not datetime_count:
        datetime_count = 0

    if not fans_uid_list:
        datetime_total = 0
    else:
        datetime_total = len(json.loads(fans_uid_list))
    fans_dict['day_num'] = {}
    fans_dict['total_num'] = {}
    fans_dict['growth_rate'] = {}
    fans_dict['day_num'][current_time_new] = datetime_count
    fans_dict['total_num'][current_time_new] = datetime_total

    last_day = ts2datetime(current_time_new - DAY)
    _id_last_day = xnr_user_no + '_' + last_day

    get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,id=_id_last_day)['_source']
    fans_total_num_last = get_result['fans_total_num']
    if not fans_total_num_last:
        fans_total_num_last = 1

    fans_dict['growth_rate'][current_time_new] = round(float(datetime_count)/fans_total_num_last,2)

    return fans_dict

def get_influ_retweeted_num(xnr_user_no,current_time):

    retweet_dict = {}

    uid = xnr_user_no2uid(xnr_user_no)


    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name_day = twitter_feedback_retweet_index_name_pre + current_date
    index_name_total = get_timeset_indexset_list(index_name_pre=twitter_feedback_retweet_index_name_pre,startdate=S_DATE,enddate=current_date)

    query_body_day = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'range':{'timestamp':{'gte':current_time_new,'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    query_body_total = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'range':{'timestamp':{'gte':0,'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    try:
        es_day_count_result = es.count(index=index_name_day,doc_type=twitter_feedback_retweet_index_type,\
                        body=query_body_day,request_timeout=999999)

        if es_day_count_result['_shards']['successful'] != 0:
            es_day_count = es_day_count_result['count']
        else:
            return 'es_day_count_found_error'
    except Exception,e:
        print e
        es_day_count = 0

    try:
        es_total_count_result = es.count(index=index_name_total,doc_type=twitter_feedback_retweet_index_type,\
                        body=query_body_total,request_timeout=999999)

        if es_total_count_result['_shards']['successful'] != 0:
            es_total_count = es_total_count_result['count']
        else:
            return 'es_total_count_found_error'
    except Exception,e:
        print e
        es_total_count = 0


    retweet_dict['day_num'] = {}
    retweet_dict['total_num'] = {}
    retweet_dict['growth_rate'] = {}

    retweet_dict['day_num'][current_time_new] = es_day_count
    retweet_dict['total_num'][current_time_new] = es_total_count

    last_day = ts2datetime(current_time_new - DAY)
    _id_last_day = xnr_user_no + '_' + last_day

    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,id=_id_last_day)['_source']
        retweet_total_num_last = get_result['retweet_total_num']

        if not retweet_total_num_last:
            retweet_total_num_last = 1
    except Exception,e:
        print e
        retweet_total_num_last = 1

    retweet_dict['growth_rate'][current_time_new] = round(float(es_day_count)/retweet_total_num_last,2)

    
    return retweet_dict

def get_influ_commented_num(xnr_user_no,current_time):
    # 收到的评论 comment_type : receive
    comment_dict = {}

    uid = xnr_user_no2uid(xnr_user_no)


    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name_day = twitter_feedback_comment_index_name_pre + current_date
    index_name_total = get_timeset_indexset_list(index_name_pre=twitter_feedback_comment_index_name_pre,startdate=S_DATE,enddate=current_date)

    query_body_day = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'term':{'comment_type':'receive'}},
                    # {'range':{'timestamp':{'gte':current_time_new,'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    query_body_total = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'term':{'comment_type':'receive'}},
                    # {'range':{'timestamp':{'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    es_day_count_result = es.count(index=index_name_day,doc_type=twitter_feedback_comment_index_type,\
                    body=query_body_day,request_timeout=999999)

    if es_day_count_result['_shards']['successful'] != 0:
        es_day_count = es_day_count_result['count']
    else:
        return 'es_day_count_found_error'


    es_total_count_result = es.count(index=index_name_total,doc_type=twitter_feedback_comment_index_type,\
                    body=query_body_total,request_timeout=999999)

    if es_total_count_result['_shards']['successful'] != 0:
        es_total_count = es_total_count_result['count']
    else:
        return 'es_total_count_found_error'

    comment_dict['day_num'] = {}
    comment_dict['total_num'] = {}
    comment_dict['growth_rate'] = {}

    comment_dict['day_num'][current_time_new] = es_day_count
    comment_dict['total_num'][current_time_new] = es_total_count

    last_day = ts2datetime(current_time_new - DAY)
    _id_last_day = xnr_user_no + '_' + last_day

    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,id=_id_last_day)['_source']
        comment_total_num_last = get_result['comment_total_num']

        if not comment_total_num_last:
            comment_total_num_last = 1
    except Exception,e:
        print e
        comment_total_num_last = 1

    comment_dict['growth_rate'][current_time_new] = round(float(es_day_count)/comment_total_num_last,2)

    return comment_dict

def get_influ_like_num(xnr_user_no,current_time):

    like_dict = {}


    uid = xnr_user_no2uid(xnr_user_no)

    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name_day = twitter_feedback_like_index_name_pre + current_date
    index_name_total = get_timeset_indexset_list(index_name_pre=twitter_feedback_like_index_name_pre,startdate=S_DATE,enddate=current_date)

    query_body_day = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'range':{'timestamp':{'gte':current_time_new,'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }
    
    query_body_total = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'range':{'timestamp':{'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    es_day_count_result = es.count(index=index_name_day,doc_type=twitter_feedback_like_index_type,\
                    body=query_body_day,request_timeout=999999)

    if es_day_count_result['_shards']['successful'] != 0:
        es_day_count = es_day_count_result['count']
    else:
        return 'es_day_count_found_error'

    es_total_count_result = es.count(index=index_name_total,doc_type=twitter_feedback_like_index_type,\
                    body=query_body_total,request_timeout=999999)

    if es_total_count_result['_shards']['successful'] != 0:
        es_total_count = es_total_count_result['count']
    else:
        return 'es_total_count_found_error'

    like_dict['day_num'] = es_day_count
    like_dict['total_num'] = es_total_count

    last_day = ts2datetime(current_time_new - DAY)
    _id_last_day = xnr_user_no + '_' + last_day

    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,id=_id_last_day)['_source']
        like_total_num_last = get_result['like_total_num']
        if not like_total_num_last:
            like_total_num_last = 1
    except Exception,e:
        print e
        like_total_num_last = 1
    like_dict['growth_rate'] = round(float(es_day_count)/like_total_num_last,2)

    return like_dict

def get_influ_at_num(xnr_user_no,current_time):
    at_dict = {}

    uid = xnr_user_no2uid(xnr_user_no)

    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name_day = twitter_feedback_at_index_name_pre + current_date
    index_name_total = get_timeset_indexset_list(index_name_pre=twitter_feedback_at_index_name_pre,startdate=S_DATE,enddate=current_date)

    query_body_day = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'range':{'timestamp':{'gte':current_time_new,'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    query_body_total = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    # {'range':{'timestamp':{'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    es_day_count_result = es.count(index=index_name_day,doc_type=twitter_feedback_at_index_type,\
                    body=query_body_day,request_timeout=999999)

    if es_day_count_result['_shards']['successful'] != 0:
        es_day_count = es_day_count_result['count']
    else:
        return 'es_day_count_found_error'

    es_total_count_result = es.count(index=index_name_total,doc_type=twitter_feedback_at_index_type,\
                    body=query_body_total,request_timeout=999999)

    if es_total_count_result['_shards']['successful'] != 0:
        es_total_count = es_total_count_result['count']
    else:
        return 'es_total_count_found_error'

    at_dict['day_num'] = es_day_count
    at_dict['total_num'] = es_total_count

    last_day = ts2datetime(current_time_new - DAY)
    _id_last_day = xnr_user_no + '_' + last_day

    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,id=_id_last_day)['_source']
        at_total_num_last = get_result['at_total_num']

        if not at_total_num_last:
            at_total_num_last = 1
    except Exception,e:
        print e
        at_total_num_last = 1

    at_dict['growth_rate'] = round(float(es_day_count)/at_total_num_last,2)


    return at_dict

def get_influ_private_num(xnr_user_no,current_time):
    # 收到的私信 private_type : receive
    private_dict = {}

    uid = xnr_user_no2uid(xnr_user_no)


    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name_day = twitter_feedback_private_index_name_pre + current_date
    index_name_total = get_timeset_indexset_list(index_name_pre=twitter_feedback_private_index_name_pre,startdate=S_DATE,enddate=current_date)
    
    query_body_day = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'term':{'private_type':'receive'}},
                    # {'range':{'timestamp':{'gte':current_time_new,'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    query_body_total = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'term':{'private_type':'receive'}},
                    # {'range':{'timestamp':{'lt':(current_time_new+DAY)}}}
                ]
            }
        }
    }

    es_day_count_result = es.count(index=index_name_day,doc_type=twitter_feedback_private_index_type,\
                    body=query_body_day,request_timeout=999999)

    if es_day_count_result['_shards']['successful'] != 0:
        es_day_count = es_day_count_result['count']
    else:
        return 'es_day_count_found_error'


    es_total_count_result = es.count(index=index_name_total,doc_type=twitter_feedback_private_index_type,\
                    body=query_body_total,request_timeout=999999)

    if es_total_count_result['_shards']['successful'] != 0:
        es_total_count = es_total_count_result['count']
    else:
        return 'es_total_count_found_error'

    private_dict['day_num'] = es_day_count
    private_dict['total_num'] = es_total_count

    last_day = ts2datetime(current_time_new - DAY)
    _id_last_day = xnr_user_no + '_' + last_day
    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,id=_id_last_day)['_source']
        private_total_num_last = get_result['private_total_num']

        if not private_total_num_last:
            private_total_num_last = 1
    except Exception,e:
        print e
        private_total_num_last = 1

    private_dict['growth_rate'] = round(float(es_day_count)/private_total_num_last,2)

    return private_dict


def compute_influence_num(xnr_user_no):

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)
    else:
        current_time = int(time.time()-DAY)
    
    current_date = ts2datetime(current_time)

    _id = xnr_user_no + '_' + current_date
    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,\
            id=_id)['_source']
        influence = get_result['influence']
    except Exception,e:
        print e
        influence = 0
    return influence

'''
渗透力
'''

# 渗透力分数
def compute_penetration_num(xnr_user_no):

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)
    else:
        current_time = int(time.time()-DAY)
    
    current_date = ts2datetime(current_time)

    _id = xnr_user_no + '_' + current_date
    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,\
                id=_id)['_source']

        pene_mark = get_result['penetration']
    except Exception,e:
        print e
        pene_mark = 0
    return pene_mark


def penetration_total(xnr_user_no,start_time,end_time):
    
    total_dict = {}
    total_dict['follow_group'] = {}
    total_dict['fans_group'] = {}
    total_dict['feedback_total'] = {}
    total_dict['self_info'] = {}
    total_dict['warning_report_total'] = {}

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'xnr_user_no':xnr_user_no}},
                    {'range':{
                        'timestamp':{'gte':start_time,'lt':end_time}
                    }}
                ]
            }
        },
        'size':MAX_SEARCH_SIZE
    }
    try:
        search_results = es.search(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,\
            body=query_body)['hits']['hits']
    except:
        search_results = []

    follow_group = {}
    fans_group = {}
    self_info = {}
    warning_report_total = {}
    feedback_total = {}


    for result in search_results:
        result = result['_source']
        timestamp = result['timestamp']
        follow_group[timestamp] = result['follow_group_sensitive_info']
        fans_group[timestamp] = result['fans_group_sensitive_info']
        self_info[timestamp] = result['self_info_sensitive_info']
        warning_report_total[timestamp] = result['warning_report_total_sensitive_info']
        feedback_total[timestamp] = result['feedback_total_sensitive_info']

    total_dict['follow_group'] = follow_group
    total_dict['fans_group'] = fans_group
    total_dict['self_info'] = self_info
    total_dict['warning_report_total'] = warning_report_total
    total_dict['feedback_total'] = feedback_total

    return total_dict

def penetration_total_today(xnr_user_no):

    total_dict = {}

    current_time = int(time.time())

    follow_group = get_pene_follow_group_sensitive(xnr_user_no,current_time)
    fans_group = get_pene_fans_group_sensitive(xnr_user_no,current_time)
    self_info = get_pene_infor_sensitive(xnr_user_no,current_time)
    
    feedback_at = get_pene_feedback_sensitive(xnr_user_no,'be_at',current_time)
    feedback_retweet = get_pene_feedback_sensitive(xnr_user_no,'be_retweet',current_time)
    feedback_commet = get_pene_feedback_sensitive(xnr_user_no,'be_comment',current_time)

    feedback_total = {}
    total_dict['follow_group'] = {}
    total_dict['fans_group'] = {}
    total_dict['self_info'] = {}
    total_dict['warning_report_total'] = {}
    total_dict['feedback_total'] = {}
    #feedback_total['sensitive_info'] = {}

    #for timestamp in feedback_at['sensitive_info']:
    feedback_total['sensitive_info'] = float(feedback_at['sensitive_info'] + \
        feedback_retweet['sensitive_info'] + feedback_commet['sensitive_info'])/3
    
    warning_report = get_pene_warning_report_sensitive(xnr_user_no,current_time)

    warning_report_total = round(float(warning_report['event']+ \
        warning_report['user'] + warning_report['tweet'])/3,2)

    total_dict['follow_group'][current_time] = follow_group['sensitive_info']
    total_dict['fans_group'][current_time] = fans_group['sensitive_info']
    total_dict['self_info'][current_time] = self_info['sensitive_info']
    total_dict['warning_report_total'][current_time] = warning_report_total
    total_dict['feedback_total'][current_time] = feedback_total['sensitive_info']

    return total_dict

def get_pene_follow_group_sensitive(xnr_user_no,current_time_old):

    #if xnr_user_no:
    es_results = es.get(index=twitter_xnr_fans_followers_index_name,doc_type=twitter_xnr_fans_followers_index_type,\
                            id=xnr_user_no)["_source"]
    followers_list = es_results['followers_list']

    
    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE_BCI)
    else:
        current_time = current_time_old
    
    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name = flow_text_index_name_pre + current_date

    follow_group_sensitive = {}

    query_body_info = {
        'query':{
            'filtered':{
                'filter':{
                    'terms':{'uid':followers_list}
                }
            }
        },
        'aggs':{
            'avg_sensitive':{
                'avg':{
                    'field':'sensitive'
                }
            }
        }
    }
    try:
        es_sensitive_result = es_flow_text.search(index=index_name,doc_type=flow_text_index_type,\
            body=query_body_info)['aggregations']
        sensitive_value = round(es_sensitive_result['avg_sensitive']['value'],2)

        if sensitive_value == None:
            sensitive_value = 0.0
    except Exception,e:
        print e
        sensitive_value = 0.0

    follow_group_sensitive['sensitive_info'] = sensitive_value

    return follow_group_sensitive

def get_pene_fans_group_sensitive(xnr_user_no,current_time_old):

    try:
        es_results = es.get(index=twitter_xnr_fans_followers_index_name,doc_type=twitter_xnr_fans_followers_index_type,\
                                id=xnr_user_no)["_source"]
        fans_list = es_results['fans_list']
    except Exception,e:
        print e
        fans_list = []

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE_BCI)
    else:
        current_time = current_time_old
    
    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name = flow_text_index_name_pre + current_date

    fans_group_sensitive = {}
    query_body_info = {
        'query':{
            'filtered':{
                'filter':{
                    'terms':{'uid':fans_list}
                }
            }
        },
        'aggs':{
            'avg_sensitive':{
                'avg':{
                    'field':'sensitive'
                }
            }
        }
    }
    es_sensitive_result = es_flow_text.search(index=index_name,doc_type=flow_text_index_type,\
        body=query_body_info)['aggregations']
    sensitive_value = es_sensitive_result['avg_sensitive']['value']

    if sensitive_value == None:
        sensitive_value = 0.0
    fans_group_sensitive['sensitive_info'] = sensitive_value

    return fans_group_sensitive

def get_pene_infor_sensitive(xnr_user_no,current_time_old):
    
    uid = xnr_user_no2uid(xnr_user_no)

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE_BCI)
        uid = S_UID
    else:
        current_time = current_time_old
    
    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)

    index_name = flow_text_index_name_pre + current_date

    my_info_sensitive = {}
    query_body_info = {
        'query':{
            'filtered':{
                'filter':{
                    'term':{'uid':uid}
                }
            }
        },
        'aggs':{
            'avg_sensitive':{
                'avg':{
                    'field':'sensitive'
                }
            }
        }
    }
    es_sensitive_result = es_flow_text.search(index=index_name,doc_type=flow_text_index_type,\
        body=query_body_info)['aggregations']
    sensitive_value = es_sensitive_result['avg_sensitive']['value']

    if sensitive_value == None:
        sensitive_value = 0.0
    my_info_sensitive['sensitive_info'] = sensitive_value

    return my_info_sensitive

def get_pene_feedback_sensitive(xnr_user_no,sort_item,current_time_old):
    
    uid = xnr_user_no2uid(xnr_user_no)

    if sort_item == 'be_at':
        index_name_sort_pre = twitter_feedback_at_index_name_pre
        index_type_sort = twitter_feedback_at_index_type
    elif sort_item == 'be_retweet':
        index_name_sort_pre = twitter_feedback_retweet_index_name_pre
        index_type_sort = twitter_feedback_retweet_index_type
    elif sort_item == 'be_comment':
        index_name_sort_pre = twitter_feedback_comment_index_name_pre
        index_type_sort = twitter_feedback_comment_index_type

    if S_TYPE == 'test':
        current_time = current_time_old
        current_time_test = datetime2ts(S_DATE_BCI)
    else:
        current_time = current_time_old
        current_time_test = current_time
    #current_time = int(time.time())
    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)
    
    current_date_test = ts2datetime(current_time_test)
    current_time_new_test = datetime2ts(current_date_test)

    index_name_sort = index_name_sort_pre + current_date

    feedback_sensitive_dict = {}
    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'root_uid':uid}},
                    {'range':{'timestamp':{'gte':current_time_new,'lt':(current_time_new+DAY)}}}
                ]
            }
        },
        'aggs':{
            'avg_sensitive':{
                'avg':{
                    'field':'sensitive_info'
                }
            }
        }
    }
    try:
        es_sensitive_result = es.search(index=index_name_sort,doc_type=index_type_sort,body=query_body)['aggregations']

        sensitive_value = es_sensitive_result['avg_sensitive']['value']

        if sensitive_value == None:
            sensitive_value = 0.0
    except Exception,e:
        print e
        sensitive_value = 0.0
    feedback_sensitive_dict['sensitive_info'] = sensitive_value

    return feedback_sensitive_dict

def get_pene_warning_report_sensitive(xnr_user_no,current_time_old):

    sensitive_report_dict = {}
    report_type_list = [u'人物',u'事件',u'言论']

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)
    else:
        current_time = current_time_old

    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)


    mid_event_list = []
    mid_tweet_list = []
    uid_list = []

    for report_type in report_type_list:
        query_body = {
            'query':{
                'bool':{
                    'must':[
                        {'term':{'xnr_user_no':xnr_user_no}},
                        {'term':{'report_type':report_type}},
                        {'range':{'report_time':{'gte':current_time_new,'lt':(current_time_new+DAY)}}}
                    ]
                }
            },
            'size':MAX_SEARCH_SIZE
            
        }
        try:
            es_sensitive_result = es.search(index=twitter_report_management_index_name,doc_type=twitter_report_management_index_type,\
                body=query_body)['hits']['hits']
        except Exception,e:
            print e
            es_sensitive_result = []
        if es_sensitive_result:    
            if report_type == u'事件':
                for result in es_sensitive_result:
                    result = result['_source']
                    report_content = json.loads(result['report_content'])
                    twitter_list = report_content['twitter_list']
                    for twitter in twitter_list:
                        mid_event_list.append(twitter['mid'])
            elif report_type == u'人物':
                for result in es_sensitive_result:
                    result = result['_source']
                    report_content = json.loads(result['report_content'])
                    user_list = report_content['user_list']
                    for user in user_list:
                        uid_list.append(user['uid'])
            elif report_type == u'言论':
                for result in es_sensitive_result:
                    result = result['_source']
                    report_content = json.loads(result['report_content'])
                    twitter_list = report_content['twitter_list']
                    for twitter in twitter_list:
                        mid_tweet_list.append(twitter['mid'])

    ## 事件平均敏感度
    
    query_body_event = {
        'query':{
            'filtered':{
                'filter':{
                    'terms':{'mid':mid_event_list}
                }
            }
        },
        'aggs':{
            'avg_sensitive':{
                'avg':{
                    'field':'sensitive'
                }
            }
        }
    }

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)

    index_name_list = get_flow_text_index_list(current_time)

    es_result_event = es_flow_text.search(index=index_name_list,doc_type=flow_text_index_type,\
        body=query_body_event)['aggregations']
    event_sensitive_avg = es_result_event['avg_sensitive']['value']

    if event_sensitive_avg == None:
        event_sensitive_avg = 0.0


    ## 人物平均敏感度
    query_body_user = {
        'query':{
            'filtered':{
                'filter':{
                    'terms':{'uid':uid_list}
                }
            }
        },
        'aggs':{
            'avg_sensitive':{
                'avg':{
                    'field':'sensitive'
                }
            }
        }
    }

    es_result_user = es_user_portrait.search(index=portrait_index_name,doc_type=portrait_index_type,\
        body=query_body_user)['aggregations']
    user_sensitive_avg = es_result_user['avg_sensitive']['value']

    if user_sensitive_avg == None:
        user_sensitive_avg = 0.0

    ## 言论平均敏感度
    query_body_tweet = {
        'query':{
            'filtered':{
                'filter':{
                    'terms':{'mid':mid_tweet_list}
                }
            }
        },
        'aggs':{
            'avg_sensitive':{
                'avg':{
                    'field':'sensitive'
                }
            }
        }
    }

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)
    index_name_list = get_flow_text_index_list(current_time)

    es_result_tweet = es_flow_text.search(index=index_name_list,doc_type=flow_text_index_type,\
        body=query_body_tweet)['aggregations']
    tweet_sensitive_avg = es_result_tweet['avg_sensitive']['value']
    if tweet_sensitive_avg == None:
        tweet_sensitive_avg = 0.0

    if S_TYPE == 'test':
        event_sensitive_avg = round(random.random(),2)
        user_sensitive_avg = round(random.random(),2)
        tweet_sensitive_avg = round(random.random(),2)

    sensitive_report_dict['event'] = event_sensitive_avg
    sensitive_report_dict['user'] = user_sensitive_avg
    sensitive_report_dict['tweet'] = tweet_sensitive_avg

    return sensitive_report_dict 


def compute_safe_num(xnr_user_no):
    
    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)
    else:
        current_time = int(time.time()-DAY)
    
    current_date = ts2datetime(current_time)

    _id = xnr_user_no + '_' + current_date
    try:
        get_result = es.get(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,\
                id=_id)['_source']

        safe_mark = get_result['safe']
    except:
        safe_mark = 0

    return safe_mark

def get_safe_active(xnr_user_no,start_time,end_time):


    safe_active_dict = {}

    query_body = {
        'query':{
            'bool':{
                'must':[
                    {'term':{'xnr_user_no':xnr_user_no}},
                    {'range':{
                        'timestamp':{'gte':start_time,'lt':end_time}
                    }}
                ]
            }
        },
        'size':MAX_SEARCH_SIZE
    }
    try:
        search_results = es.search(index=twitter_xnr_count_info_index_name,doc_type=twitter_xnr_count_info_index_type,\
            body=query_body)['hits']['hits']
    except:
        search_results = []

    for result in search_results:
        result = result['_source']
        timestamp = result['timestamp']
        safe_active_dict[timestamp] = result['total_post_sum']
    
    return safe_active_dict

def get_safe_active_today(xnr_user_no):

    query_body = {
        'query':{
            'term':{'xnr_user_no':xnr_user_no}
        }
    }

    current_time = int(time.time())
    current_date = ts2datetime(current_time)
    current_time_new = datetime2ts(current_date)
    safe_active_dict = {} 
    xnr_flow_text_index_name = xnr_flow_text_index_name_pre + current_date
    try:
        search_result = es.count(index=xnr_flow_text_index_name,doc_type=xnr_flow_text_index_type,body=query_body)
        if search_result['_shards']['successful'] != 0:
            result = search_result['count']
        else:
            print 'es index rank error'
            result = 0
    except:
        result = 0
    safe_active_dict[current_time_new] = result

    return safe_active_dict


def get_tweets_distribute(xnr_user_no,start_time,end_time):
    topic_distribute_dict = {}
    topic_distribute_dict['radar'] = {}
    uid = xnr_user_no2uid(xnr_user_no)

    if xnr_user_no:
        es_results = es.get(index=twitter_xnr_fans_followers_index_name,doc_type=twitter_xnr_fans_followers_index_type,\
                                id=xnr_user_no)["_source"]
        followers_list = es_results['followers_list']

    results = es_user_portrait.mget(index=portrait_index_name,doc_type=portrait_index_type,\
        body={'ids':followers_list})['docs']

    topic_list_followers = []
    for result in results:
        if result['found'] == True:
            result = result['_source']
            topic_string_first = result['topic_string'].split('&')
            topic_list_followers.extend(topic_string_first)
    topic_list_followers_count = Counter(topic_list_followers)
    print 'topic_list_followers_count:::',topic_list_followers_count

    # 查询的时间范围
    start_time = int(start_time)
    end_time = int(end_time)
    if start_time < datetime2ts(S_DATE):
        start_time = datetime2ts(S_DATE)
    else:
        start_time = datetime2ts(ts2datetime(start_time))
    end_time = datetime2ts(ts2datetime(end_time))
    days_num = (end_time - start_time)/DAY
    # index_name_list = get_xnr_flow_text_index_list(end_time,days_num)
    index_name_list = get_new_xnr_flow_text_index_list(end_time,days_num)
    
    topic_string = []
    for index_name_day in index_name_list:

        query_body = {
            'query':{
                'bool':{
                    'must':[
                        
                        {'term':{'xnr_user_no':xnr_user_no}}
                    ]
                }
            },
            'size':TOP_WEIBOS_LIMIT,
            'sort':{'timestamp':{'order':'desc'}}
        }
        try:
            es_results = es.search(index=index_name_day,doc_type=new_xnr_flow_text_index_type,body=query_body)['hits']['hits']
            # print 'es_results::',es_results
            for topic_result in es_results:
                #print 'topic_result::',topic_result
                topic_result = topic_result['_source']
                topic_field = topic_result['topic_field_first'][:3]
            topic_string.append(topic_field)
        except Exception,e:
            # print e
            continue

    topic_xnr_count = Counter(topic_string)
    print 'topic_distribute_dict:::',topic_distribute_dict
    print 'topic_xnr_count:::',topic_xnr_count
    if topic_xnr_count:
        for topic, value in topic_list_followers_count.iteritems():
            topic_xnr_count[topic] = min([topic_xnr_count[topic],value])
            try:
                topic_value = round(float(topic_xnr_count[topic])/value,2)
            except:
                continue
            topic_distribute_dict['radar'][topic] = topic_value
            
    # 整理仪表盘数据
    mark = 0
    if topic_xnr_count:
        n_topic = len(topic_list_followers_count.keys())
        for topic,value in topic_xnr_count.iteritems():

            try:
                mark += float(value)/(topic_list_followers_count[topic]*n_topic)
            except:
                continue
    topic_distribute_dict['mark'] = round(mark,4)

    return topic_distribute_dict


def get_safe_tweets(xnr_user_no,topic,start_time, end_time, sort_item):
    # 查询的时间范围
    start_time = int(start_time)
    end_time = int(end_time)
    if start_time < datetime2ts(S_DATE):
        start_time = datetime2ts(S_DATE)
    else:
        start_time = datetime2ts(ts2datetime(start_time))
    end_time = datetime2ts(ts2datetime(end_time))
    days_num = (end_time - start_time)/DAY
    # index_name_list = get_new_xnr_flow_text_index_list(current_time)
    index_name_list = get_new_xnr_flow_text_index_list(end_time,days_num)

    
    es_results_all = []
    for index_name_day in index_name_list:
        query_body = {
            'query':{
                'bool':{
                    'must':[
                        {'term':{'topic_field_first':topic}},
                        {'term':{'xnr_user_no':xnr_user_no}}
                    ]
                }
            },
            'size':TOP_WEIBOS_LIMIT,
            'sort':{sort_item:{'order':'desc'}}
        }
        try:
            es_results = es.search(index=index_name_day,doc_type=new_xnr_flow_text_index_type,body=query_body)['hits']['hits']
            es_results_all.extend(es_results)

        except Exception,e:
            # print e
            continue

    
    results_all = []
    for result in es_results_all:
        result = result['_source']
        uid = result['uid']
        nick_name,photo_url = uid2nick_name_photo(uid)
        result['nick_name'] = nick_name
        result['photo_url'] = photo_url
        results_all.append(result)
    return results_all

def get_follow_group_distribute(xnr_user_no):
    domain_distribute_dict = {}
    domain_distribute_dict['radar'] = {}
    # 获取所有关注者
    es_results = es.get(index=twitter_xnr_fans_followers_index_name,doc_type=twitter_xnr_fans_followers_index_type,\
                            id=xnr_user_no)["_source"]
    followers_list = es_results['followers_list']

    # 获取今日关注者
    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)
    else:
        current_time = int(time.time())
    current_date = ts2datetime(current_time)
    r_uid_list_datetime_index_name = r_followers_uid_list_datetime_pre + current_date
    followers_results = r_fans_followers.hget(r_uid_list_datetime_index_name,xnr_user_no)

    if followers_results != None:
        followers_list_today = json.loads(followers_results)
    else:
        followers_list_today = []
        if S_TYPE == 'test':
            followers_list_today = ['872177406915653632']

    # 所有关注者领域分布
    results = es.mget(index=portrait_index_name,doc_type=portrait_index_type,\
        body={'ids':followers_list})['docs']
    
    domain_list_followers = []
    for result in results:
        if result['found'] == True:
            result = result['_source']
            # domain_name = result['domain_name']
            domain = result['domain']
            if domain:
                domain_name = domain_en2ch_dict[domain]
                domain_list_followers.append(domain_name)

    domain_list_followers_count = Counter(domain_list_followers)
   

    print 'domain_list_followers_count'
    print domain_list_followers_count


    # 今日关注者
    #followers_list_today = FOLLOWERS_TODAY
    try:
        today_results = es.mget(index=portrait_index_name,doc_type=portrait_index_type,\
            body={'ids':followers_list_today})['docs']
        domain_list_followers_today = []

        for result in today_results:
            if result['found'] == True:
                result = result['_source']
                # domain_name = result['domain_name']
                domain = result['domain']
                if domain:
                    domain_name = domain_en2ch_dict[domain]
                    domain_list_followers_today.append(domain_name)

        domain_list_followers_today_count = Counter(domain_list_followers_today)

    except Exception,e:
        print e
        domain_list_followers_today_count = {}

    
    for domain, value in domain_list_followers_count.iteritems():
        if domain_list_followers_today_count:
            try:
                domain_value = round(float(domain_list_followers_today_count[domain])/value,2)
            except:
                domain_value = 0
        else:
            domain_value = 0
        domain_value = min([domain_value,value])
        domain_distribute_dict['radar'][domain] = domain_value

    # 整理仪表盘数据
    mark = 0
    if domain_list_followers_today_count:
        n_domain = len(domain_list_followers_count.keys())
        for domain,value in domain_list_followers_today_count.iteritems():
            try:
                mark += float(value)/(domain_list_followers_count[domain]*n_domain)
            except:
                continue
    domain_distribute_dict['mark'] = round(mark,4)

    return domain_distribute_dict

def get_follow_group_tweets(xnr_user_no,domain,sort_item):

    if S_TYPE == 'test':
        current_time = datetime2ts(S_DATE)
    else:
        current_time = int(time.time())

    es_results = es.get(index=twitter_xnr_fans_followers_index_name,doc_type=twitter_xnr_fans_followers_index_type,\
                            id=xnr_user_no)["_source"]
    followers_list = es_results['followers_list']

    print 'domain', domain
    domain_en = domain_ch2en_dict[domain]
    print 'domain_en', domain_en

    domain_query_body = {
        'query':{
            'bool':{
                'must':[
                    {'terms':{'uid':followers_list}},
                    # {'term':{'domain_name':domain}}
                    {'term':{'domain':domain_en}}
                ]
            }
        }
    }

    domain_search_results = es.search(index=portrait_index_name,\
        doc_type=portrait_index_type,body=domain_query_body)['hits']['hits']

    domain_uid_list = []    
    for domain_result in domain_search_results:
        domain_result = domain_result['_source']
        domain_uid_list.append(domain_result['uid'])

    print 'domain_uid_list'
    print domain_uid_list

    results_all = []

    index_name_list = get_flow_text_index_list(current_time)

    query_body_flow_text = {
        'query':{
            'bool':{
                'must':[
                    {'terms':{'uid':domain_uid_list}},
                    # {'terms':{'message_type':[1,3]}}
                ]
            }
        },
        'size':TOP_WEIBOS_LIMIT,
        'sort':{sort_item:{'order':'desc'}}
    }

    flow_text_results = es_flow_text.search(index=index_name_list,doc_type=flow_text_index_type,\
                        body=query_body_flow_text)['hits']['hits']

    # print 'flow_text_results'
    # print flow_text_results
    
    results_all = []
    for result in flow_text_results:
        result = result['_source']
        uid = result['uid']
        nick_name,photo_url = uid2nick_name_photo(uid)
        result['nick_name'] = nick_name
        result['photo_url'] = photo_url
        results_all.append(result)
    return results_all

