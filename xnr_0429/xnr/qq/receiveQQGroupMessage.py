# -*- coding: utf-8 -*-

# 如果不希望加载本插件，可以在配置文件中的 plugins 选项中删除 qqbot_test.plugins.grouplog
import os
import datetime
import hashlib
import json
import time
import types

from qqbot import _bot as bot
from qqbot.utf8logger import INFO

from elasticsearch import Elasticsearch
from sensitive_compute import sensitive_check
import sys, getopt

reload(sys)
sys.path.append('../')
sys.path.append('/home/xnr1/xnr_0429/xnr/')
#sys.path.append('../cron/qq_group_message/')

# es = Elasticsearch("http://219.224.134.213:9205/")
from global_utils import es_xnr as es,r,r_qq_group_set_pre
import sys, getopt
from global_utils import group_message_index_name_pre, \
        group_message_index_type, qq_document_task_name, QRCODE_PATH

from qq_xnr_groupmessage_mappings import group_message_mappings


def onQQMessage(bot, contact, member, content):
    # 当收到 QQ 消息时被调用
    # bot     : QQBot 对象，提供 List/SendTo/GroupXXX/Stop/Restart 等接口，详见文档第五节
    # contact : QContact 对象，消息的发送者
    # member  : QContact 对象，仅当本消息为 群或讨论组 消息时有效，代表实际发消息的成员
    # content : str 对象，消息内容
    INFO('test groups %s', bot.List('group'))
    INFO('bot.conf %s', bot.conf)
    print '========================================================================recive qq message start'
    print 'contact.============.',contact
    print contact.qq, contact.nick
    print '-----------------------------------------------------------------------------'

    if contact.ctype == 'group':
        INFO('群的 QQ.. %s', contact.qq)  # #NULL
        INFO('群的昵称.. %s', contact.nick) # 嘿哼哈
        INFO('成员的 QQ.. %s', member.qq)   # #NULL
        INFO('成员的昵称.. %s', member.nick) # /石沫沫
        INFO('最后发言时间.. %s', member.last_speak_time) # -1
        INFO('消息.. %s', content) # test内容

        last_speak_time = int(time.time())
        print 'last_speak_time..',last_speak_time
        if content == '':
            INFO('您发了一张图片或假消息... %s', content)
        else:
            sen_value,sen_words = sensitive_check(content)      # sen_words包含sensitive_words_string：北京&达赖和sensitive_words_dict
            if sen_value !=0:
                sen_flag = 1    #该条信息是敏感信息
            else:
                sen_flag = 0
            # qq_item = {
            #     'xnr_qq_number': bot.session.qq,
            #     'xnr_nickname': bot.session.nick,
            #     'timestamp': member.last_speak_time,
            #     'speaker_qq_number': member.qq,
            #     'text': content,
            #     'sensitive_flag':sen_flag,
            #     'sensitive_value': sen_value,
            #     'sensitive_words_string': sen_words['sensitive_words_string'],
            #     'speaker_nickname': member.nick,
            #     'qq_group_number': contact.qq,
            #     'qq_group_nickname': contact.nick
            # }
            qq_item = {
                'xnr_qq_number': bot.session.qq,
                'xnr_nickname': bot.session.nick,
                'timestamp': last_speak_time,
                'speaker_qq_number': '',
                'text': content,
                'sensitive_flag':sen_flag,
                'sensitive_value': sen_value,
                'sensitive_words_string': sen_words['sensitive_words_string'],
                'speaker_nickname': member.nick,
                'qq_group_number': '',
                'qq_group_nickname': contact.nick
            }
            qq_json = json.dumps(qq_item)
            print 'qq_json=====:',qq_json
            # 判断该qq群是否在redis的群set中
            #qq_number  = qq_item['xnr_qq_number']
            #qq_group_number = qq_item['qq_group_number']

            # r_qq_group_set = r_qq_group_set_pre + qq_number
            # qq_group_set = r.smembers(r_qq_group_set)
            #test
            #qq_group_set = set(['531811289'])
           
            #if qq_group_number in qq_group_set:
            
            conMD5 = string_md5(content)
            
            nowDate = datetime.datetime.now().strftime('%Y-%m-%d')
            index_name = group_message_index_name_pre+ str(nowDate)
            print 'INDEX NAME-=-------------=-=-'
            print index_name
            #index_id = bot.conf.qq + '_' + contact.qq + '_' + str(member.last_speak_time) + '_' + conMD5
            # 让系统随机分配 _id
            if not es.indices.exists(index=index_name):
                print 'get mapping'
                print group_message_mappings(bot.session.qq,nowDate)
            print 'qq_item.....',qq_item
            print es.index(index=index_name, doc_type=group_message_index_type,body=qq_item)
                

def string_md5(str):
    md5 = ''
    if type(str) is types.StringType:
        _md5 = hashlib.md5()
        _md5.update(str)
        md5 = _md5.hexdigest()
    return md5


def execute():
    bot.Login()
    bot.Plug('receiveQQGroupMessage')
    bot.Run()


def execute_v2(qqbot_port, qqbot_num, qqbot_mailauth):
    if not os.path.exists(QRCODE_PATH+qqbot_port):
        os.system('mkdir ' +  QRCODE_PATH+qqbot_port)
    bot.Login(['-p', qqbot_port, '-b', QRCODE_PATH+qqbot_port, \
            '-r', '-q', qqbot_num, \
            '-m', qqbot_num+'@qq.com', '-mc', qqbot_mailauth, \
            '-dm'])
    bot.Plug('receiveQQGroupMessage')
    bot.Run()

if __name__ == '__main__':
    #execute()
    opts, args = getopt.getopt(sys.argv[1:], 'hi:o:m:')
    print "opts,args,opts,args,opts,args,opts,args,opts,args,opts,args"
    print opts, args 
    for op, value in opts:
        if op == '-i':
            qqbot_port = value
        elif op == '-o':
            qqbot_num = value
        elif op == '-m':
            qqbot_mailauth = value
    #print 'qqbot_port, qqbot_num. qqbot_mailauth:', qqbot_port
    #print 'qqbot_mailauth:', qqbot_mailauth
   # print 'qqbot_num:', qqbot_num
    # 2018.8.20 yuanlai
    execute_v2(qqbot_port, qqbot_num, qqbot_mailauth)
    #mailauthcode:sirtgdmgwiivbegf
