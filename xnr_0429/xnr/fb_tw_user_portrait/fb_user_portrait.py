#-*- coding: utf-8 -*-
import time
import json
from collections import Counter
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from keyword_extraction import get_filter_keywords
import sys
sys.path.append('../')
from global_config import S_DATE_FB, S_DATE_TW
from global_utils import es_xnr_2 as es, \
                         fb_portrait_index_name, fb_portrait_index_type, \
                         facebook_user_index_name, facebook_user_index_type, \
                         facebook_flow_text_index_name_pre, facebook_flow_text_index_type, \
                         fb_bci_index_name_pre, fb_bci_index_type
from time_utils import get_facebook_flow_text_index_list, get_fb_bci_index_list, datetime2ts, ts2datetime
from parameter import MAX_SEARCH_SIZE, FB_TW_TOPIC_ABS_PATH, FB_DOMAIN_ABS_PATH, DAY, WEEK

MAX_SEARCH_SIZE = 999999
TEST_MAX_FLOW_TEXT_DAYS = 30
FB_TW_TOPIC_ABS_PATH = '/home/xnr1/xnr_0429/xnr/cron/topic_domain_facebook_twitter_v1/topic'
FB_DOMAIN_ABS_PATH = '/home/xnr1/xnr_0429/xnr/cron/topic_domain_facebook_twitter_v1/domain_facebook'

sys.path.append(FB_TW_TOPIC_ABS_PATH)
from test_topic import topic_classfiy
from config import name_list, zh_data

sys.path.append(FB_DOMAIN_ABS_PATH)
from domain_classify import domain_main



def merge_dict(x, y):
    for k, v in y.items():
        if k in x.keys():
            x[k] += v
        else:
            x[k] = v
    return x

def load_uid_list():
    uid_list = []
    uid_list_query_body = {'size': MAX_SEARCH_SIZE}
    try:
        search_results = es.search(index=facebook_user_index_name, doc_type=facebook_user_index_type, body=uid_list_query_body)['hits']['hits']
        for item in search_results:
            uid_list.append(item['_source']['uid'])
    except Exception,e:
        print e
    return uid_list

def load_timestamp(type='test'):
    # if type == 'test':
    #     timestamp =  datetime2ts(S_DATE_FB)
    # else:
    timestamp = time.time()
    return timestamp

def save_data2es(data):
    update_uid_list = []
    create_uid_list = []
    try:
        for uid, d in data.items():
            if es.exists(index=fb_portrait_index_name, doc_type=fb_portrait_index_type, id=uid):
                update_uid_list.append(uid)
            else:
                create_uid_list.append(uid)
        #bulk create
        if create_uid_list:
            bulk_create_action = []
            count = 0
            for uid in create_uid_list:
                create_action = {'index':{'_id': uid}}
                bulk_create_action.extend([create_action, data[uid]])
                count += 1
                if count % 5000 == 0:
                    es.bulk(bulk_create_action, index=fb_portrait_index_name, doc_type=fb_portrait_index_type)
                    bulk_create_action = []
            if bulk_create_action:
                result = es.bulk(bulk_create_action, index=fb_portrait_index_name, doc_type=fb_portrait_index_type)
                if result['errors'] :
                    print result
                    return False
        #bulk update
        if update_uid_list:
            bulk_update_action = []
            count = 0
            for uid in update_uid_list:
                update_action = {'update':{'_id': uid}}
                bulk_update_action.extend([update_action, {'doc': data[uid]}])
                count += 1
                if count % 5000 == 0:
                    es.bulk(bulk_update_action, index=fb_portrait_index_name, doc_type=fb_portrait_index_type)
                    bulk_update_action = []
            if bulk_update_action:
                result = es.bulk(bulk_update_action, index=fb_portrait_index_name, doc_type=fb_portrait_index_type)
                if result['errors'] :
                    print result
                    return False
    except Exception,e:
        print e
        return False
    return True


def update_keywords(uid_list=[]):
    if not uid_list:
        uid_list = load_uid_list()
    fb_flow_text_index_list = get_facebook_flow_text_index_list(load_timestamp(), TEST_MAX_FLOW_TEXT_DAYS)
    keywords_query_body={
      'post_filter': {
        'missing': {
          'field': 'keywords_string'
        }
      },
      'query': {
        "filtered": {
          "filter": {
            "bool": {
              "must": [
                {
                  "terms": {
                    "uid": uid_list
                  }
                },
                
              ]
            }
          }
        }
      },
      'size': MAX_SEARCH_SIZE,
      "sort": {
        "timestamp": {
          "order": "desc"
        }
      },
      "fields": [
        "keywords_dict",
        "uid"
      ]
    }
    user_keywords = {}
    for index_name in fb_flow_text_index_list:
        try:
            search_results = es.search(index=index_name, doc_type=facebook_flow_text_index_type, body=keywords_query_body)['hits']['hits']
            for item in search_results:
                content = item['fields']
                uid = content['uid'][0]
                if not uid in user_keywords:
                    user_keywords[uid] = {
                        'keywords': {}
                    }
                if content.has_key('keywords_dict'):
                    user_keywords[uid]['keywords'] = merge_dict(user_keywords[uid]['keywords'], json.loads(content['keywords_dict'][0]))
        except Exception,e:
            print e
    for uid in uid_list:
        if uid in user_keywords:
            content = user_keywords[uid]
            temp_keywords = {}
            if len(content['keywords']) >= 50:
                for item in sorted(content['keywords'].items(), lambda x, y: cmp(x[1], y[1]), reverse=True)[:50]:
                    temp_keywords[item[0]] = item[1]
            else:
                temp_keywords = content['keywords']
            user_keywords[uid]['keywords'] = json.dumps(temp_keywords)
            user_keywords[uid]['keywords_string'] = '&'.join(temp_keywords.keys())
        else:
            user_keywords[uid] = {
                'keywords': json.dumps({}),
                'keywords_string': ''   
            }
    return save_data2es(user_keywords)


def update_hashtag(uid_list=[]):
    if not uid_list:
        uid_list = load_uid_list()
    fb_flow_text_index_list = get_facebook_flow_text_index_list(load_timestamp(), TEST_MAX_FLOW_TEXT_DAYS)
    keywords_query_body = {
        'query':{
            "filtered":{
                "filter": {
                    "bool": {
                        "must": [
                            {"terms": {"uid": uid_list}},
                        ]
                     }
                }
            }
        },
        'size': MAX_SEARCH_SIZE,
        "sort": {"timestamp": {"order": "desc"}},
        "fields": ["hashtag", "uid"]
    }
    user_hashtag = {}
    for index_name in fb_flow_text_index_list:
        try:
            search_results = es.search(index=index_name, doc_type=facebook_flow_text_index_type, body=keywords_query_body)['hits']['hits']
            for item in search_results:
                content = item['fields']
                uid = content['uid'][0]
                if not uid in user_hashtag:
                    user_hashtag[uid] = {
                        'hashtag_list': []
                    }
                if content.has_key('hashtag'):
                    hashtag = content['hashtag'][0]
                    if hashtag:
                        hashtag_list = hashtag.split('&') 
                        user_hashtag[uid]['hashtag_list'].extend(hashtag_list)
        except Exception,e:
            print e
    for uid in uid_list:
        if uid in user_hashtag:
            content = user_hashtag[uid]
            hashtag_list = user_hashtag[uid]['hashtag_list']
            user_hashtag[uid] = {
                'hashtag': '&'.join(list(set(hashtag_list)))
            }
        else:
            user_hashtag[uid] = {
                'hashtag': ''
            }
    return save_data2es(user_hashtag)

def update_influence(uid_list=[]):
    if not uid_list:
        uid_list = load_uid_list()
    fb_bci_index_list = get_fb_bci_index_list(load_timestamp(), TEST_MAX_FLOW_TEXT_DAYS)
    fb_influence_query_body = {
        'query':{
            "filtered":{
                "filter": {
                    "bool": {
                        "must": [
                            {"terms": {"uid": uid_list}},
                        ]
                     }
                }
            }
        },
        'size': MAX_SEARCH_SIZE,
        "sort": {"timestamp": {"order": "desc"}},
        "fields": ["influence", "uid"]
    }
    user_influence = {}
    for index_name in fb_bci_index_list:
        try:
            search_results = es.search(index=index_name, doc_type=fb_bci_index_type, body=fb_influence_query_body)['hits']['hits']
            for item in search_results:
                content = item['fields']
                uid = content['uid'][0]
                if not uid in user_influence:
                    user_influence[uid] = {
                        'influence_list': []
                    }
                if content.has_key('influence'):
                    user_influence[uid]['influence_list'].append(float(content.get('influence')[0]))
        except Exception,e:
            print e
    for uid in uid_list:
        if uid in user_influence:
            content = user_influence[uid]
            if not sum(content['influence_list']):
                influence = 0.0
            else:
                influence = float(sum(content['influence_list']))/len(content['influence_list'])
            content['influence'] = influence
            content.pop('influence_list')
        else:
            user_influence[uid] = {
                'influence': 0.0
            } 
    return save_data2es(user_influence)

def update_sensitive(uid_list=[]):
    if not uid_list:
        uid_list = load_uid_list()
    fb_flow_text_index_list = get_facebook_flow_text_index_list(load_timestamp(), TEST_MAX_FLOW_TEXT_DAYS)
    sensitive_query_body = {
        'query':{
            "filtered":{
                "filter": {
                    "bool": {
                        "must": [
                            {"terms": {"uid": uid_list}},
                        ]
                     }
                }
            }
        },
        'size': MAX_SEARCH_SIZE,
        "sort": {"timestamp": {"order": "desc"}},
        "fields": ["sensitive_words_dict", "sensitive", "uid"]
    }
    user_sensitive = {}
    for index_name in fb_flow_text_index_list:
        try:
            search_results = es.search(index=index_name, doc_type=facebook_flow_text_index_type, body=sensitive_query_body)['hits']['hits']
            for item in search_results:
                content = item['fields']
                uid = content['uid'][0]
                if not uid in user_sensitive:
                    user_sensitive[uid] = {
                        'sensitive_dict': {},
                        'sensitive_list': []
                    }
                if content.has_key('sensitive_words_dict'):
                    user_sensitive[uid]['sensitive_dict'] = merge_dict(user_sensitive[uid]['sensitive_dict'], json.loads(content['sensitive_words_dict'][0]))
                if content.has_key('sensitive'):
                    user_sensitive[uid]['sensitive_list'].append(float(content.get('sensitive')[0]))
        except Exception,e:
            print e
    for uid in uid_list:
        if uid in user_sensitive:
            content = user_sensitive[uid]
            user_sensitive[uid]['sensitive_string'] = '&'.join(content['sensitive_dict'].keys())
            user_sensitive[uid]['sensitive_dict'] = json.dumps(content['sensitive_dict'])
            if not sum(content['sensitive_list']):
                sensitive = 0.0
            else:
                sensitive = float(sum(content['sensitive_list']))/len(content['sensitive_list'])
            content['sensitive'] = sensitive
            user_sensitive[uid]['sensitive'] = sensitive
            content.pop('sensitive_list')
        else:
            user_sensitive[uid] = {
                'sensitive': 0,
                'sensitive_string': '',
                'sensitive_dict': json.dumps({})

            }
    return save_data2es(user_sensitive)

def update_sentiment(uid_list=[]):
    '''
    SENTIMENT_DICT_NEW = {'0':u'中性', '1':u'积极', '2':u'生气', '3':'焦虑', \
         '4':u'悲伤', '5':u'厌恶', '6':u'消极其他', '7':u'消极'}
    '''
    if not uid_list:
        uid_list = load_uid_list()
    fb_flow_text_index_list = get_facebook_flow_text_index_list(load_timestamp(), TEST_MAX_FLOW_TEXT_DAYS)
    sentiment_query_body = {
        'query':{
            "filtered":{
                "filter": {
                    "bool": {
                        "must": [
                            {"terms": {"uid": uid_list}},
                        ]
                     }
                }
            }
        },
        'size': MAX_SEARCH_SIZE,
        "sort": {"timestamp": {"order": "desc"}},
        "fields": ["sentiment", "uid"]
    }
    user_sentiment = {}
    for index_name in fb_flow_text_index_list:
        try:
            search_results = es.search(index=index_name, doc_type=facebook_flow_text_index_type, body=sentiment_query_body)['hits']['hits']
            for item in search_results:
                content = item['fields']
                uid = content['uid'][0]
                if not uid in user_sentiment:
                    user_sentiment[uid] = {
                        'sentiment_list': []
                    }
                if content.has_key('sentiment'):
                    user_sentiment[uid]['sentiment_list'].append(int(content.get('sentiment')[0]))        
        except Exception,e:
            print e
    for uid in uid_list:
        if uid in user_sentiment:
            content = user_sentiment[uid]
            if content['sentiment_list']:
                sentiment = Counter(content['sentiment_list']).most_common(1)[0][0]
            else:
                sentiment = 0
            content['sentiment'] = sentiment
            content.pop('sentiment_list')
        else:
            user_sentiment[uid] = {
                'sentiment': 0
            }
    return save_data2es(user_sentiment)

def count_text_num(uid_list, fb_flow_text_index_list):
    count_result = {}
    #QQ那边好像就是按照用户来count的    https://github.com/huxiaoqian/xnr1/blob/82ff9704792c84dddc3e2e0f265c46f3233a786f/xnr/qq_xnr_manage/qq_history_count_timer.py
    for uid in uid_list:
        textnum_query_body = {
            'query':{
                "filtered":{
                    "filter": {
                        "bool": {
                            "must": [
                                {"term": {"uid": uid}},
                            ]
                         }
                    }
                }
            }
        }
        text_num = 0
        for index_name in fb_flow_text_index_list:
            try:
                result = es.count(index=index_name, doc_type=facebook_flow_text_index_type,body=textnum_query_body)
                if result['_shards']['successful'] != 0:
                    text_num += result['count']
            except Exception,e:
                # print e
                pass
        count_result[uid] = text_num
    return count_result

def trans_bio_data(bio_data):
    count = 1.0
    while True:
        translated_bio_data = trans(bio_data)
        if len(translated_bio_data) == len(bio_data):
            break
        else:
            print 'sleep start ...'
            time.sleep(count)
            count = count*1.1
            print 'sleep over ...'
    return translated_bio_data

def update_domain(uid_list=[]):
    if not uid_list:
        uid_list = load_uid_list()
    fb_flow_text_index_list = get_facebook_flow_text_index_list(load_timestamp(), TEST_MAX_FLOW_TEXT_DAYS)
    user_domain_data = {}
    #load num of text
    count_result = count_text_num(uid_list, fb_flow_text_index_list)
    #load baseinfo
    fb_user_query_body = {
        'post_filter': {
            'exists': {
                'field': 'bio_str'
            }
        },
        'query':{
            "filtered":{
                "filter": {
                    "bool": {
                        "must": [
                            {"terms": {"uid": uid_list}},
                        ]
                     }
                }
            }
        },
        'size': MAX_SEARCH_SIZE,
        "fields": ["bio_str", "category", "uid"]
    }
    try:
        search_results = es.search(index=facebook_user_index_name, doc_type=facebook_user_index_type, body=fb_user_query_body)['hits']['hits']
        for item in search_results:
            content = item['fields']
            uid = content['uid'][0]
            if not uid in user_domain_data:
                text_num = count_result[uid]
                user_domain_data[uid] = {
                    'bio_str': '',
                    'category': '',
                    'number_of_text': text_num
                }
            #对于长文本，Goslate 会在标点换行等分隔处把文本分拆为若干接近 2000 字节的子文本，再一一查询，最后将翻译结果拼接后返回用户。通过这种方式，Goslate 突破了文本长度的限制。
            if content.has_key('category'):
                category = content.get('category')[0]
            else:
                category = ''
            if content.has_key('bio_str'):
                bio_str = content.get('bio_str')[0]
            else:
                bio_str = ''  
            user_domain_data[uid]['bio_str'] = bio_str
            user_domain_data[uid]['category'] = category
    except Exception,e:
        print e
    #domian计算
    user_domain_temp = domain_main(user_domain_data) 
    user_domain = {}
    for uid in uid_list:
        if uid in user_domain_temp:
            user_domain[uid] = {
                'domain': user_domain_temp[uid]
            }
        else:
            user_domain[uid] = {'domain': 'other'}
    return save_data2es(user_domain)

def update_topic(uid_list=[]):
    if not uid_list:
        uid_list = load_uid_list()
    fb_flow_text_index_list = get_facebook_flow_text_index_list(load_timestamp(), TEST_MAX_FLOW_TEXT_DAYS)
    user_topic_data = get_filter_keywords(fb_flow_text_index_list, uid_list)
    user_topic_dict, user_topic_list = topic_classfiy(uid_list, user_topic_data)
    
    user_topic_string = {}
    for uid, topic_list in user_topic_list.items():
        li = []
        for t in topic_list:
            li.append(zh_data[name_list.index(t)].decode('utf8'))
        user_topic_string[uid] = '&'.join(li)
    user_topic = {}
    for uid in uid_list:
        if uid in user_topic_dict:
            user_topic[uid] = {
                'filter_keywords': json.dumps(user_topic_data[uid]),
                'topic': json.dumps(user_topic_dict[uid]),
                'topic_string': user_topic_string[uid]
            }
        else:
            user_topic[uid] = {
                'filter_keywords': json.dumps({}),
                'topic': json.dumps({}),
                'topic_string': ''
            }
    return save_data2es(user_topic)

def get_user_location(location_dict):
    if location_dict.has_key('name'):
        location = location_dict['name']
    elif location_dict.has_key('country') and location_dict.has_key('city'):
        location = location_dict['city'] + ', ' + location_dict['country']
    else:
        location = ''
    return location

def update_baseinfo(uid_list=[]):
    user_baseinfo = {}
    fb_user_query_body = {
        'query':{
            "filtered":{
                "filter": {
                    "bool": {
                        "must": [
                            {"terms": {"uid": uid_list}},
                        ]
                     }
                }
            }
        },
        'size': MAX_SEARCH_SIZE,
        "fields": ["location", "gender", "name", "uid"]
    }
    search_results = es.search(index=facebook_user_index_name, doc_type=facebook_user_index_type, body=fb_user_query_body)['hits']['hits']
    for item in search_results:
        content = item['fields']
        uid = content['uid'][0]
        if not uid in user_baseinfo:
            user_baseinfo[uid] = {
                'uid': str(uid),
                'uname': '',
                'gender': 0,
                'location': '',
            }
        location = ''
        if content.has_key('location'):
            location_dict = json.loads(content.get('location')[0])
            location = get_user_location(location_dict)
        gender = 0
        if content.has_key('gender'):
            gender_str = content.get('gender')[0]
            if gender_str == 'male':
                gender = 1
            elif gender_str == 'female':
                gender = 2
        uname = ''
        if content.has_key('name'):
            uname = content.get('name')[0]
        user_baseinfo[uid]['location'] = location
        user_baseinfo[uid]['gender'] = gender
        user_baseinfo[uid]['uname'] = uname
    for uid in uid_list:
        if not uid in user_baseinfo:
            user_baseinfo[uid] = {
                'uid': str(uid),
                'uname': '',
                'gender': 0,
                'location': '',
            }
    return save_data2es(user_baseinfo)

def update_all(uid_list=[]):
    time_list = []
    time_list.append(time.time())

    flag = False
    if uid_list:    #如果没有提供uid_list，则是日常更新，按照属性的周更新和日更新来。如果提供了则所有的属性都要更新。
        flag = True
    else:
        uid_list = load_uid_list()
        if not ((datetime2ts(ts2datetime(time.time())) - datetime2ts(S_DATE_FB)) % (WEEK*DAY)):
            flag = True

    print 'total num: ', len(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

    #日更新
    print 'update_baseinfo: ', update_baseinfo(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

    print 'update_hashtag: ', update_hashtag(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

    print 'update_influence: ', update_influence(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

    print 'update_sensitive: ', update_sensitive(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

    #周更新
    # if flag:
    print 'update_keywords:', update_keywords(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]
    
    print 'update_sentiment: ', update_sentiment(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

    print 'update_domain: ', update_domain(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

    print 'update_topic: ', update_topic(uid_list)
    time_list.append(time.time())
    print 'time used: ', time_list[-1] - time_list[-2]

if __name__ == '__main__':
    update_all()
    # update_domain(load_uid_list()[:50])
# total num:  92
# time used:  0.0157630443573
# update_baseinfo:  True
# time used:  0.154299974442
# update_hashtag:  True
# time used:  0.46758389473
# update_influence:  True
# time used:  0.33092212677
# update_sensitive:  True
# time used:  0.285825967789
# update_keywords: True
# time used:  1.21863102913
# update_sentiment:  True
# time used:  0.325371980667
# update_domain:  True
# time used:  65.2284970284
# update_topic:  True
# time used:  12.6456358433


