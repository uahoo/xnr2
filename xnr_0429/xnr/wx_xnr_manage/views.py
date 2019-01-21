#-*- coding: utf-8 -*-
import os
import time
import json
from flask import Blueprint, url_for, render_template, request,\
                  abort, flash, session, redirect
from utils import utils_create_xnr, utils_load_all_groups, utils_set_groups, utils_check_status, utils_logout, \
                  utils_login, utils_show_wxxnr, utils_delete, utils_show_wx_xnr_listening_groups
from xnr.global_utils import r_wx as r

mod = Blueprint('wx_xnr_manage', __name__, url_prefix='/wx_xnr_manage')

@mod.route('/create/')
def create_xnr():
    wx_id = request.args.get('wx_id', '')
    submitter = request.args.get('submitter', '')
    mail = request.args.get('mail', '')
    access_id = request.args.get('access_id', '')
    remark = request.args.get('remark', '')
    if wx_id and submitter and access_id:
        res = utils_create_xnr({'wx_id':wx_id, 'submitter':submitter, 'mail':mail, 'access_id':access_id, 'remark':remark})
        if res:
            return json.dumps(res)
    return json.dumps({}) 

@mod.route('/login/')
def login():
    wxbot_id = request.args.get('wxbot_id', '')
    if wxbot_id:
        res = utils_login(wxbot_id)
        if res:
            return json.dumps(res)
    return json.dumps({}) 

@mod.route('/logout/')
def logout():
    wxbot_id = request.args.get('wxbot_id', '')
    if wxbot_id:
        res = utils_logout(wxbot_id)
        if res:
            return json.dumps(res)
    return json.dumps({}) 

@mod.route('/checkstatus/')
def check_status():
    wxbot_id = request.args.get('wxbot_id', '')
    if wxbot_id:
        res = utils_check_status(wxbot_id)
        if res:
            return json.dumps(res)
    return json.dumps({}) 

@mod.route('/loadallgroups/')
def load_all_groups():
    #加载指定虚拟人的所有群组信息
    wxbot_id = request.args.get('wxbot_id', '')
    if wxbot_id:
        res = utils_load_all_groups(wxbot_id)
        if res:
            return json.dumps(res)
    return json.dumps({}) 

@mod.route('/setgroups/')
def set_groups():
    wxbot_id = request.args.get('wxbot_id', '')
    group_list_string = request.args.get('group_list', '')
    group_list = group_list_string.split(',')
    if wxbot_id:
        res = utils_set_groups(wxbot_id, group_list)
        if res:
            return json.dumps(res)
    return json.dumps({}) 

@mod.route('/show/')
def show_wxxnr():
    submitter = request.args.get('submitter', '')
    res = utils_show_wxxnr(submitter)
    if res:
        return json.dumps(res)
    return json.dumps({}) 

@mod.route('/show_listening_groups/')
def show_wxxnr_listening_groups():
    wxbot_id = request.args.get('wxbot_id', '')
    if wxbot_id:
        res = utils_show_wx_xnr_listening_groups(wxbot_id)
        if res:
            return json.dumps(res)
    return json.dumps({}) 

@mod.route('/delete/')
def delete():
    wxbot_id = request.args.get('wxbot_id', '')
    if wxbot_id:
        res = utils_delete(wxbot_id)
        if res:
            return json.dumps(res)
    return json.dumps({}) 
