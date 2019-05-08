# -*- coding: utf-8 -*-
'''
use to save function---about deal database
'''
import time
import sys
import json
import subprocess
from xnr.global_utils import es_xnr,qq_xnr_index_name,\
        qq_xnr_index_type, ABS_LOGIN_PATH,QRCODE_PATH,r_qq_group_set_pre,r, qq_xnr_max_no, r_qq_receive_message
from xnr.global_utils import qq_xnr_history_count_index_name_pre,qq_xnr_history_count_index_type,\
                        group_message_index_name_pre,group_message_index_type
from xnr.global_config import port_range
from xnr.parameter import MAX_VALUE,LOCALHOST_IP
from xnr.utils import user_no2qq_id
from xnr.time_utils import ts2datetime,datetime2ts
import socket
from xnr.qq.getgroup import getgroup,getgroup_v2,getgroup_v3
from xnr.qq.receiveQQGroupMessage import execute_v2


def IsOpen(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        result = s.connect_ex((ip,int(port)))
        
        if result:              #端口可用
            return True
        else:
            return False
    except:
        
        return False



def get_all_ports():

    query_body = {
        "query":{
            "match_all": {}
        },
        "size": MAX_VALUE
    }
    try:
        result = es_xnr.search(index=qq_xnr_index_name, doc_type=qq_xnr_index_type,body=query_body)['hits']['hits']
    except:
        return []
    results = []
    if result != []:
        for item in result:
            if item['_source']['qqbot_port'] not in results:
                results.append(int(item['_source']['qqbot_port']))
    return results


'''
def find_port(exist_port_list):
    if exist_port_list != []:
        port = max(exist_port_list)
        port += 1
    else:
        port = 1025
    while port<=65535:
        if IsOpen(LOCALHOST_IP,port):
            break
        port +=1
    return port
'''

def find_port(exist_port_list):
    min_port = port_range[0]
    max_port = port_range[1]
    for port in range(min_port, max_port+1):
        if not port in exist_port_list:
            if IsOpen(LOCALHOST_IP,port):   #端口可用
                return port
    return False

def get_qq_xnr_no():
    
    if not r.exists(qq_xnr_max_no): #如果当前redis没有记录，则去es数据库查找补上
        user_no_max = 1
        r.set(qq_xnr_max_no,user_no_max)
    else:   #如果当前redis有记录，则取用
        user_no_max = r.incr(qq_xnr_max_no)

    return user_no_max

def get_login_name(xnr_user_no):

    try:
        print 'execut get_login_name function--------------------------------------------------------------------------------'
        get_results = es_xnr.get(index=qq_xnr_index_name,doc_type=qq_xnr_index_type,id=xnr_user_no)['_source']
        print get_results, 'es results-=-=-=-=-=-==-=-=-=========================-----------------------------------------------' 
        qq_number = get_results['qq_number']
        qqbot_port = get_results['qqbot_port']
        access_id = get_results['access_id']
        print "qq_number, qqbot_port, access_id, _+_+_+_+_+_+_+_+_+_"
        print qq_number, qqbot_port, access_id
        #qqbot_port = '8199'
        # ABS_LOGIN_PATH = /home/xnr1/xnr_0429/xnr/qq/reciveQQGroupMesaage.py
        p_str1 = 'python '+ ABS_LOGIN_PATH + ' -i '+str(qqbot_port) + ' >> login'+str(qqbot_port)+'.txt'
        #qqbot_port = '8190'
        qqbot_num = qq_number
        qqbot_port = str(qqbot_port)
        qqbot_mc = access_id #'sirtgdmgwiivbegf'
        #qqbot_mc = 'worunhzbzyipdagc'
        # yuanlai >>>>>>>>>>>>8.20
        p_str1 = 'python '+ ABS_LOGIN_PATH + ' -i '+qqbot_port + ' -o ' + qqbot_num + ' -m ' + qqbot_mc + ' >> login'+qqbot_port+'.txt'
        # xuanhui 8.20 把邮件发送到80217252
        #p_str1 = 'python '+ ABS_LOGIN_PATH + ' -i '+qqbot_port + ' -o ' + '80617252' + ' -m ' + qqbot_mc + ' >> login'+qqbot_port+'.txt'
        #p_str1 = 'python '+ ABS_LOGIN_PATH + ' -i '+qqbot_port + ' -o ' + qqbot_num + ' -m ' + qqbot_mc
        command_str = 'python '+ ABS_LOGIN_PATH + ' -i '+qqbot_port + ' -o ' + qqbot_num + ' -m ' + qqbot_mc
        #print 'p_str1:', p_str1
        #print '========================================================================='
        p_str2 = 'pgrep -f ' + '"' + command_str + '"'
        #print 'p_str2::',p_str2
        process_ids = subprocess.Popen(p_str2, \
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print '========================================================================='
        print process_ids
        process_id_list = process_ids.stdout.readlines()
        print process_id_list
        print '========================================================================='
        for process_id in process_id_list:
            process_id = process_id.strip()
            kill_str = 'kill -9 ' + process_id
            print 'kill_str::',kill_str
            p2 = subprocess.Popen(kill_str, \
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        print p_str1
        p2 = subprocess.Popen(p_str1, \
                shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # # 存储qq端口、授权码等消息,用于后台主进程调用
        qq_info = dict()
        qq_info['qq_num'] = qqbot_num
        qq_info['qq_port'] = qqbot_port
        qq_info['access_id'] = qqbot_mc
        r.lpush(r_qq_receive_message,json.dumps(qq_info))
	    
        return True

    except:
        return False


def create_qq_xnr(xnr_info):
# xnr_info = [qq_number,qq_groups,nickname,active_time,create_time]
    print '============1'
    qq_group_exist_list = ''#[]
    qq_group_new_list = []
    qq_number = xnr_info['qq_number']
    #qq_groups = xnr_info['qq_groups'].encode('utf-8').split('，')
    group_names = xnr_info['group_names'].encode('utf-8').split('，')
    mark_names = xnr_info['mark_names'].encode('utf-8').split('，')
    group_numbers = xnr_info['group_numbers'].encode('utf-8').split('，')
    print 'group_numbers...',group_numbers
    if not len(group_names)==len(mark_names)==len(group_numbers):
        #return [False,'群名称数量和群号码数量不一致']
        return [False,'群名称数量、群备注数量和群号码数量不一致']

    if len(group_numbers) == 0:
        return [False, '输入不能为空']

    # redis 群名
    r_qq_group_set = r_qq_group_set_pre + qq_number

    mark_name_exist_list = []
    
    nickname = xnr_info['nickname']
    access_id = xnr_info['access_id']
    remark = xnr_info['remark']
    submitter = xnr_info['submitter']

    
    #r_qq_group_mark_set = r_qq_group_mark_set_pre + qq_number

    query_body_qq_exist = {
        'query':{
            'term':{'qq_number':qq_number}
        }
    }

    search_result = es_xnr.search(index=qq_xnr_index_name,doc_type=qq_xnr_index_type,\
        body=query_body_qq_exist)['hits']['hits']
    print '456'
    if search_result:
        #return ['当前qq已经被添加！',qq_group_exist_list]
        group_info = json.loads(search_result[0]['_source']['group_info'])
        group_info_keys = group_info.keys() # 群号

        for i in range(len(group_numbers)):

            group_qq_number = group_numbers[i]
            group_qq_name = group_names[i]
            group_qq_mark = mark_names[i]

            if group_qq_number in group_info_keys:   # 若群号已添加，则可修改群名
                #qq_group_exist_list.append(group_qq_number)
                #mark_name_list = group_info[group_qq_number]['mark_name']
                group_name_list = group_info[group_qq_number]['group_name']
                r.sadd(r_qq_group_set,group_qq_mark)

                if not group_qq_name in group_name_list:
                    group_info[group_qq_number]['group_name'].append(group_qq_name)

            else:  # 若群号未添加，首先检查备注名是否重复，若重复，则返回，否则，正常流程。
                if not r.sadd(r_qq_group_set,group_qq_mark):  # 群号唯一 改为 备注唯一
                    mark_name_exist_list.append(group_qq_mark)
                else:
                    group_info[group_qq_number] = {'mark_name':group_qq_mark,'group_name':[group_qq_name]}

        if mark_name_exist_list:
            return [False,'失败！以下备注名重复：' + ','.join(mark_name_exist_list)]

        qqbot_port = search_result[0]['_source']['qqbot_port']
        
        # 把不在的群添加进去           
        qq_exist_result = search_result[0]['_source']
        xnr_user_no = qq_exist_result['xnr_user_no']
        qq_exist_result['group_info'] = json.dumps(group_info)

        qq_exist_result['qq_group_num'] = len(group_info)

        es_xnr.update(index=qq_xnr_index_name,doc_type=qq_xnr_index_type,id=xnr_user_no,\
            body={'doc':qq_exist_result})

        result = True

    else:

        # active_time = xnr_info[3]
        create_ts = xnr_info['create_ts']
        exist_port_list = get_all_ports()           #返回list形式int型端口号
        qqbot_port = find_port(exist_port_list)
        #qq_groups_num = len(qq_groups)
        # qq_groups = getgroup_v2(qq_number)
        user_no_current = get_qq_xnr_no()
        xnr_user_no = user_no2qq_id(user_no_current)  #五位数 QXNR0001
        
        # 群信息
        group_info = {}
        
        for i in range(len(group_numbers)):
            group_qq_number = group_numbers[i]
            group_qq_name = group_names[i]
            group_qq_mark = mark_names[i]

            if not r.sadd(r_qq_group_set,group_qq_mark):  # 群号唯一 改为 备注唯一. 存入redis,后面接收群消息时，用于过滤消息。
                mark_name_exist_list.append(group_qq_mark)
            else:
                group_info[group_qq_number] = {'mark_name':group_qq_mark,'group_name':[group_qq_name]}


        if mark_name_exist_list:
            return [False,'失败！以下备注名重复：' + ','.join(mark_name_exist_list)]

        qq_group_num = len(group_info)
        group_info = json.dumps(group_info)

        #try:        
            ## 存入es
        print es_xnr.index(index=qq_xnr_index_name, doc_type=qq_xnr_index_type, id=xnr_user_no, \
        body={'qq_number':qq_number,'nickname':nickname,'group_info':group_info,'qq_group_num':qq_group_num,'create_ts':create_ts,\
                'qqbot_port':qqbot_port,'user_no':user_no_current,'xnr_user_no':xnr_user_no,\
                'access_id':access_id,'remark':remark,'submitter':submitter})
        

        result = True
        # except:
        #     result = False

    print 'before python recieveQQGroupMessage:', result


        

        #print 'output:', p2.stdout.readlines()
        
    return [result,qq_group_exist_list]

def login_status(xnr_user_no):
	
	group_dict = getgroup_v2(xnr_user_no)
	print 'group_dict======',group_dict
	if group_dict:
		login_status = 'True'
	else:
		login_status = 'False'
	return login_status

def show_qq_xnr_index(MAX_VALUE,submitter):
    query_body = {
        'query':{
            'term':{'submitter':submitter}
        },
        'size':MAX_VALUE
    }
    results = []
    result = es_xnr.search(index=qq_xnr_index_name, doc_type=qq_xnr_index_type, body=query_body)['hits']['hits']
    qq_xnr_list = []
    for item in result:
        item_dict = dict()
        #temp = item['_source'].copy()
        #item_dict = dict(item_dict, **temp)
        #step1: identify login status
        #port = item['_source']['qqbot_port']
        try:
            qqnum = item['_source']['qq_number']
            xnr_user_no = item['_source']['xnr_user_no']
            nickname = item['_source']['nickname']
            item_dict['qq_number'] = qqnum
            item_dict['xnr_user_no'] = xnr_user_no
            item_dict['nickname'] = nickname
            results.append(item_dict)
        except:
            continue
    return results


def show_qq_xnr(MAX_VALUE,submitter):
    query_body = {
        'query':{
            'term':{'submitter':submitter}
        },
        'size':MAX_VALUE
    }
    results = []
    result = es_xnr.search(index=qq_xnr_index_name, doc_type=qq_xnr_index_type, body=query_body)['hits']['hits']
    qq_xnr_list = []
    for item in result:
        item_dict = dict()
        temp = item['_source'].copy()
        item_dict = dict(item_dict, **temp)
        #step1: identify login status
        port = item['_source']['qqbot_port']
        qqnum = item['_source']['qq_number']
        xnr_user_no = item['_source']['xnr_user_no']
        #group_dict = getgroup_v2(xnr_user_no)
        #print 'group_dict:::',group_dict
        # if group_dict:
            # login_status = True
        # else:
            # login_status = False
        item_dict['login_status'] = 'unknown' #'unknown' #login_status
        now_date = ts2datetime(time.time() - 24*3600)
        #histroy_id = item['_source']['xnr_user_no'] + '_' + now_date
        qq_xnr_history_count_index_name = qq_xnr_history_count_index_name_pre + now_date
        try:
            history_result = es_xnr.get(index=qq_xnr_history_count_index_name,\
                doc_type=qq_xnr_history_count_index_type, id=xnr_user_no)['_source']
            total_post_num = history_result['total_post_num']
            daily_post_num = history_result['daily_post_num']
        except:
            total_post_num = 0
            daily_post_num = 0
        
        group_message_index_name = group_message_index_name_pre + ts2datetime(time.time())

        query_body = {
            'query':{
                'bool':{
                    'must':[
                        {'term':{'speaker_qq_number':qqnum}},
                        {'term':{'xnr_qq_number':qqnum}}
                    ]
                }
            }
        }
        try:
            count_result = es_xnr.count(index=group_message_index_name,doc_type=group_message_index_type,body=query_body)

            if count_result['_shards']['successful'] != 0:
                today_count = count_result['count']
            else:
                print 'es index rank error'
                today_count = 0
        except:
            today_count = 0

        item_dict['daily_post_num'] = today_count
        item_dict['total_post_num'] = total_post_num + today_count
        results.append(item_dict)

    return results

def delete_qq_xnr(qq_number):

    get_result = es_xnr.get(index=qq_xnr_index_name,doc_type=qq_xnr_index_type,id=qq_number)['_source']
    qq = get_result['qq_number']
    r_qq_group_set = r_qq_group_set_pre + qq

    while True:
        a = r.spop(r_qq_group_set)
        if a:
            continue
        else:
            break

    try:
        es_xnr.delete(index=qq_xnr_index_name, doc_type=qq_xnr_index_type, id=qq_number)
        result = 1
    except:
        result = 0
    return result


def delete_qq_group(xnr_user_no,group_numbers_string):

    group_numbers = group_numbers_string.encode('utf-8').split('，')

    if not group_numbers:

        return [False,'请先选择要删除的群']


    query_body_qq_exist = {
        'query':{
            'term':{'xnr_user_no':xnr_user_no}
        }
    }

    search_result = es_xnr.search(index=qq_xnr_index_name,doc_type=qq_xnr_index_type,\
        body=query_body_qq_exist)['hits']['hits']

    if search_result:
        group_info = json.loads(search_result[0]['_source']['group_info'])
        qq_number = search_result[0]['_source']['qq_number']
        r_qq_group_set = r_qq_group_set_pre + qq_number

        for item in group_numbers:
            try:
                group_qq_mark = group_info[item]['mark_name']
                print 'group_qq_mark...',group_qq_mark
                r.srem(r_qq_group_set,group_qq_mark)

                group_info.pop(item)

            except:
                pass

        qq_group_num = len(group_info)
        group_info = json.dumps(group_info)

        es_xnr.update(index=qq_xnr_index_name, doc_type=qq_xnr_index_type, id=xnr_user_no,  \
            body={"doc":{'group_info':group_info,'qq_group_num':qq_group_num}})

        return [True,'']
    else:
        return [False,'当前qq尚未添加到系统']


def change_qq_xnr(xnr_user_no,group_names_string,mark_names_string,group_numbers_string):

    get_result = es_xnr.get(index=qq_xnr_index_name,doc_type=qq_xnr_index_type,id=xnr_user_no)['_source']

    group_info = json.loads(get_result['group_info'])

    group_names = group_names_string.encode('utf-8').split('，')
    mark_names = mark_names_string.encode('utf-8').split('，')
    group_numbers = group_numbers_string.encode('utf-8').split('，')

    if len(group_numbers) != len(group_names) and len(group_numbers) != 0:
        return 'not_equal'

    group_numbers_origin = group_info.keys()

    delete_list = list(set(group_numbers_origin).difference(set(group_numbers)))
    #add_list = list(set(group_numbers).difference(set(group_numbers_origin)))

    if delete_list:
        for item in delete_list:
            group_info.pop(item)

    for i in range(len(group_numbers)):
        group_qq_number = group_numbers[i]
        group_qq_name = group_names[i]

        if group_qq_number not in group_numbers_origin:  # 新添加的
            group_info[group_qq_number] = [group_qq_name,'']
            r.sadd(r_qq_group_set,group_qq_number)  ## 存入redis,后面接收群消息时，用于过滤消息。

    qq_group_num = len(group_info)
    group_info = json.dumps(group_info)

    try:
        es_xnr.update(index=qq_xnr_index_name, doc_type=qq_xnr_index_type, id=xnr_user_no,  \
            body={"doc":{'group_info':group_info,'qq_group_num':qq_group_num}})
        result = True #'Successfully changed'
    except:
        result = False #'Changing Failed'

    return result

def search_qq_xnr(qq_number):
    query_body = {
    "query": {
        "filtered":{
            "filter":{
                "term":{"qq_number": qq_number}
            }
        }
    },
    'size':MAX_VALUE
}

    result = es_xnr.search(index=qq_xnr_index_name, doc_type=qq_xnr_index_type, body=query_body)
    
    return result



