# -*- coding:utf-8 -*-

'''
weibo information monitor function about database task
'''
import sys
import json
import time,datetime
from xnr.time_utils import ts2datetime,datetime2ts,ts2date,\
        ts2datetimestr,get_xnr_flow_text_index_listname,get_xnr_feedback_index_listname
from xnr.global_utils import es_flow_text,flow_text_index_name_pre,flow_text_index_type,\
                             es_xnr,weibo_xnr_fans_followers_index_name,weibo_xnr_fans_followers_index_type,\
                             es_user_profile,profile_index_name,profile_index_type,\
                             weibo_xnr_corpus_index_name,weibo_xnr_corpus_index_type,\
                             weibo_xnr_index_name,weibo_xnr_index_type,\
                             xnr_flow_text_index_name_pre,xnr_flow_text_index_type,\
                             es_user_portrait,weibo_bci_index_name_pre,weibo_bci_index_type,\
                             weibo_keyword_count_index_name,weibo_keyword_count_index_type,\
                             weibo_full_keyword_index_name,weibo_full_keyword_index_type,\
                             weibo_sensitive_post_index_name_pre,weibo_sensitive_post_index_type,\
                             weibo_active_user_index_name_pre,weibo_active_user_index_type
from xnr.weibo_publish_func import retweet_tweet_func,comment_tweet_func,like_tweet_func,follow_tweet_func                             
from xnr.parameter import MAX_FLOW_TEXT_DAYS,MAX_VALUE,DAY,MID_VALUE,MAX_SEARCH_SIZE,HOT_WEIBO_NUM,INFLUENCE_MIN
from xnr.save_weibooperate_utils import save_xnr_like,save_xnr_followers
from xnr.global_config import S_TYPE, S_DATE,S_DATE_BCI

import jieba.posseg as pseg

from textrank4zh import TextRank4Keyword, TextRank4Sentence


def extract_keywords(w_text):

    tr4w = TextRank4Keyword()
    tr4w.analyze(text=w_text, lower=True, window=4)
    k_dict = tr4w.get_keywords(100, word_min_len=2)

    return k_dict



#查询用户昵称
def get_user_nickname(uid):
    try:
        result=es_user_profile.get(index=profile_index_name,doc_type=profile_index_type,id=uid)
        user_name=result['_source']['nick_name']
    except:
        user_name=''
    return user_name

#lookup weibo_xnr concerned users
def lookup_weiboxnr_concernedusers(weiboxnr_id):
    try:
        result=es_xnr.get(index=weibo_xnr_fans_followers_index_name,doc_type=weibo_xnr_fans_followers_index_type,id=weiboxnr_id)
        followers_list=result['_source']['followers_list']
    except:
    	followers_list=[]
    return followers_list


#lookup keywords_string limit with xnr concerned users and time ranges
#input:from_ts,to_ts,weiboxnr_id
#output:keywords_dict,it's used to create wordcloud
#合并dict
def union_dict(*objs):
    #print 'objs:', objs[0]
    _keys=set(sum([obj.keys() for obj in objs],[]))
    _total={}

    for _key in _keys:
        _total[_key]=sum([int(obj.get(_key,0)) for obj in objs])

    return _total

#组织词云内容查询
def lookup_weibo_keywordstring(from_ts,to_ts,weiboxnr_id):
    now_time=int(time.time())
    time_gap = to_ts - from_ts
    test_time_gap = datetime2ts(ts2datetime(now_time)) - datetime2ts(S_DATE)
    #print 'from, to:', ts2date(from_ts), ts2date(to_ts)
    if S_TYPE == 'test':
        today_date_time = datetime2ts(S_DATE)
        from_ts = from_ts - test_time_gap
        to_ts = to_ts - test_time_gap
    else:
        today_date_time= datetime2ts(ts2datetime(now_time))
    
    #print 'from, to:', ts2date(from_ts), ts2date(to_ts)
    xnr_user_no=weiboxnr_id

    keywords_dict=dict()
    if to_ts > today_date_time:
        #今日词云信息统计
        today_kewords_dict=dict()
        #today_kewords_dict=lookup_today_keywords(today_date_time,to_ts,xnr_user_no)
        history_keywords_dict=lookup_history_keywords(from_ts,to_ts,xnr_user_no)
        keywords_dict=union_dict(today_kewords_dict,history_keywords_dict)
    else:
        keywords_dict=lookup_history_keywords(from_ts,to_ts,xnr_user_no)
    #print 'all keywords_dict:', keywords_dict
    return keywords_dict 


#查询历史词云信息
def lookup_history_keywords(from_ts,to_ts,xnr_user_no):
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[{'term':{'xnr_user_no':xnr_user_no}},
                        {'range':{'timestamp':{'gte':from_ts,'lte':to_ts}}}]
                    }
                }
            }
        },
        'size':100
    }
    #print 'from_ts:', ts2date(from_ts)
    #print 'to_ts:', ts2date(to_ts)
    es_result=es_xnr.search(index=weibo_keyword_count_index_name,\
            doc_type=weibo_keyword_count_index_type,body=query_body)['hits']['hits']
    if not es_result:
        es_result = dict()
        return es_result
    all_keywords_dict=dict()
    for item in es_result:
        keywords_dict = json.loads(item['_source']['keyword_value_string'])
        all_keywords_dict=union_dict(all_keywords_dict,keywords_dict)
    #print 'history keyword_dict:', all_keywords_dict
    return all_keywords_dict

#查询今日词云
def lookup_today_keywords(from_ts,to_ts,xnr_user_no):
    userslist=lookup_weiboxnr_concernedusers(xnr_user_no)
    query_body={
            'query':{
                'filtered':{
                    'filter':{
                        'bool':{
                            'must':[
                                {'terms':{'uid':userslist}},
                                {'range':{'timestamp':{'gte':from_ts,'lte':to_ts}}}
                            ]
                        }
                    }
                }
            },
            'aggs':{
                'keywords':{
                    'terms':{
                        'field':'keywords_string',
                        'size': 80
                    }
                }
            }
        }
    flow_text_index_name = flow_text_index_name_pre + ts2datetime(to_ts)
    try:
        flow_text_exist=es_flow_text.search(index=flow_text_index_name,doc_type=xnr_flow_text_index_type,\
                    body=query_body)['aggregations']['keywords']['buckets']
        word_dict = dict()

        word_dict_new = dict()
        keywords_string = ''
        for item in flow_text_exist:
            word = item['key']
            count = item['doc_count']
            word_dict[word] = count

            keywords_string += '&'
            keywords_string += item['key']

        k_dict = extract_keywords(keywords_string)

        for item_item in k_dict:
            keyword = item_item.word
            # print 'keyword::',keyword,type(keyword)
            if word_dict.has_key(keyword):
                word_dict_new[keyword] = word_dict[keyword]
            else:
                word_dict_new[keyword] = 1
            # print 'count:',word_dict_new[keyword] 
    except:
        word_dict_new = dict()
    return word_dict_new   

#lookup hot posts
#input:from_ts,to_ts,weiboxnr_id,classify_id,search_content,order_id
#output:weibo hot_posts content
def lookup_hot_posts(start_time,end_time,weiboxnr_id,classify_id,order_id):

#weiboxnr_id,classify_id暂时不用
    print "weiboxnr_id------------------------------------------------------------"
    print weiboxnr_id
    print 'post request start!!!!!'
    weibo_sensitive_post_index_name_list = []
    days_num = int((end_time - start_time)/DAY) + 1
    print 'days_num = int((end_time - start_time)/DAY) + 1-=-=-='
    print end_time, start_time, DAY
    print days_num
    for i in range(0,days_num):
        date_ts = end_time - i*DAY
        print 'date_ts, end_time, i, DAY-=-=-=-=-=-=-=-=-=-=-'
        print date_ts, end_time, i, DAY
        index_name = weibo_sensitive_post_index_name_pre + ts2datetime(date_ts)
        print index_name
        if es_xnr.indices.exists(index=index_name):
            weibo_sensitive_post_index_name_list.append(index_name)
            print 'has append -----------0000000000000000000000000000'
        print 'has not  append -----------0000000000000000000000000000'
    sort_condition_list = []
    if order_id==1:         #按时间排序
        sort_condition_list=[{'timestamp':{'order':'desc'}}] 
    
    elif order_id==2:       #按热度排序
        sort_condition_list=[{'retweeted':{'order':'desc'}}]

    elif order_id==3:       #按敏感度排序
        sort_condition_list=[{'sensitive':{'order':'desc'}}]

    
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[{'range':{'timestamp':{'gte':int(start_time),'lt':int(end_time)}}}]
                    }
                }
            }

        },
        'size':HOT_WEIBO_NUM,     
        'sort':sort_condition_list
        }
    try:
        es_result=es_xnr.search(index=weibo_sensitive_post_index_name_list,doc_type=weibo_sensitive_post_index_type,\
            body=query_body)['hits']['hits']
        hot_result=[]
        for item in es_result:
            hot_result.append(item['_source'])
    except:
        hot_result=[]

    return hot_result






'''
def lookup_hot_posts(from_ts,to_ts,weiboxnr_id,classify_id,order_id):
    print 'post request start!!!!!'
    #step 1 :adjust the time condition for time
    time_gap = to_ts - from_ts
    now_time = time.time()
    test_time_gap = datetime2ts(ts2datetime(now_time)) - datetime2ts(S_DATE)
    #print 'from, to:', from_ts, to_ts
    if S_TYPE == 'test':
        today_date_time = datetime2ts(S_DATE)
        from_ts = from_ts - test_time_gap
        #to_ts = to_ts - test_time_gap
        to_ts=from_ts + MAX_FLOW_TEXT_DAYS * DAY

    from_date_ts=datetime2ts(ts2datetime(from_ts))
    to_date_ts=datetime2ts(ts2datetime(to_ts))
    #print 'from_date_ts, to_date_ts:', ts2date(from_date_ts), ts2date(to_date_ts)
    #print from_date_ts,to_date_ts

    flow_text_index_name_list=[]
    days_num = (to_date_ts - from_date_ts)/DAY + 1
    for i in range(0,days_num):
        date_range_start_ts = to_date_ts - i*DAY
        date_range_start_datetime = ts2datetime(date_range_start_ts)
        index_name = flow_text_index_name_pre + date_range_start_datetime
        if es_flow_text.indices.exists(index=index_name):
            flow_text_index_name_list.append(index_name)
        else:
            pass
    print flow_text_index_name_list
    sort_condition_list = []
    if order_id==1:         #按时间排序
        sort_condition_list=[{'timestamp':{'order':'desc'}}] 
        #post_num = HOT_WEIBO_NUM        
    elif order_id==2:       #按热度排序
        sort_condition_list=[{'retweeted':{'order':'desc'}}]
        #post_num = HOT_WEIBO_NUM
    elif order_id==3:       #按敏感度排序
        # sort_condition_list=[{'sensitive':{'order':'desc'}}]
        # post_num = 150
        hot_result = search_sensitive_post(weiboxnr_id,classify_id,from_ts,to_ts)
    #else:                   #默认设为按时间排序
    #    sort_condition_list=[{'timestamp':{'order':'desc'}}]

    userslist=lookup_weiboxnr_concernedusers(weiboxnr_id)
    #全部用户 0，已关注用户 1，未关注用户-1
    range_time_list={'range':{'timestamp':{'gte':int(from_ts),'lt':int(to_ts)}}}
   # print range_time_list

    user_condition_list=[]
    if classify_id == 1:
        user_condition_list=[{'bool':{'must':[{'terms':{'uid':userslist}},range_time_list]}}]
    elif classify_id == 2:
        user_condition_list=[{'bool':{'must':[range_time_list],'must_not':[{'terms':{'uid':userslist}}]}}]
    elif classify_id == 0:
        user_condition_list=[{'bool':{'must':[range_time_list]}}]

    #print 'sort_condition_list',sort_condition_list
    #print 'user_condition_list',user_condition_list
    
    query_body={
        'query':{
            'filtered':{
                'filter':user_condition_list
            }

        },
        'size':HOT_WEIBO_NUM,     
        'sort':sort_condition_list
        }
    if order_id==3:
        pass
    else:
        try:
            es_result=es_flow_text.search(index=flow_text_index_name_list,doc_type=flow_text_index_type,\
            body=query_body)['hits']['hits']
            hot_result=[]
            for item in es_result:
                item['_source']['nick_name']=get_user_nickname(item['_source']['uid'])
                hot_result.append(item['_source'])
        except:
            hot_result=[]
    #print 'hot_result:', hot_result
    # post_result = remove_repeat(hot_result)
    return hot_result
'''

def search_sensitive_post(xnr_user_no,classify_id,start_time,end_time):
    weibo_sensitive_post_index_name_list = []
    days_num = int((end_time - start_time)/DAY) + 1
    for i in range(0,days_num):
        date_ts = end_time - i*DAY
        index_name = weibo_sensitive_post_index_name_pre + ts2datetime(date_ts)
        if es_xnr.indices.exists(index=index_name):
            weibo_sensitive_post_index_name_list.append(index_name)
    if classify_id == 0:
        search_condition = [{'term':{'xnr_user_no':xnr_user_no}},{'range':{'timestamp':{'gte':start_time,'lte':end_time}}}]
    elif classify_id == 2:#未关注
        search_condition = [{'term':{'xnr_user_no':xnr_user_no}},{'range':{'timestamp':{'gte':start_time,'lte':end_time}}},{'term':{'search_type':-1}}]
    elif classify_id == 1:
        search_condition = [{'term':{'xnr_user_no':xnr_user_no}},{'range':{'timestamp':{'gte':start_time,'lte':end_time}}},{'term':{'search_type':1}}]



    query_body = {
        'query':{
            'filtered':{
                'filter':{
                'bool':{
                    'must':search_condition
                }
                }
            }
        },
        'size':HOT_WEIBO_NUM,
        'sort':{'sensitive':{'order':'desc'}}
    }
    try:
        es_result=es_xnr.search(index=weibo_sensitive_post_index_name_list,doc_type=weibo_sensitive_post_index_type,\
            body=query_body)['hits']['hits']
        hot_result=[]
        for item in es_result:
            hot_result.append(item['_source'])
    except:
        hot_result=[]

    return hot_result


def remove_repeat(post_result):
    origin_list = []
    filter_ids = []
    post_result_2 = post_result
    #print 'len post', len(post_result)
    for i in range(0,len(post_result)):
        set_mark = set_intersection(post_result[i]['mid'],filter_ids)
        #if not post_result[i]['mid'] in filter_ids:
        if set_mark == 0:
            for j in range(i+1,len(post_result_2)):
                re = filterDouble(post_result[i], post_result_2[j])
                #print 're:::',re
                if not re == 'not':
                    filter_ids.append(re)
    #print 'filter', len(set(filter_ids))
    new_post_results = [d for d in post_result if d['mid'] not in filter_ids]
    #print '^^^^^', len(new_post_results)
    return new_post_results

def filterDouble(doc1, doc2):
    #print doc1['text'],doc1['mid']
    #print doc2['text'],doc2['mid']
    doc1_text = [w for w in pseg.cut(doc1['text'])]
    doc2_text = [w for w in pseg.cut(doc2['text'])]
    #rint len(doc1_text), len(doc2_text)
    #print doc1_text
    #print doc2_text
    if len(set(doc1_text)) == 0 or len(set(doc2_text))==0:
        simi_A = 0
        simi_B = 0
    else:
        simi_A = float(len(list(set(doc1_text)&set(doc2_text))))/len(set(doc1_text))
        simi_B = float(len(list(set(doc1_text)&set(doc2_text))))/len(set(doc2_text))
    #print 'simi::',simi_A,simi_B
    if (simi_A > 0.75) or (simi_B > 0.75):
        if simi_A > simi_B:
            return doc1['mid']
        else:
            return doc2['mid']
    else:
        return 'not'

#交集判断
def set_intersection(str_A,list_B):
    list_A=[]
    list_A.append(str_A)
    set_A = set(list_A)
    set_B = set(list_B)
    result = set_A & set_B
    number = len(result)
    return number

#微博操作##########
#转发微博
def get_weibohistory_retweet(task_detail):
    text=task_detail['text']
    r_mid=task_detail['r_mid']

    xnr_user_no=task_detail['xnr_user_no']
    xnr_es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    account_name=xnr_es_result['weibo_mail_account']
    password=xnr_es_result['password']

    #调用转发微博函数
    mark=retweet_tweet_func(account_name,password,text,r_mid)
    
    # 保存微博，将转发微博保存至flow_text_表
    ###########################################
    return mark

#评论
def get_weibohistory_comment(task_detail):
    text=task_detail['text']
    r_mid=task_detail['r_mid']

    xnr_user_no=task_detail['xnr_user_no']
    xnr_es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    account_name=xnr_es_result['weibo_mail_account']
    password=xnr_es_result['password']

    #调用评论微博函数
    mark=comment_tweet_func(account_name,password,text,r_mid)
    
    # 保存评论，将评论内容保存至表
    ###########################################
    return mark

#赞
def get_weibohistory_like(task_detail):
    root_mid=task_detail['r_mid']

    xnr_user_no=task_detail['xnr_user_no']
    xnr_es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    account_name=xnr_es_result['weibo_mail_account']
    password=xnr_es_result['password']
    root_uid=xnr_es_result['uid']

    xnr_result=es_xnr.get(index=weibo_xnr_fans_followers_index_name,doc_type=weibo_xnr_fans_followers_index_type,id=xnr_user_no)['_source']
    if xnr_result['followers_list']:
        followers_list=xnr_result['followers_list']
    else:
        followers_list=[]

    if xnr_result['fans_list']:
        fans_list=xnr_result['fans_list']
    else:
        fans_list=[]

    #调用点赞函数
    mark=like_tweet_func(account_name,password,root_mid)

    #保存点赞信息至表
    uid=task_detail['uid']
    photo_url=task_detail['photo_url']
    nick_name=task_detail['nick_name']
    timestamp=task_detail['timestamp']
    text=task_detail['text']
    update_time=task_detail['update_time']
    mid=root_uid+'_'+root_mid

    if uid not in followers_list:
        if uid not in fans_list:
            weibo_type='stranger'
        else:
            weibo_type='fans'
    else:
        if uid not in fans_list:
            weibo_type='follow'
        else:
            weibo_type='friend'

    like_info=[uid,photo_url,nick_name,mid,timestamp,text,root_mid,root_uid,weibo_type,update_time]
    save_mark=save_xnr_like(like_info)

    return mark,save_mark


#直接关注
def attach_fans_follow(task_detail):
    xnr_user_no=task_detail['xnr_user_no']
    xnr_es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    account_name=xnr_es_result['weibo_mail_account']
    password=xnr_es_result['password']

    follower_uid=task_detail['uid']
    trace_type=task_detail['trace_type']

    #调用关注函数
    
    mark=follow_tweet_func(xnr_user_no,account_name,password,follower_uid,trace_type)
    #保存至关注列表
    #if mark:
    #    save_mark=save_xnr_followers(xnr_user_no,follower_uid)
    #else:
    #    save_mark=False

    return mark

###加入语料库
#task_detail=[corpus_type,theme_daily_name,text,uid,mid,timestamp,retweeted,comment,like,create_type]
def addto_weibo_corpus(task_detail):
    corpus_type=task_detail[0]
    theme_daily_name=task_detail[1]
    text=task_detail[2]
    uid=task_detail[3]
    mid=task_detail[4]
    timestamp=task_detail[5]
    retweeted=task_detail[6]
    comment=task_detail[7]
    like=task_detail[8]
    create_type=task_detail[9]
    xnr_user_no=task_detail[10]
    create_time=int(time.time())

    corpus_id=task_detail[4]    #mid

    try:
        es_xnr.index(index=weibo_xnr_corpus_index_name,doc_type=weibo_xnr_corpus_index_type,id=corpus_id,\
            body={'corpus_type':corpus_type,'theme_daily_name':theme_daily_name,'text':text,'uid':uid,'mid':mid,\
            'timestamp':timestamp,'retweeted':retweeted,'comment':comment,'like':like,'create_type':create_type,\
            'create_time':create_time,'xnr_user_no':xnr_user_no})
        result=True
    except:
        result=False
    return result


#task_detail=(corpus_type,theme_daily_name,create_type,xnr_user_no,mid,uid,timestamp,create_time)
def new_addto_weibo_corpus(task_detail):
    flow_text_index_name = flow_text_index_name_pre + ts2datetime(task_detail['timestamp'])
    try:
        corpus_result = es_flow_text.get(index=flow_text_index_name,doc_type=flow_text_index_type,id=task_detail['mid'])['_source']
        task_detail['text']=corpus_result['text']
        task_detail['retweeted']=corpus_result['retweeted']
        task_detail['comment']=corpus_result['comment']
        task_detail['like']=corpus_result['like']
    except:
        mark=False

    try:
        es_xnr.index(index=weibo_xnr_corpus_index_name,doc_type=weibo_xnr_corpus_index_type,id=task_detail['mid'],body=task_detail)
        mark=True
    except:
        mark=False
    return mark


###############################################################
#批量添加关注
def attach_fans_batch(xnr_user_no_list,fans_id_list,trace_type):
    for xnr_user_no in xnr_user_no_list:
        xnr_es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
        account_name=xnr_es_result['weibo_mail_account']
        password=xnr_es_result['password']

        mark_list=[]
        save_mark_list=[]
        #调用关注函数：
        for uid in fans_id_list:
            mark=follow_tweet_func(xnr_user_no,account_name,password,uid,trace_type)
            #mark=follow_tweet_func(account_name,password,uid)
            mark_list.append(mark)
            #保存至关注列表
            #if mark:
            #    save_mark=save_xnr_followers(xnr_user_no,uid)
            #else:
            #    save_mark=False
            #save_mark_list.append(save_mark)
    return mark_list

#lookup acitve_user
#input:classify_id,weiboxnr_id
#output:active weibo_user info list
def lookup_active_weibouser(classify_id,weiboxnr_id,start_time,end_time):
    start_datetime = datetime2ts(ts2datetime(start_time-DAY))
    end_datetime = datetime2ts(ts2datetime(end_time-DAY))
    weibo_active_user_index_name_list = []
    if start_datetime == end_datetime:
        index_name=weibo_active_user_index_name_pre + ts2datetime(end_datetime)
        if es_xnr.indices.exists(index=index_name):
            weibo_active_user_index_name_list.append(index_name)
    else:
        day_num = int((end_datetime - start_datetime)/DAY) 
        for i in range(0,day_num):
            temp_date = ts2datetime(end_datetime - i*DAY)
            index_name = weibo_active_user_index_name_pre + temp_date
            if es_xnr.indices.exists(index=index_name):
                weibo_active_user_index_name_list.append(index_name)

    query_body={
        'query':{
            'match_all':{}
        },
        'size':100,
        'sort':{'influence':{'order':'desc'}}
    }
    results = []
   
    try:
        #print weibo_active_user_index_name_list
        result = es_xnr.search(index=weibo_active_user_index_name_list,doc_type=weibo_active_user_index_type,body=query_body)['hits']['hits']
        for item in result:
            results.append(item['_source'])
       # print results
    except:
       print 'active_user error!!'
    return results

'''
def lookup_active_weibouser(classify_id,weiboxnr_id,start_time,end_time):
    print 'active user start!!!'
    time_gap = end_time - start_time
    now_time = time.time()
    test_time_gap = datetime2ts(ts2datetime(now_time)) - datetime2ts(S_DATE_BCI)
    #print 'from, to:', ts2date(start_time), ts2date(end_time)
    today_date_time = end_time - DAY
    if S_TYPE == 'test':
        today_date_time = datetime2ts(S_DATE_BCI)
        start_time = start_time - test_time_gap
        end_time = end_time - test_time_gap

    from_date_ts=datetime2ts(ts2datetime(start_time))
    to_date_ts=datetime2ts(ts2datetime(end_time))
    #print 's_date_bci:', S_DATE_BCI
    #print 'from_date_ts, to_date_ts:', ts2date(from_date_ts), ts2date(to_date_ts)
     
    bci_index_name = weibo_bci_index_name_pre + ''.join(ts2datetime(today_date_time).split('-'))
   # print 'bci_index_name:', bci_index_name
    #print 'end_time:', ts2date(end_time)

    #step1: users condition
    #make sure the users range by classify choice
    userlist = lookup_weiboxnr_concernedusers(weiboxnr_id)

    if classify_id == 1:      #concrenedusers
        condition_list=[{'bool':{'must':{'terms':{'uid':userlist}}}}]
    elif classify_id == 2:    #unconcrenedusers
        condition_list=[{'bool':{'must_not':[{'terms':{'uid':userlist}}]}}] 
    elif classify_id == 0:
        condition_list=[{'match_all':{}}]
    #print userlist,classify_id,condition_list

    #step 2:lookup users 
    user_max_index=count_maxweibouser_influence(end_time - DAY)
    results = []
    for item in condition_list:
        query_body={

            'query':item,
            'size':HOT_WEIBO_NUM,       #查询影响力排名前50的用户即可
            'sort':{'user_index':{'order':'desc'}}
            }
        try:
            #print 'query_body:', query_body
            flow_text_exist=es_user_portrait.search(index=bci_index_name,\
                    doc_type=weibo_bci_index_type,body=query_body)['hits']['hits']
            search_uid_list = [item['_source']['user'] for item in flow_text_exist]
            weibo_user_exist = es_user_profile.search(index=profile_index_name,\
                    doc_type=profile_index_type,body={'query':{'terms':{'uid':search_uid_list}}})['hits']['hits']
            #print 'weibo_user_exist:', weibo_user_exist
            weibo_user_dict = dict()
            for item in weibo_user_exist:
                uid = item['_source']['uid']
                weibo_user_dict[uid] = item['_source']
            for item in flow_text_exist:
                #print 'item:', item['_source']
                influence = item['_source']['user_index']/user_max_index*100
                fans_num = item['_source']['user_fansnum']
                friends_num = item['_source']['user_friendsnum']
                total_number = item['_source']['total_number']
                uid = item['_source']['user']
                try:
                    weibo_user_info = weibo_user_dict[uid]
                    uname = weibo_user_info['nick_name']
                    location = weibo_user_info['user_location']
                    url = weibo_user_info['photo_url']
                except:
                    uname = ''
                    location = ''
                    url = ''
                #print 'uid:', uid
                results.append({'uid':uid, 'influence':influence, 'fans_num':fans_num, \
                        'total_number':total_number, 'friends_num':friends_num,\
                        'uname': uname, 'location':location, 'url': url})
                #print 'results:', results
               
        except:
            results=[]

    return results
'''
#查询微博数
def count_weibouser_weibosum(uid,end_time):
    date_time=ts2datetimestr(end_time-DAY)
    index_name=xnr_flow_text_index_name_pre+date_time

    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'term':{'uid':uid}
                }
            }
        },
        'size':1,
        'sort':{'timestamp':{'order':'desc'}}
    }
    try:
        weibo_result=es_xnr.search(index=index_name,doc_type=xnr_flow_text_index_type,body=query_body)['hits']['hits']
        for item in weibo_result:
            weibos_sum=item['_source']['weibos_sum']
    except:
        weibos_sum=0
    return weibos_sum

#计算影响力
def count_maxweibouser_influence(end_time):
    date_time=ts2datetimestr(end_time)
    index_name=weibo_bci_index_name_pre+date_time
    #print 'max index_name:', index_name
    query_body={
        'query':{
            'match_all':{}
        },
        'size':1,
        'sort':{'user_index':{'order':'desc'}}
    }
    try:
        #if S_TYPE == 'test':
        #    temp_index_name='bci_20161121'
        #    max_result=es_user_profile.search(index=temp_index_name,doc_type=weibo_bci_index_type,body=query_body)['hits']['hits']
        #else:
        max_result=es_user_profile.search(index=index_name,doc_type=weibo_bci_index_type,body=query_body)['hits']['hits']
        for item in max_result:
           max_user_index=item['_source']['user_index']
    except:
        max_user_index=1
    return max_user_index

def count_weibouser_index(uid,end_time):
    try:
        if S_TYPE == 'test':
            temp_index_name='bci_20161121'
            user_result=es_user_profile.get(index=temp_index_name,doc_type=weibo_bci_index_type,id=uid)['_source']
        else:
            user_result=es_user_profile.get(index=index_name,doc_type=weibo_bci_index_type,id=uid)['_source']
        user_index=user_result['user_index']
    except:
        user_index=0
    return user_index

#weibo_user_detail
def weibo_user_detail(user_id):
    result=es_user_profile.get(index=profile_index_name,doc_type=profile_index_type,id=user_id)['_source']
    return result
            




#查询全网词云
#组织词云内容查询
def lookup_full_keywordstring(from_ts,to_ts):
    now_time=int(time.time())
    time_gap = to_ts - from_ts
    test_time_gap = datetime2ts(ts2datetime(now_time)) - datetime2ts(S_DATE)
    if S_TYPE == 'test':
        today_date_time = datetime2ts(S_DATE)
        from_ts = from_ts - test_time_gap
        to_ts = to_ts - test_time_gap
    else:
        today_date_time= datetime2ts(ts2datetime(now_time))

    

    keywords_dict=dict()
    if to_ts > today_date_time:
        #今日词云信息统计
        today_kewords_dict = dict()
       # today_kewords_dict=lookup_today_fullkeywords(today_date_time,to_ts)
        history_keywords_dict=lookup_history_fullkeywords(from_ts,to_ts)
        keywords_dict=union_dict(today_kewords_dict,history_keywords_dict)
    else:
        keywords_dict=lookup_history_fullkeywords(from_ts,to_ts)

    return keywords_dict 



#查询历史词云信息
def lookup_history_fullkeywords(from_ts,to_ts):
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                        {'range':{'timestamp':{'gte':from_ts,'lte':to_ts}}}]
                    }
                }
            }
        },
        'size':100
    }
    #print 'from_ts:', ts2date(from_ts)
    #print 'to_ts:', ts2date(to_ts)
    es_result=es_xnr.search(index=weibo_full_keyword_index_name,\
            doc_type=weibo_full_keyword_index_type,body=query_body)['hits']['hits']
    if not es_result:
        es_result = dict()
        return es_result
    all_keywords_dict=dict()
    for item in es_result:
        keywords_dict = json.loads(item['_source']['keyword_value_string'])
        all_keywords_dict=union_dict(all_keywords_dict,keywords_dict)
    #print 'history keyword_dict:', all_keywords_dict
    return all_keywords_dict

#查询今日词云
def lookup_today_fullkeywords(from_ts,to_ts):

    query_body={
            'query':{
                'filtered':{
                    'filter':{
                        'bool':{
                            'must':[
                                {'range':{'timestamp':{'gte':from_ts,'lte':to_ts}}}
                            ]
                        }
                    }
                }
            },
            'aggs':{
                'keywords':{
                    'terms':{
                        'field':'keywords_string',
                        'size': 80
                    }
                }
            }
        }
    flow_text_index_name = flow_text_index_name_pre + ts2datetime(to_ts)
    try:
        flow_text_exist=es_flow_text.search(index=flow_text_index_name,doc_type=xnr_flow_text_index_type,\
                    body=query_body)['aggregations']['keywords']['buckets']

        word_dict = dict()

        word_dict_new = dict()

        keywords_string = ''
        for item in flow_text_exist:
            word = item['key']
            count = item['doc_count']
            word_dict[word] = count

            keywords_string += '&'
            keywords_string += item['key']

        k_dict = extract_keywords(keywords_string)

        for item_item in k_dict:
            keyword = item_item.word
            # print 'keyword::',keyword,type(keyword)
            if word_dict.has_key(keyword):
                word_dict_new[keyword] = word_dict[keyword]
            else:
                word_dict_new[keyword] = 1
            # print 'count:',word_dict_new[keyword] 
    except:
        word_dict_new = dict()
    return word_dict_new    
