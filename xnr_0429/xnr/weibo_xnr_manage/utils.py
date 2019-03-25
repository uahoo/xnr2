#!/usr/bin/python
#-*- coding:utf-8 -*-
'''
use to save function about database
'''
import sys
import os
import time
import datetime
import json
sys.path.append("/home/xnr1/xnr_0429/")
from xnr.global_utils import es_user_portrait,es_xnr,weibo_xnr_index_name,weibo_xnr_index_type,\
                             weibo_xnr_fans_followers_index_name,weibo_xnr_fans_followers_index_type,\
                             es_user_profile,profile_index_name,profile_index_type,\
                             weibo_xnr_timing_list_index_name,weibo_xnr_timing_list_index_type,\
                             xnr_flow_text_index_name_pre,xnr_flow_text_index_type,\
                             weibo_feedback_retweet_index_name,weibo_feedback_retweet_index_name_pre,weibo_feedback_retweet_index_type,\
                             weibo_feedback_at_index_name,weibo_feedback_at_index_name_pre,weibo_feedback_at_index_type,\
                             weibo_feedback_comment_index_name,weibo_feedback_comment_index_name_pre,weibo_feedback_comment_index_type,\
                             weibo_feedback_like_index_name,weibo_feedback_like_index_name_pre,weibo_feedback_like_index_type,\
                             weibo_xnr_save_like_index_name,weibo_xnr_save_like_index_type,\
                             portrait_index_name,portrait_index_type,weibo_bci_index_name_pre,weibo_bci_index_type,\
                             weibo_xnr_assessment_index_name,weibo_xnr_assessment_index_type,\
                             weibo_xnr_count_info_index_name,weibo_xnr_count_info_index_type,\
                             weibo_date_remind_index_name,weibo_date_remind_index_type,\
                             weibo_feedback_follow_index_name,weibo_feedback_follow_index_type,\
                             weibo_feedback_fans_index_name,weibo_feedback_fans_index_type,\
                             new_xnr_flow_text_index_name_pre,new_xnr_flow_text_index_type,\
                             weibo_xnr_relations_index_name, weibo_xnr_relations_index_type
from xnr.parameter import HOT_WEIBO_NUM,MAX_VALUE,MAX_SEARCH_SIZE,DAY,FLOW_TEXT_START_DATE,REMIND_DAY
from xnr.data_utils import num2str
from xnr.time_utils import get_xnr_feedback_index_listname,get_timeset_indexset_list,get_xnr_flow_text_index_listname,\
                           ts2datetime,datetime2ts,ts2datetimestr,ts2yeartime
from xnr.weibo_publish_func import retweet_tweet_func,comment_tweet_func,like_tweet_func,unfollow_tweet_func,follow_tweet_func
from xnr.save_weibooperate_utils import save_xnr_like,delete_xnr_followers
from xnr.global_config import S_TYPE,XNR_CENTER_DATE_TIME,S_WEIBO_TEST_DATE,R_BEGIN_TIME

##获取索引
def get_xnr_set_index_listname(index_name_pre,date_range_start_ts,date_range_end_ts):
    index_name_list=[]
    if ts2datetime(date_range_start_ts) != ts2datetime(date_range_end_ts):
        iter_date_ts=date_range_end_ts
        while iter_date_ts >= date_range_start_ts:
            date_range_start_date=ts2datetime(iter_date_ts)
            index_name=index_name_pre+date_range_start_date
            if es_xnr.indices.exists(index=index_name):
                index_name_list.append(index_name)
            else:
                pass
            iter_date_ts=iter_date_ts-DAY
    else:
        date_range_start_date=ts2datetime(date_range_start_ts)
        index_name=index_name_pre+date_range_start_date
        if es_xnr.indices.exists(index=index_name):
            index_name_list.append(index_name)
        else:
            pass
    return index_name_list


##########################################
#	step 2：show weibo_xnr 	information  #
##########################################
def get_xnr_detail(xnr_user_no):
	try:
		results=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
		xnr_info=results
	except:
		xnr_info=[]
	return xnr_info

# step 2.1: show completed weibo_xnr information 
def show_completed_weiboxnr(account_no,now_time):
    query_body={
		'query':{
			'filtered':{
				'filter':{
					'bool':{
						'must':[
							{'term':{'submitter':account_no}},
                            {'term':{'create_status':2}}
						]
					}					
				}
			}

		},
		'size':MAX_VALUE
    }
    #print 'start_time:',time.time()
    results=es_xnr.search(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,body=query_body)['hits']['hits']
    result=[]
    #print 'xnr_search_time:',time.time()
    for item in results:
        xnr_list=item['_source']
        xnr_user_no=item['_source']['xnr_user_no']
        uid=item['_source']['uid']
        #粉丝数
        fans_num=count_fans_num(xnr_user_no)
        #print 'fans_num_time:',time.time()
        #历史发帖量
        history_post_num=count_history_post_num(xnr_user_no,now_time)
        #print 'history_post_num_time:',time.time()
        #历史评论数
        history_comment_num = count_xnr_comment(xnr_user_no,now_time,uid)
        #history_comment_num=count_history_comment_num(uid)
        #print 'history_comment_num：',time.time()
        #今日发帖量
        today_comment_num=count_today_comment_num(xnr_user_no,now_time)
        #print 'today_comment_num:',time.time()

        xnr_list['fans_num']=fans_num
        xnr_list['history_post_num']=history_post_num
        xnr_list['history_comment_num']=history_comment_num
        xnr_list['today_comment_num']=today_comment_num
        #xnr_list.extend(fans_num,history_post_num,history_comment_num,today_comment_num)
        #今日提醒
        today_remind=xnr_today_remind(xnr_user_no,now_time)
        #print 'today_remind:',time.time()
        today_remind_num=today_remind['remind_num']
        xnr_list['today_remind_num']=today_remind_num

        result.append(xnr_list)
    return result


#计算粉丝数
def count_fans_num(xnr_user_no):
    try:
        result=es_xnr.get(index=weibo_xnr_fans_followers_index_name,doc_type=weibo_xnr_fans_followers_index_type,id=xnr_user_no)['_source']
        #print "===========================result"
        #print "-------------------===========================--------------------------------result"
        #print result
        followers_list=result['fans_list']
        number=len(followers_list)
        #print number
    except:
        number=0
    return number

#计算历史发帖量
def count_history_post_num(xnr_user_no,now_time):
    #获取检索列表
    temp_weibo_xnr_flow_text_listname=get_xnr_feedback_index_listname(xnr_flow_text_index_name_pre,now_time)
    weibo_xnr_flow_text_listname=[]
    for index_name in temp_weibo_xnr_flow_text_listname:
        if es_xnr.indices.exists(index=index_name):
            weibo_xnr_flow_text_listname.append(index_name)
        else:
            pass
    #print 'weibo_xnr_flow_text_listname',weibo_xnr_flow_text_listname
    #定义检索规则
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'term':{'xnr_user_no':xnr_user_no}
                }
            }
        },
        'aggs':{
            'history_post_num':{
                'terms':{
                    'field':'xnr_user_no'
                }
            }
        }
    }
    try:
        results=es_xnr.search(index=weibo_xnr_flow_text_listname,doc_type=xnr_flow_text_index_type,\
            body=query_body)['aggregations']['history_post_num']['buckets']
        number=0
        for item in results:
            number=item['doc_count']
    except:
        number=0
    return number

#计算今日发帖量
def count_today_comment_num(xnr_user_no,now_time):
    #对时间进行处理，确定查询范围
    date_time=ts2datetime(now_time)
    weibo_xnr_flow_text_listname=xnr_flow_text_index_name_pre+date_time
    star_time=datetime2ts(date_time)
   # print ts2datetime(star_time),ts2datetime(now_time)
    #定义检索规则
    query_body={
        'query':{
            'filtered':{
                'filter':{
                'bool':{
                'must':[
                    {'term':{'xnr_user_no':xnr_user_no}}
                ]}}
            }
        },
        'size':MAX_VALUE
    }
    try:
        results=es_xnr.search(index=weibo_xnr_flow_text_listname,doc_type=xnr_flow_text_index_type,\
            body=query_body)['hits']['hits']
        number=len(results)
    except:
       # print  'except-today_post!'
        number=0
    return number

#计算历史评论数
def count_xnr_comment(xnr_user_no,todaytime,uid):
    task_id = xnr_user_no+'_'+ts2datetime(todaytime - DAY)
    try:
        result=es_xnr.get(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=task_id)['_source']
        result_num = result['comment_total_num']
    except:
        result_num = 0
    number = result_num + count_history_comment_num(uid)
    return number

def count_history_comment_num(uid):
    weibo_feedback_comment_index_name_list = get_xnr_set_index_listname(weibo_feedback_comment_index_name_pre,datetime2ts(ts2datetime(XNR_CENTER_DATE_TIME)),XNR_CENTER_DATE_TIME)
    #定义检索规则
   # print weibo_feedback_comment_index_name_list
    type_s = 'make'
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[{'term':{'uid':uid}},{'term':{'comment_type':type_s}}]
                    }
                }
            }
        }
    }
    #query_body_1 = {'query':{'match_all':{}}}
    try:
        result=es_xnr.search(index=weibo_feedback_comment_index_name_list,doc_type=weibo_feedback_comment_index_type,body=query_body)['hits']['hits']
    #print result
    # number=0
        number=len(result)
    except:
       # print 'comment-except!'
    	number=0
    #print 'comment_number',number
    return number

#step 2.2: show uncompleted weibo_xnr information 
def show_uncompleted_weiboxnr(account_no):
	query_body={
		'query':{
			'filtered':{
				'filter':{
					'bool':{
						'must':[

							{'term':{'submitter':account_no}},
							{'range':{
								'create_status':{
								'gte':0,
								'lte':1
								}
							}
							}

						]
					}					
				}
			}

		},
		'size':MAX_VALUE
	}
	try:
		results=es_xnr.search(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,body=query_body)['hits']['hits']
		result=[]
		for item in results:
			result.append(item['_source'])
	except:
		result=[]
	return result

#######################################
#	step 3：today remind (今日提醒)   #
#######################################
def xnr_today_remind(xnr_user_no,now_time):
	##发帖提醒
	#当前发帖量
    complete_num=count_today_comment_num(xnr_user_no,now_time)
    xnr_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    day_post_average_list=json.loads(xnr_result['day_post_average'])
    #最小目标发帖量
    if day_post_average_list[0].encode('utf-8'):
        min_post_num=int(day_post_average_list[0].encode('utf-8'))
    else:
    	min_post_num=0
    #min_post_num=min(int(day_post_average_list[0].encode('utf-8')),int(day_post_average_list[-1].encode('utf-8')))
    #目标发帖差额
    post_dvalue=min_post_num-complete_num

    if post_dvalue>0:
        post_remind_content='尚未完成发帖目标，今日请至少再发'+str(post_dvalue)+'条帖子！'
        post_remind_flag=1
    else:
        post_remind_content='恭喜您，发帖目标已完成！'
        post_remind_flag=0
    post_remind=[post_remind_flag,post_remind_content]

    ##日历提醒
    date_remind_flag=0
    date_remind_content=[]
    date_result=show_date_count(now_time)         #修改
    #print date_result
    for date_item in date_result:
        if (date_item['countdown_days']>0) and (date_item['countdown_days']<REMIND_DAY):
            date_remind_flag=date_remind_flag+1
            date_remind_content_temp=str(date_item['countdown_days'])+'天后是'+date_item['date_name'].encode('utf-8')+'纪念日，请注意！'
            date_remind_content.append(date_remind_content_temp)
    if date_remind_flag == 0:
        temp_remind='暂无日历提醒。'
        date_remind_content.append(temp_remind)
    else:
        pass
    date_remind=[date_remind_flag,date_remind_content]

    #设置提醒内容
    remind_content=dict()
    #显示消息条数
    remind_num=post_remind_flag+date_remind_flag
    remind_content['remind_num']=remind_num
    #发帖提醒设置
    remind_content['post_remind_content']=post_remind_content
    #日期提醒设置：
    remind_content['date_remind_content']=date_remind_content
    return remind_content

def show_date_count(today_time):
    query_body={
        'query':{
            'match_all':{}
        },
        'size':MAX_VALUE,
        'sort':{'date_time':{'order':'asc'}}
    }
    result=es_xnr.search(index=weibo_date_remind_index_name,doc_type=weibo_date_remind_index_type,body=query_body)['hits']['hits']
    #取出预警时间进行处理
    date_warming_result=[]
    for item in result:
        #计算距离日期
        date_time=item['_source']['date_time']
        year=ts2yeartime(today_time)
        warming_date=year+'-'+date_time
        today_date=ts2datetime(today_time)
        countdown_num=(datetime2ts(warming_date)-datetime2ts(today_date))/DAY

        item['_source']['countdown_days']=countdown_num
        date_warming_result.append(item['_source'])
        
    return date_warming_result

#############################################
#	step 4：operate count (进入，操作统计)  #
#############################################
#step 4.1：history count

#累计统计
def xnr_cumulative_statistics(xnr_date_info,xnr_user_no):
    Cumulative_statistics_dict=dict()
    Cumulative_statistics_dict['date_time']='累计统计'
    if xnr_date_info: 
        #print xnr_date_info[0]
        Cumulative_statistics_dict['user_fansnum']=count_fans_num(xnr_user_no) 
        #Cumulative_statistics_dict['user_fansnum']=xnr_date_info[-1]['user_fansnum']
        total_post_sum=0
        daily_post_num=0
        business_post_num=0
        hot_follower_num=0
        trace_follow_tweet_num=0
        influence_sum=0
        penetration_sum=0
        safe_sum=0
        number=len(xnr_date_info)
        for i in xrange(0,len(xnr_date_info)):
            #print xnr_date_info[i]['date_time']
            #total_post_sum=total_post_sum+xnr_date_info[i]['total_post_sum']
            daily_post_num=daily_post_num+xnr_date_info[i]['daily_post_num']
            business_post_num=business_post_num+xnr_date_info[i]['business_post_num']
            hot_follower_num=hot_follower_num+xnr_date_info[i]['hot_follower_num']
            trace_follow_tweet_num=trace_follow_tweet_num+xnr_date_info[i]['trace_follow_tweet_num']
            influence_sum=influence_sum+xnr_date_info[i]['influence']
            penetration_sum=penetration_sum+xnr_date_info[i]['penetration']
            safe_sum=safe_sum+xnr_date_info[i]['safe']
            #print total_post_sum,daily_post_num

        Cumulative_statistics_dict['total_post_sum']=daily_post_num+business_post_num+hot_follower_num+trace_follow_tweet_num
        Cumulative_statistics_dict['daily_post_num']=daily_post_num
        Cumulative_statistics_dict['business_post_num']=business_post_num
        Cumulative_statistics_dict['hot_follower_num']=hot_follower_num
        Cumulative_statistics_dict['trace_follow_tweet_num']=trace_follow_tweet_num
        Cumulative_statistics_dict['influence']=round(influence_sum/number,2)
        Cumulative_statistics_dict['penetration']=round(penetration_sum/number,2)
        Cumulative_statistics_dict['safe']=round(safe_sum/number,2)
        #Cumulative_statistics_dict['influence']=xnr_date_info[0]['influence']
        #Cumulative_statistics_dict['penetration']=xnr_date_info[0]['penetration']
        #Cumulative_statistics_dict['safe']=xnr_date_info[0]['safe']
    else:
    	Cumulative_statistics_dict['user_fansnum']=0
    	Cumulative_statistics_dict['total_post_sum']=0
        Cumulative_statistics_dict['daily_post_num']=0
        Cumulative_statistics_dict['business_post_num']=0
        Cumulative_statistics_dict['hot_follower_num']=0
        Cumulative_statistics_dict['trace_follow_tweet_num']=0
        Cumulative_statistics_dict['influence']=0
        Cumulative_statistics_dict['penetration']=0
        Cumulative_statistics_dict['safe']=0

    return Cumulative_statistics_dict

##从流数据中对今日信息进行统计

#查询虚拟人粉丝数
def get_today_xnr_fans(xnr_user_no):
    xnr_uid = xnr_user_no2uid(xnr_user_no)
    query_body = {
       'query':{
            'filtered':{
                'filter':{
                    'term':{'root_uid':xnr_uid}
                }
            }
        },
        'size':MAX_SEARCH_SIZE
    }
    try:
        search_result = es_xnr.search(index = weibo_feedback_fans_index_name,doc_type = weibo_feedback_fans_index_type,body = query_body)['hits']['hits']
       # print "search_fans_result::",search_result
        fans_num = len(search_result)
    except:
        fans_num = 0
    return fans_num

def show_today_history_count(xnr_user_no,start_time,end_time):
    xnr_date_info=[]
    date_time=ts2datetime(end_time)

    index_name=xnr_flow_text_index_name_pre+date_time

    xnr_user_detail=dict()
    xnr_user_detail['date_time']=date_time

    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term':{'xnr_user_no':xnr_user_no}},
                            {'range':{
                                'timestamp':{
                                    'gte':start_time,
                                    'lte':end_time
                                }
                            }}
                        ]
                    }                    
                }
            }
        },
        'aggs':{
            'all_task_source':{
                'terms':{
                    'field':'task_source'
                }
            }
        }
    }


    lookup_type='fans_list'
    #今日总粉丝数
    fans_list=lookup_xnr_fans_followers(xnr_user_no,lookup_type)
    xnr_user_detail['user_fansnum']= len(fans_list)   
    try:
        xnr_result=es_xnr.search(index=index_name,doc_type=xnr_flow_text_index_type,body=query_body)
        print xnr_result
       # print 'xnr_result:::',xnr_result
        #今日总粉丝数
        #fans_list=lookup_xnr_fans_followers(user_id,lookup_type)
        #xnr_user_detail['user_fansnum']= len(fans_list)
        #xnr_user_detail['user_fansnum']=get_today_xnr_fans(xnr_user_no)
        #print "search_fans_result::",search_result
        
        if not xnr_result['hits']['hits']:
            print "not ----------------------------------hits hits--------------------------------"
            # xnr_user_detail['user_fansnum']=0
            #xnr_user_detail['daily_post_num']=2
            #xnr_user_detail['business_post_num']=1
            #xnr_user_detail['hot_follower_num']=2
            #xnr_user_detail['total_post_sum']=6
            #xnr_user_detail['trace_follow_tweet_num']=1
        else:

            # for item in xnr_result['hits']['hits']:            
                # xnr_user_detail['user_fansnum']=item['_source']['user_fansnum']
            # daily_post-日常发帖,hot_post-热点跟随,business_post-业务发帖
            for item in xnr_result['aggregations']['all_task_source']['buckets']:
                if item['key'] == 'daily_post':
                    xnr_user_detail['daily_post_num']=item['doc_count']
                elif item['key'] == 'business_post':
                    xnr_user_detail['business_post_num']=item['doc_count']
                elif item['key'] == 'hot_post':
                    xnr_user_detail['hot_follower_num']=item['doc_count']
                elif item['key'] =='trace_follow_tweet':
                    xnr_user_detail['trace_follow_tweet_num']=item['doc_count']
            #总发帖量
            if xnr_user_detail.has_key('daily_post_num'):
                pass
            else:
                xnr_user_detail['daily_post_num']=0
            
            if xnr_user_detail.has_key('business_post_num'):
                pass
            else:
                xnr_user_detail['business_post_num']=0

            if xnr_user_detail.has_key('hot_follower_num'):
                pass
            else:
                xnr_user_detail['hot_follower_num']=0

            if xnr_user_detail.has_key('trace_follow_tweet_num'):
                pass
            else:
                xnr_user_detail['trace_follow_tweet_num']=0

            xnr_user_detail['total_post_sum']=xnr_user_detail['daily_post_num']+xnr_user_detail['business_post_num']+xnr_user_detail['hot_follower_num']+xnr_user_detail['trace_follow_tweet_num']

    except Exception,e:
       # print 'e1!:',e
    	#xnr_user_detail['user_fansnum']=0
    	xnr_user_detail['daily_post_num']=0
    	xnr_user_detail['business_post_num']=0
    	xnr_user_detail['hot_follower_num']=0
    	xnr_user_detail['total_post_sum']=0
        xnr_user_detail['trace_follow_tweet_num']=0

    #评估信息
    #昨日信息
    yesterday_date=ts2datetime(datetime2ts(date_time)-DAY)
    xnr_assessment_id=xnr_user_no+'_'+yesterday_date
    #print 'xnr_user_detail:::',xnr_user_detail
    if xnr_user_detail['user_fansnum'] == 0:
        count_id=xnr_user_no+'_'+yesterday_date
        try:
            xnr_count_result=es_xnr.get(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=count_id)['_source']
            if xnr_count_result['user_fansnum'] == 0:
                xnr_user_detail['user_fansnum']=xnr_count_result['fans_total_num']
            else:
                xnr_user_detail['user_fansnum']=xnr_count_result['user_fansnum']
        except:
            xnr_user_detail['user_fansnum']=0
    else:
        pass
    try:
        xnr_assess_result=es_xnr.get(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=xnr_assessment_id)['_source']
       # print 'xnr_assessment_id:::',xnr_assessment_id
        xnr_user_detail['influence']=xnr_assess_result['influence']
        xnr_user_detail['penetration']=xnr_assess_result['penetration']
        xnr_user_detail['safe']=xnr_assess_result['safe']
    except:
        xnr_user_detail['influence']= 21.6
        xnr_user_detail['penetration']= 17.9
        xnr_user_detail['safe']=63.1

    xnr_date_info.append(xnr_user_detail)

    return xnr_date_info



def show_condition_history_count(xnr_user_no,start_time,end_time):
    query_body={
    	#'fields':['date_time','user_fansnum','total_post_sum','daily_post_num','hot_follower_num','business_post_num','influence','penetration','safe'],
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term':{'xnr_user_no':xnr_user_no}},
                            {'range':{
                            	'timestamp':{
                            		'gte':start_time,
                            		'lte':end_time
                            	}
                            }}
                        ]
                    }
                }
            }
        },
        'sort':{'timestamp':{'order':'asc'}} ,
        'size':MAX_SEARCH_SIZE
    }
    print 'weibo_xnr_count_info_index_name::',weibo_xnr_count_info_index_name
    print 'weibo_xnr_count_info_index_type', weibo_xnr_count_info_index_type
    print 'query_body', query_body
    try:
        xnr_count_result=es_xnr.search(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,body=query_body)['hits']['hits']
        print "=============================================xnr_count_result--------------------=================-----------"
        print xnr_count_result
        print "=============================================xnr_count_result--------------------=================-----------"
        xnr_date_info=[]
        for item in xnr_count_result:
            if item['_source']['user_fansnum'] == 0:
                item['_source']['user_fansnum']=item['_source']['fans_total_num']
            else:
                pass
            xnr_date_info.append(item['_source'])
    except Exception as e:
        print '---------------=================--------------------es exception'
        print e
        xnr_date_info=[]
    #print 'xnr_date_info::',xnr_date_info
    return xnr_date_info

#历史统计表查询组织
def show_history_count(xnr_user_no,date_range):	
    if S_TYPE == 'test':
        print '======================test'
        test_time_gap=date_range['end_time']-date_range['start_time']
        test_datetime_gap=int(test_time_gap/DAY)
        #print 'test_datetime_gap',test_datetime_gap
        date_range['end_time']=XNR_CENTER_DATE_TIME
        if date_range['type'] == 'today':
            date_range['start_time']=datetime2ts(ts2datetime(date_range['end_time']))
        else:
            date_range['start_time']=datetime2ts(ts2datetime(date_range['end_time']-DAY*test_datetime_gap))
    else:
        pass
    #print 'date_range',date_range

    if date_range['type']=='today':
        print "today==================================="
        start_time=datetime2ts(ts2datetime(date_range['end_time']))
        end_time=date_range['end_time']       #当前时间
        #print 'today_time:',start_time,end_time
        xnr_date_info=show_today_history_count(xnr_user_no,start_time,end_time)
        print "today_history_info==================================="
        print xnr_date_info
        print "today_history_info==================================="

    else:
        print "condition==================================="
        start_time=date_range['start_time']
        end_time=date_range['end_time']
        now_time=int(time.time())
        system_start_time=FLOW_TEXT_START_DATE
        if end_time > now_time:
            end_time=now_time
        if start_time < system_start_time:
            start_time=system_start_time
        print 'condition_time:',start_time,end_time
        xnr_date_info=show_condition_history_count(xnr_user_no,start_time,end_time)
        print "condition_history_count==================================="
        print xnr_date_info
    #xnr_date_info.sorted(key=lambda k:k['date_time'],reverse=True)
    #print 'xnr_date_info',xnr_date_info
    Cumulative_statistics_dict=xnr_cumulative_statistics(xnr_date_info,xnr_user_no)


    return Cumulative_statistics_dict,xnr_date_info

def delete_history_count(task_id):
    try:
        es_xnr.delete(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=task_id)
        result=True
    except:
        result=False
    return result

def create_history_count(task_detail):
    task_id=task_detail['xnr_user_no']+'_'+task_detail['date_time']
    try:
        mark=es_xnr.index(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=task_id,body=task_detail)
    except:
        mark=False
    return mark

#step 4.2: timing task list
###########获取定时发送任务列表##############
def show_timing_tasks(xnr_user_no,start_time,end_time):
    if S_TYPE == 'test':
        test_time_gap=end_time-start_time
        test_datetime_gap=int(test_time_gap/DAY)
        #print 'test_datetime_gap',test_datetime_gap
        end_time=XNR_CENTER_DATE_TIME
        start_time=datetime2ts(ts2datetime(end_time-DAY*test_datetime_gap))
    else:
        pass
    #print start_time,end_time
    #print start_time,end_time
    #获取虚拟人编号
    #user_no_str=xnr_user_no[4:8]
    #print user_no_str
    #user_no=long(user_no_str)
    #print user_no
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term':{'xnr_user_no':xnr_user_no}},
							{'range':{
								'post_time':{
									'gte':start_time,
									'lte':end_time
								}
							}}
						]
					}					
				}
			}

		},
		'size':MAX_VALUE,
		'sort':{'post_time':{'order':'desc'}} 	#按发送时间排序
    }
    results=es_xnr.search(index=weibo_xnr_timing_list_index_name,doc_type=weibo_xnr_timing_list_index_type,body=query_body)['hits']['hits']
    result=[]
    for item in results:
        item['_source']['id']=item['_id']
        result.append(item['_source'])
    return result


###########针对任务进行操作——查看##############
def wxnr_timing_tasks_lookup(task_id):
	result=es_xnr.get(index=weibo_xnr_timing_list_index_name,doc_type=weibo_xnr_timing_list_index_type,id=task_id)['_source']
	return result

###########针对任务进行操作——修改##############
def wxnr_timing_tasks_change(task_id,task_change_info):
	task_source=task_change_info[0]
	operate_type=task_change_info[1]
	create_time=task_change_info[2]
	post_time=int(task_change_info[3])
	text=task_change_info[4]
	remark=task_change_info[5]

	try:
		es_xnr.update(index=weibo_xnr_timing_list_index_name,doc_type=weibo_xnr_timing_list_index_type,id=task_id,\
			body={"doc":{'task_source':task_source,'operate_type':operate_type,'create_time':create_time,\
			'post_time':post_time,'text':text,'remark':remark}})
		result=True
	except:
		result=False
	return result

###########针对任务进行操作——撤销##############
def wxnr_timing_tasks_revoked(task_id):
	task_result=es_xnr.get(index=weibo_xnr_timing_list_index_name,doc_type=weibo_xnr_timing_list_index_type,id=task_id)['_source']
	task_status=task_result['task_status']
	#撤销操作即调整任务状态，将task_status状态设置为-1，只有未发送的任务可以撤销
	
	if task_status == 0:
		task_status = -1
		try:
			es_xnr.update(index=weibo_xnr_timing_list_index_name,doc_type=weibo_xnr_timing_list_index_type,id=task_id,\
				body={"doc":{'task_status':task_status}})
			result=True
		except:
			result=False
	else:
		result=False

	return result

#step 4.3: history information
#step 4.3.1:show history posting
def show_history_posting(require_detail):
    if S_TYPE == 'test':
        date_range_end_ts=XNR_CENTER_DATE_TIME
        test_time_gap=require_detail['end_time']-require_detail['start_time']
        test_datetime_gap=int(test_time_gap/DAY)
        date_range_start_ts=datetime2ts(ts2datetime(date_range_end_ts-DAY*test_datetime_gap))
    else:
        date_range_start_ts=require_detail['start_time']
        date_range_end_ts=require_detail['end_time']
    #print date_range_start_ts,date_range_end_ts


    xnr_user_no=require_detail['xnr_user_no']	
    task_source=require_detail['task_source']
    try:
        es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
        uid=es_result['uid']
    except:
        uid=''


    temp_weibo_xnr_flow_text_listname=get_xnr_flow_text_index_listname(xnr_flow_text_index_name_pre,date_range_start_ts,date_range_end_ts)
    weibo_xnr_flow_text_listname=[]
    for index_name in temp_weibo_xnr_flow_text_listname:
        #print 'index_name:',index_name
        if es_xnr.indices.exists(index=index_name):
            weibo_xnr_flow_text_listname.append(index_name)

        else:
            #print 'not_',index_name
            pass
    #print weibo_xnr_flow_text_listname
    query_body={
		'query':{
			'filtered':{
				'filter':{
					'bool':{
						'must':[
							{'term':{'uid':uid}},
							{'terms':{'task_source':task_source}}
						]
					}					
				}
			}
		},
		'sort':{'timestamp':{'order':'desc'}},
		'size':HOT_WEIBO_NUM
    }

    try:
        #print weibo_xnr_flow_text_listname
        if weibo_xnr_flow_text_listname:
            result=es_xnr.search(index=weibo_xnr_flow_text_listname,doc_type=xnr_flow_text_index_type,body=query_body)['hits']['hits']
            post_result=[]
            for item in result:
                post_result.append(item['_source'])
        else:
            post_result=[]
    except:
        post_result=[]
    return post_result


def new_show_history_posting(require_detail):
    if S_TYPE == 'test':
        date_range_end_ts=XNR_CENTER_DATE_TIME
        test_time_gap=require_detail['end_time']-require_detail['start_time']
        test_datetime_gap=int(test_time_gap/DAY)
        date_range_start_ts=datetime2ts(ts2datetime(date_range_end_ts-DAY*test_datetime_gap))
    else:
        date_range_start_ts=require_detail['start_time']
        date_range_end_ts=require_detail['end_time']
    #print date_range_start_ts,date_range_end_ts


    xnr_user_no=require_detail['xnr_user_no']   
    message_type=require_detail['message_type']
    try:
        es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
        uid=es_result['uid']
    except:
        uid=''


    temp_weibo_xnr_flow_text_listname=get_xnr_flow_text_index_listname(new_xnr_flow_text_index_name_pre,date_range_start_ts,date_range_end_ts)
    weibo_xnr_flow_text_listname=[]
    for index_name in temp_weibo_xnr_flow_text_listname:
        #print 'index_name:',index_name
        if es_xnr.indices.exists(index=index_name):
            weibo_xnr_flow_text_listname.append(index_name)

        else:
            #print 'not_',index_name
            pass
    #print weibo_xnr_flow_text_listname
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term':{'uid':uid}},
                            {'terms':{'message_type':message_type}}
                        ]
                    }                   
                }
            }
        },
        'sort':{'timestamp':{'order':'desc'}},
        'size':HOT_WEIBO_NUM
    }

    try:
        #print weibo_xnr_flow_text_listname
        if weibo_xnr_flow_text_listname:
            result=es_xnr.search(index=weibo_xnr_flow_text_listname,doc_type=new_xnr_flow_text_index_type,body=query_body)['hits']['hits']
            post_result=[]
            for item in result:
                post_result.append(item['_source'])
        else:
            post_result=[]
    except:
        post_result=[]
    return post_result



#step 4.3.2:show at content
def show_at_content(require_detail):
    xnr_user_no=require_detail['xnr_user_no']
    es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    uid=es_result['uid']

	#content_type='weibo'表示@我的微博，='at'表示@我的评论
    content_type=require_detail['content_type']

    if S_TYPE == 'test':
        end_time=XNR_CENTER_DATE_TIME
        test_time_gap=require_detail['end_time']-require_detail['start_time']
        test_datetime_gap=int(test_time_gap/DAY)
        start_time=datetime2ts(ts2datetime(end_time-DAY*test_datetime_gap))
    else:
        start_time=require_detail['start_time']
        end_time=require_detail['end_time']
    #print start_time,end_time
    query_body={
		'query':{
			'filtered':{
				'filter':{
					'bool':{
						'must':[
							{'term':{'root_uid':uid}},
							{'range':{
								'timestamp':{
									'gte':start_time,
									'lte':end_time
								}
							}}
						]
					}
					
				}
			}
		},
		'sort':{'timestamp':{'order':'desc'}},
		'size':MAX_SEARCH_SIZE
    }


    index_name_list=[]
    index_type_list=[]
    #condition_list=[]
    weibo_feedback_retweet_index_name_list = get_xnr_set_index_listname(weibo_feedback_retweet_index_name_pre,start_time,end_time)
    weibo_feedback_at_index_name_list = get_xnr_set_index_listname(weibo_feedback_at_index_name_pre,start_time,end_time)

    for i in xrange(0,len(content_type)):
        if content_type[i]=='weibo':
            index_name_list.append(weibo_feedback_retweet_index_name_list)
            index_type_list.append(weibo_feedback_retweet_index_type)
        elif content_type[i]=='at':
            index_name_list.append(weibo_feedback_at_index_name_list)
            index_type_list.append(weibo_feedback_at_index_type)

    result=[]
    for j in xrange(0,len(index_name_list)):
        try:
            if index_name_list[j]:
                r_result=es_xnr.search(index=index_name_list[j],doc_type=index_type_list[j],body=query_body)['hits']['hits']
                #result=[]
                for item in r_result:
                    result.append(item['_source'])
            else:
                pass
        except:
            result=[]
		#results.append(result)
    #print index_name_list,start_time,end_time,uid
    return result


#step 4.3.3:show comment content
def show_comment_content(require_detail):
    xnr_user_no=require_detail['xnr_user_no']
    comment_type=require_detail['comment_type']
    es_result = es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']

    if S_TYPE == 'test':
        end_time=XNR_CENTER_DATE_TIME
        test_time_gap=require_detail['end_time']-require_detail['start_time']
        test_datetime_gap=int(test_time_gap/DAY)
        start_time=datetime2ts(ts2datetime(end_time-DAY*test_datetime_gap))
    else:
        start_time=require_detail['start_time']
        end_time=require_detail['end_time']

	#start_time=require_detail['start_time']
	#end_time=require_detail['end_time']

    query_body={
		'query':{
			'filtered':{
				'filter':{
					'bool':{
						'must':[
							{'term':{'root_uid':uid}},
							{'terms':{'comment_type':comment_type}},
							{'range':{
								'timestamp':{
									'gte':start_time,
									'lte':end_time
								}
							}}
						]
					}
				}
			}
		},
		'sort':{'timestamp':{'order':'desc'}},
		'size':MAX_SEARCH_SIZE
    }

    weibo_feedback_comment_index_name_list = get_xnr_set_index_listname(weibo_feedback_comment_index_name_pre,start_time,end_time)

    try:
        results=[]
        if weibo_feedback_comment_index_name_list:
            result=es_xnr.search(index=weibo_feedback_comment_index_name_list,doc_type=weibo_feedback_comment_index_type,body=query_body)['hits']['hits']
            for item in result:
                results.append(item['_source'])
        else:
            pass
    except:
        results=[]
    return results



#step 4.3.4:show like content
def show_like_content(require_detail):
    xnr_user_no=require_detail['xnr_user_no']
    es_result = es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    uid = es_result['uid']
    like_type=require_detail['like_type']

    #start_time=require_detail['start_time']
    #end_time=require_detail['end_time']
    if S_TYPE == 'test':
        end_time=XNR_CENTER_DATE_TIME
        test_time_gap=require_detail['end_time']-require_detail['start_time']
        test_datetime_gap=int(test_time_gap/DAY)
        start_time=datetime2ts(ts2datetime(end_time-DAY*test_datetime_gap))
    else:
        start_time=require_detail['start_time']
        end_time=require_detail['end_time']

    results=[]
    for i in xrange(0,len(like_type)):
        receive_temp_result=[]
        send_temp_result=[]
        if like_type[i] == 'receive':
            receive_temp_result=lookup_receive_like(uid,start_time,end_time)
            results.extend(receive_temp_result)
        elif like_type[i] == 'send':
            send_temp_result=lookup_send_like(uid,start_time,end_time)
            results.extend(send_temp_result)
        #results.extend(temp_result)
    return results

def lookup_receive_like(uid,start_time,end_time):
    query_body={
        'query':{
            'filtered':{
                'filter':{
                	'bool':{
                		'must':[
                			{'term':{'root_uid':uid}},
                			{'range':{
								'timestamp':{
									'gte':start_time,
									'lte':end_time
								}
							}}
                		]
                	}
                }
            }
        },
        'sort':{'timestamp':{'order':'desc'}},
        'size':MAX_SEARCH_SIZE
    }
    weibo_feedback_like_index_name_list = get_xnr_set_index_listname(weibo_feedback_like_index_name_pre,start_time,end_time)
    try:
        results=[]
        if weibo_feedback_like_index_name_list:
            result=es_xnr.search(index=weibo_feedback_like_index_name_list,doc_type=weibo_feedback_like_index_type,body=query_body)['hits']['hits']
            for item in result:
                results.append(item['_source'])
        else:
            pass
    except:
        results=[]
    return results

def lookup_send_like(uid,start_time,end_time):
    query_body={
        'query':{
            'filtered':{
                'filter':{
                	'bool':{
                		'must':[
                			{'term':{'uid':uid}},
                			{'range':{
								'timestamp':{
									'gte':start_time,
									'lte':end_time
								}
							}}
                		]
                	}
                }
            }
        },
        'sort':{'timestamp':{'order':'desc'}},
        'size':MAX_SEARCH_SIZE
    }
    try:
        result=es_xnr.search(index=weibo_xnr_save_like_index_name,doc_type=weibo_xnr_save_like_index_type,body=query_body)['hits']['hits']
        results=[]
        for item in result:
            results.append(item['_source'])
    except:
        results=[]
    return results

###########################################################################
#	step 4.3 & 4.4 & 4.5：微博相关操作，调用公共函数                      #
# (转发，评论，点赞，收藏，查看对话，回复，取消关注，直接关注，查看详情)  #  
###########################################################################

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
    #print 'xnr_user_no:',xnr_user_no
    xnr_es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    account_name=xnr_es_result['weibo_mail_account']
    password=xnr_es_result['password']
    root_uid=xnr_es_result['uid']

    
    xnr_result=es_xnr.get(index=weibo_xnr_fans_followers_index_name,doc_type=weibo_xnr_fans_followers_index_type,id=xnr_user_no)['_source']
    if xnr_result.get('followers_list',''):
        followers_list=xnr_result['followers_list']
    else:
        followers_list=[]

    if xnr_result.get('fans_list',''):
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

#收藏
#——暂无公共函数调用

#查看对话
####root_mid之间的数据关系可能存在问题
def show_comment_dialog(mid):
    query_body={
		'query':{
			'filtered':{
				'filter':{
					'bool':{
						'must':[
							{'term':{'root_mid':mid}}
						]
					}
				}
			}
		},
		'sort':{'timestamp':{'order':'desc'}},
		'size':MAX_SEARCH_SIZE
	}
    weibo_feedback_comment_index_name_list = get_xnr_set_index_listname(weibo_feedback_comment_index_name_pre,start_time,end_time)
    try:
        if weibo_feedback_comment_index_name_list:
            results=[]
            es_result=es_xnr.search(index=weibo_feedback_comment_index_name_list,doc_type=weibo_feedback_comment_index_type,body=query_body)['hits']['hits']
            for item in es_result:
                results.append(item['_source'])
        else:
            pass
    except:
        results=[]
	return results



#回复
#——回复即调用评论函数

#取消关注
def cancel_follow_user(task_detail):
    xnr_user_no=task_detail['xnr_user_no']
    xnr_es_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    account_name=xnr_es_result['weibo_mail_account']
    password=xnr_es_result['password']

    follower_uid=task_detail['uid']

    #调用取消关注函数
    
    mark=unfollow_tweet_func(xnr_user_no,account_name,password,follower_uid)
    #修改关注列表
    #if mark:
    #    save_mark=delete_xnr_followers(xnr_user_no,follower_uid)
    #else:
    #    save_mark=False
    return mark

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

#查看详情
def lookup_detail_weibouser(uid):
	result=es_user_profile.get(index=profile_index_name,doc_type=profile_index_type,id=uid)['_source']
	return result

#step 4.4: list of concerns

'''
def wxnr_list_concerns(user_id,order_type):
    try:
        result=es_xnr.get(index=weibo_xnr_fans_followers_index_name,doc_type=weibo_xnr_fans_followers_index_type,id=user_id)
        followers_list=result['_source']['followers_list']
    except:
        followers_list=[]

    user_result=[]
    if followers_list:
        followers_result=es_user_profile.mget(index=profile_index_name,doc_type=profile_index_type,body={'ids':followers_list})['docs']
        
        for item in followers_result:
            user_dict=dict()
            uid=item['_id']
            user_dict['uid']=item['_id']
            #计算影响力
            user_dict['influence']=count_weibouser_influence(uid)
            #敏感度查询,话题领域
            try:
                temp_user_result=es_user_profile.get(index=portrait_index_name,doc_type=portrait_index_type,id=uid)['_source']
                user_dict['sensitive']=temp_user_result['sensitive']
                user_dict['topic_string']=temp_user_result['topic_string']
            except:
                user_dict['sensitive']=0
                user_dict['topic_string']=''

            if item['found']:
                user_dict['photo_url']=item['_source']['photo_url']            
                user_dict['nick_name']=item['_source']['nick_name']
                user_dict['sex']=item['_source']['sex']
                user_dict['user_birth']=item['_source']['user_birth']
                user_dict['create_at']=item['_source']['create_at']
                user_dict['user_location']=item['_source']['user_location']
            else:
                user_dict['photo_url']=''            
                user_dict['nick_name']=''
                user_dict['sex']=''
                user_dict['user_birth']=''
                user_dict['create_at']=''
                user_dict['user_location']=''
            user_result.append(user_dict)
    else:
        user_result=[]

    #对结果按要求排序
    user_result.sort(key=lambda k:(k.get(order_type,0)),reverse=True)
    return user_result
'''

def lookup_xnr_fans_followers(user_id,lookup_type):
    try:
        xnr_result=es_xnr.get(index=weibo_xnr_fans_followers_index_name,doc_type=weibo_xnr_fans_followers_index_type,id=user_id)['_source']
        lookup_list=xnr_result[lookup_type]
    except:
        lookup_list=[]
    return lookup_list

#交集判断
def set_intersection(str_A,list_B):
    list_A=[]
    list_A.append(str_A)
    set_A = set(list_A)
    set_B = set(list_B)
    result = set_A & set_B
    number = len(result)
    return number

def wxnr_list_concerns(user_id,order_type):
    # 新方法 @hanmc 2019-1-16 19:05:28
    results = []
    query_body = {
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term': {'xnr_no': user_id}},
                            {'term': {'pingtaiguanzhu': 1}}
                        ]
                    }
                }
            }
        },
        'size': MAX_VALUE,
        'sort': {order_type: {"order": "desc"}},
    }
    search_results = es_xnr.search(index=weibo_xnr_relations_index_name, doc_type=weibo_xnr_relations_index_type, body=query_body)['hits']['hits']

    for data in search_results:
        data = data['_source']
        r = {
            'uid': data['uid'],
            #'nick_name': data['nickname'],
            'nick_name': data.get('nickname', ''),
            'topic_string': data.get('topic_string', ''),
            'sensitive': data.get('sensitive', 0),
            'influence': data.get('influence', 0),
            'follow_source': '',
            'sex': data.get('sex', ''),
            'photo_url': data.get('photo_url', ''),
        }
        results.append(r)
    return results


"""
    # 旧方法，弃用
    print 'start!!',int(time.time())
    try:
        xnr_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=user_id)['_source']
        xnr_uid=xnr_result['uid']
    except:
        xnr_uid=''
    print 'followers!!',int(time.time())
    lookup_type='followers_list'
    followers_list=lookup_xnr_fans_followers(user_id,lookup_type)


    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                       'must':{'term':{'root_uid':xnr_uid}}
                    }
                }
            }
        },
        'size':MAX_VALUE
    }
    xnr_followers_result=[]
    #print 'compute!!!',int(time.time())
    if xnr_uid:
        #print 'search!!!',int(time.time())
        followers_result=es_xnr.search(index=weibo_feedback_follow_index_name,doc_type=weibo_feedback_follow_index_type,body=query_body)['hits']['hits']
        #print 'for!!!',int(time.time())
        for item in followers_result:
            user_dict=dict()
            follower_uid=item['_source']['uid']
            set_mark =  set_intersection(follower_uid,followers_list)
            #if follower_uid in followers_list:
            if set_mark > 0:
                user_dict['uid']=follower_uid
                #计算影响力
                #print 'influence!!!!',int(time.time())
                user_dict['influence']=0
                # user_dict['influence']=count_weibouser_influence(follower_uid)
                #敏感度查询,话题领域
                #print 'sensitive!!!',int(time.time())
                # try:
                #     temp_user_result=es_user_portrait.get(index=portrait_index_name,doc_type=portrait_index_type,id=follower_uid)['_source']
                #     user_dict['sensitive']=temp_user_result['sensitive']
                #     user_dict['topic_string']=temp_user_result['topic_string']
                # except:
                user_dict['sensitive']=0
                user_dict['topic_string']=''
                #print user_dict['sensitive']
                #print 'sensitive!!!_final!!!',int(time.time())
                user_dict['photo_url']=item['_source']['photo_url']            
                user_dict['nick_name']=item['_source']['nick_name']
                user_dict['sex']=item['_source']['sex']
                #user_dict['user_birth']=item['_source']['user_birth']
                #user_dict['create_at']=item['_source']['create_at']
                user_dict['follow_source']=item['_source']['follow_source']  #微博推荐
                #user_dict['user_location']=item['_source']['user_location']
                xnr_followers_result.append(user_dict)
            else:
                pass
    else:
    	xnr_followers_result=[]
    #print 'final!!!',int(time.time())
    #对结果按要求排序
    xnr_followers_result.sort(key=lambda k:(k.get(order_type,0)),reverse=True)
    return xnr_followers_result
"""




#计算影响力
def count_weibouser_influence(uid):
    now_time=int(time.time())
    date_time=ts2datetimestr(now_time-DAY)
    index_name=weibo_bci_index_name_pre+date_time
    
    query_body={
        'query':{
            'match_all':{}
        },
        'size':1,
        'sort':{'user_index':{'order':'desc'}}
    }
    try:
        max_result=es_user_profile.search(index=index_name,doc_type=weibo_bci_index_type,body=query_body)['hits']['hits']
        for item in max_result:
           max_user_index=item['_source']['user_index']

        user_result=es_user_profile.get(index=index_name,doc_type=weibo_bci_index_type,id=uid)['_source']
        user_index=user_result['user_index']
        infulence_value=user_index/max_user_index*100
    except:
        infulence_value=0
    return infulence_value


#step 4.5: list of fans  
def wxnr_list_fans(user_id,order_type):
    # 新方法 @hanmc 2019-1-17 12:21:44
    results = []
    query_body = {
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term': {'xnr_no': user_id}},
                            {'term': {'pingtaifensi': 1}}
                        ]
                    }
                }
            }
        },
        'size': MAX_VALUE,
        'sort': {order_type: {"order": "desc"}},
    }
    search_results = es_xnr.search(index=weibo_xnr_relations_index_name, doc_type=weibo_xnr_relations_index_type, body=query_body)['hits']['hits']

    for data in search_results:
        data = data['_source']
        r = {
            'uid': data.get('uid', ''),
            'nick_name': data.get('nickname', ''),
            'user_location': data.get('geo', ''),
            'topic_string': data.get('topic_string', ''),
            'sensitive': data.get('sensitive', 0),
            'influence': data.get('influence', 0),
            'fans_source': '',
            'sex': data.get('sex', ''),
            'photo_url': data.get('photo_url', ''),
        }
        results.append(r)
    return results


"""
        # 旧方法，弃用
        try:
            xnr_result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=user_id)['_source']
            xnr_uid=xnr_result['uid']
            #print '=======================================xnr_uid'
            #print xnr_uid
        except:
            #print '=======================================not find anything about xnr_uid and some error occur'
            xnr_uid=''
        
        lookup_type='fans_list'
        fans_list=lookup_xnr_fans_followers(user_id,lookup_type)
    
        query_body={
            'query':{
                'filtered':{
                    'filter':{
                        'bool':{
                           'must':{'term':{'root_uid':xnr_uid}}
                        }
                    }
                }
            },
            'size':MAX_VALUE
        }
        xnr_fans_result=[]
        if xnr_uid:
            fans_result=es_xnr.search(index=weibo_feedback_fans_index_name,doc_type=weibo_feedback_fans_index_type,body=query_body)['hits']['hits']
            #print '===========================================,fans_result'
            #print fans_result
            for item in fans_result:
                user_dict=dict()
                fans_uid=item['_source']['uid']
                set_mark =  set_intersection(fans_uid,fans_list)
                #print '===========================================,set_mark'
                #print set_mark 
                #if fans_uid in fans_list:
                if set_mark > 0:
                    user_dict['uid']=fans_uid
                    #计算影响力
                    user_dict['influence']=0
                   # user_dict['influence']=count_weibouser_influence(fans_uid)
                    #敏感度查询,话题领域
                    #try:
                    #    temp_user_result=es_user_profile.get(index=portrait_index_name,doc_type=portrait_index_type,id=fans_uid)['_source']
                    #    user_dict['sensitive']=temp_user_result['sensitive']
                    #    user_dict['topic_string']=temp_user_result['topic_string']
                    #except:
                    user_dict['sensitive']=0
                    user_dict['topic_string']=''
    
                    user_dict['photo_url']=item['_source']['photo_url']            
                    user_dict['nick_name']=item['_source']['nick_name']
                    user_dict['sex']=item['_source']['sex']
                    #user_dict['user_birth']=item['_source']['user_birth']
                    #user_dict['create_at']=item['_source']['create_at']
                    user_dict['fan_source']=item['_source']['fan_source']  #微博推荐
                    user_dict['user_location']=item['_source']['geo']
                    xnr_fans_result.append(user_dict)
                else:
                    pass
                    # add xuanhui kn
                    #user_dict['uid']=fans_uid
                    #user_dict['influence']=0
                    #user_dict['sensitive']=0
                    #user_dict['topic_string']=''
                    #user_dict['photo_url']=item['_source']['photo_url']            
                    #user_dict['nick_name']=item['_source']['nick_name']
                    #user_dict['sex']=item['_source']['sex']
                    #user_dict['fan_source']=item['_source']['fan_source']  #微博推荐
                    #user_dict['user_location']=item['_source']['geo']
                    #xnr_fans_result.append(user_dict)
        else:
            xnr_fans_result=[]
    
        #对结果按要求排序
        xnr_fans_result.sort(key=lambda k:(k.get(order_type,0)),reverse=True)
        print "================================================xnr_fans_result"
        print xnr_fans_result
        return xnr_fans_result
"""

#########################################################
#	step 5：change    and   continue                    #
#########################################################
def change_continue_xnrinfo(xnr_user_no):
    result=es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    return result


###############################
#	step 6：delete_weibo_xnr  #
###############################
def delete_weibo_xnr(xnr_user_no):
	try:
		es_xnr.delete(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)
		result=True
	except:
		result=False
	return result


###############################
#   step 7：虚拟人评估信息  #
###############################
def lookup_xnr_assess_info(xnr_user_no,start_time,end_time,assess_type):
    query_body={
        'fields':['date_time',assess_type],
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':[
                            {'term':{'xnr_user_no':xnr_user_no}},
                            {'range':{
                                'timestamp':{
                                    'gte':start_time,
                                    'lte':end_time
                                }
                            }}
                        ]
                    }
                }
            }
        },
        'sort':{'timestamp':{'order':'asc'}},
        'size':MAX_SEARCH_SIZE
    }
    try:
        xnr_assess_result=es_xnr.search(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,body=query_body)['hits']['hits']
        assess_result=[]
        for item in xnr_assess_result:
           # print 'item::',item
            assess_result.append(item['fields'])
    except:
        assess_result=[]
    return assess_result


#create xnr_flow_text example
def create_xnr_flow_text(task_detail,task_id):
	result=es_xnr.index(index="xnr_flow_text_2017-10-14",doc_type=xnr_flow_text_index_type,id=task_id,body=task_detail)
	return result

def delete_xnr_flow_text(task_id):
	result=es_xnr.delete(index="xnr_flow_text_2017-10-11",doc_type=xnr_flow_text_index_type,id=task_id)
	return result	


def update_weibo_count(task_detail,task_id):
    #result=es_xnr.index(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=task_id,body=task_detail)
    result=es_xnr.update(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=task_id,body={"doc":{'user_fansnum':task_detail['user_fansnum']}})
    return result

def delete_weibo_count(task_id):
    result=es_xnr.delete(index=weibo_xnr_count_info_index_name,doc_type=weibo_xnr_count_info_index_type,id=task_id)
    return result


def create_send_like(task_detail,task_id):
    result=es_xnr.index(index=weibo_xnr_save_like_index_name,doc_type=weibo_xnr_save_like_index_type,id=task_id,body=task_detail)
    return result


def delete_receive_like():
    query_body={
        'query':{
            'filtered':{
                'filter':{
                    'bool':{
                        'must':{'range':{'timestamp':{'gte':0,'lte':1506787140}}}
                    }
                }
            }
        }    
    }
    id_result=es_xnr.search(index=weibo_feedback_like_index_name,doc_type=weibo_feedback_like_index_type,body=query_body)['hits']['hits']
    result_list=[]
    for item in id_result:
        t_id=item['_id']
        result=es_xnr.delete(index=weibo_feedback_like_index_name,doc_type=weibo_feedback_like_index_type,id=t_id)
        result_list.append(result)

    return result_list

# kn 获取用户账户密码是否错误
def get_account_info(xnr_user_no):
    account = {}
    result_info = es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
    print result_info  
    try:
        print result_info['verify_password']
        account_info = result_info['verify_password']
        if account_info:
            account["account_info"] = account_info
        else:
            account["account_info"] = 0
    except Exception,e:
        account["account_info"] = 0
        pass
    return account

# 修改用户账户和密码
def update_account_info(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    weibo_phone_account = task_detail['weibo_phone_account']
    weibo_mail_account = task_detail['weibo_mail_account']
    account_password = task_detail['password']
    print account_password
    try:
        item_exist = es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
        item_exist['weibo_phone_account'] = weibo_phone_account
        item_exist['weibo_mail_account'] = weibo_mail_account
        item_exist['password'] = account_password
        item_exist['verify_password'] = ''

        print es_xnr.update(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no,body={'doc':item_exist})
        return {"status":'ok'}
    except Exception,e:
        return {"status":'fail'}
        print e


# by kn xuan 查看当前xnr的监测关键词
def get_xnr_monitor_words(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    try:
        item_exist = es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
        keywords_result = item_exist['monitor_keywords']
    except Exception as e:
        return ''
    return keywords_result


def modify_xnr_monitor_words(task_detail):
    xnr_user_no = task_detail['xnr_user_no']
    try:
        item_exist = es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
        item_exist['monitor_keywords'] = ','.join(task_detail['new_monitor_keywords'].encode('utf-8').split('，'))
        print es_xnr.update(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no,body={'doc':item_exist})
        
        return {"status":"ok"}

    except Exception as e:
        print e
        return {"status":"fail"}

    '''
    try:
        item_exist = es_xnr.get(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no)['_source']
        old_keyword = task_detail['old_monitor_keywords']
        new_keyword = task_detail['new_monitor_keywords']
        old_monitor_keywords = (item_exist['monitor_keywords'].split(','))
        print item_exist['monitor_keywords'] 
        print old_monitor_keywords
        new_str_list = list()
        new_str = str()
        for old in old_monitor_keywords:
            if old == old_keyword:
                new_str_list.append(new_keyword)
                #new_str = new_str + new_keyword + ','
            else:
                new_str_list.append(old_keyword)
                #new_str = new_str + old + ','
        ['你好','我好','他好']
        print new_str_list
        for new in new_str_list:
            new_str = new_str + new + ','
        #new_str= '你好'
        new_str = new_str[:-1]
        end_str = ','.join(new_str.encode('utf-8').split('，'))
        item_exist['monitor_keywords'] = new_str.encode('utf-8')
        print es_xnr.update(index=weibo_xnr_index_name,doc_type=weibo_xnr_index_type,id=xnr_user_no,body={'doc':item_exist})
        print new_str[:-1]
        return {"status":"ok"}
    except Exception as e:
        print e
        return {"status":"fail"}

    print 'util-=-=-=-+_+_+_+_+__++_+++++++++++++++++++++++++++++++________________________________--'
    '''


