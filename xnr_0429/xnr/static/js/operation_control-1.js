//检验密码是否正确
/*var check_password_url='/weibo_xnr_manage/verify_xnr_account/?xnr_user_no='+ID_Num;
public_ajax.call_request('get',check_password_url,checkPassword);
function checkPassword(data){
	if(data['account_info']==0){
		$('.infoError').html('<span style="color:#03a9f4;">账户正常运行中。</span>');
	}else {
		$('.infoError').html('<span style="color:red;">账户异常，为保证虚拟人正常工作，请检查您的账户和密码是否正确，并及时更改。</span>');
	}
}
*/
var end_time=Date.parse(new Date())/1000;
//=====历史统计====定时任务列表====历史消息===时间段选择===
$('.choosetime .demo-label input').on('click',function () {
    var _val=$(this).val();
    var sh=$(this).attr('shhi');
    var mid=$(this).parents('.choosetime').attr('midurl');
    var task=$(this).parents('.choosetime').attr('task');
    if (_val=='mize'&&sh!=0){
        $(this).parents('.choosetime').find('#start_'+sh).show();
        $(this).parents('.choosetime').find('#end_'+sh).show();
        $(this).parents('.choosetime').find('#sure-'+sh).css({display:'inline-block'});
    }else {
        $(this).parents('.choosetime').find('#start_'+sh).hide();
        $(this).parents('.choosetime').find('#end_'+sh).hide();
        $(this).parents('.choosetime').find('#sure-'+sh).hide();
        var his_timing_task_url;
        if (mid=='show_history_count'){
            if (_val==0){
                his_timing_task_url='/weibo_xnr_manage/show_history_count/?xnr_user_no='+ID_Num+'&type=today&start_time=0&end_time='+end_time;
            }else {
                _start=getDaysBefore(_val);
                his_timing_task_url='/weibo_xnr_manage/show_history_count/?xnr_user_no='+ID_Num+'&type=&start_time='+_start+'&end_time='+end_time;
            }
        }else if (mid=='new_show_history_posting'){
            var conTP=[];
            $(".li-3 .news #content .tab-pane.active input:checkbox:checked").each(function (index,item) {
                conTP.push($(this).val());
            });
            var mid_2=$(".li-3 .news li.active").attr('midurl').split('&');
            if (_val==0){
                his_timing_task_url='/weibo_xnr_manage/'+mid_2[0]+'/?xnr_user_no='+ID_Num+'&'+mid_2[2]+'='+conTP.join(',')+
                    '&start_time='+todayTimetamp()+'&end_time='+end_time;
            }else {
                _start=getDaysBefore(_val);
                his_timing_task_url='/weibo_xnr_manage/'+mid_2[0]+'/?xnr_user_no='+ID_Num+'&'+mid_2[2]+'='+conTP.join(',')+
                    '&start_time='+_start+'&end_time='+end_time;
            }
        }else {
            var startTime='';
            if (_val==0){
                startTime=todayTimetamp();
            }else {
                startTime=getDaysBefore(_val);
            }
            his_timing_task_url='/weibo_xnr_manage/'+mid+'/?xnr_user_no='+ID_Num+'&start_time='+startTime+'&end_time='+end_time;
        }
        public_ajax.call_request('get',his_timing_task_url, window[task]);
    }
});
$('.sureTime').on('click',function () {
    var t=$(this).attr('shhi');
    var s=$(this).parents('.choosetime').find('#start_'+t).val();
    var d=$(this).parents('.choosetime').find('#end_'+t).val();
    if (s==''||d==''){
        $('#successfail p').text('时间不能为空。');
        $('#successfail').modal('show');
    }else {
        var mid=$(this).parents('.choosetime').attr('midurl');
        var task=$(this).parents('.choosetime').attr('task');
        var his_timing_task_url='/weibo_xnr_manage/'+mid+'/?xnr_user_no='+ID_Num+'&start_time='+(Date.parse(new Date(s))/1000)+
            '&end_time='+(Date.parse(new Date(d))/1000);
        if (mid=='show_history_count'){his_timing_task_url+='&type='};
        if (mid=='new_show_history_posting'){
            var conTP=[];
            $(".li-3 .news #content .tab-pane.active input:checkbox:checked").each(function (index,item) {
                conTP.push($(this).val());
            });
            var mid_2=$(".li-3 .news li.active").attr('midurl').split('&');
            his_timing_task_url='/weibo_xnr_manage/'+mid_2[0]+'/?xnr_user_no='+ID_Num+'&'+mid_2[2]+'='+conTP.join(',')+
                '&start_time='+(Date.parse(new Date(s))/1000)+'&end_time='+(Date.parse(new Date(d))/1000);
        }
        public_ajax.call_request('get',his_timing_task_url,window[task]);
    }
});
$(".customizeTime").keydown(function(e) {
    if (e.keyCode == 13) {
        var _val=$(this).val();
        var reg = new RegExp("^[0-9]*$");
        if (reg.test(_val)){

        }else {
            $('#successfail p').text('只能输入数字。');
            $('#successfail').modal('show');
        }
    }
});
//历史统计
var historyTotal_url='/weibo_xnr_manage/show_history_count/?xnr_user_no='+ID_Num+'&type=today&start_time=0&end_time='+end_time;
public_ajax.call_request('get',historyTotal_url,historyTotal);
function historyTotal(data) {
    historyTotalTable(data[0]);
    historyTotalLine(data[1]);
}
function historyTotalLine(data) {
    var time=[],fansDate=[],totalPostData=[],dailyPost=[],
        hotData=[],businessData=[],traceData=[],influeData=[],pentData=[],safeData=[];
    $.each(data,function (index,item) {
        time.push(item.date_time);
        fansDate.push(item.user_fansnum)
        totalPostData.push(item.total_post_sum)
        dailyPost.push(item.daily_post_num)
        hotData.push(item.hot_follower_num)
        businessData.push(item.business_post_num)
        traceData.push(item.trace_follow_tweet_num)
        influeData.push(item.influence)
        pentData.push(item.penetration)
        safeData.push(item.safe)
    });
    var myChart = echarts.init(document.getElementById('history-1'),'dark');
    var option = {
        backgroundColor:'transparent',
        title: {
            text: '',
        },
        tooltip: {
            trigger: 'axis'
        },
        legend: {
            data:['总粉丝数','总微博数','日常发帖','热点跟随','业务发帖','跟踪转发','影响力','渗透力','安全性'],
            width:'400',
            left:'center'
        },
        toolbox: {
            show: true,
            feature: {
                dataZoom: {
                    yAxisIndex: 'none'
                },
                magicType: {type: ['line', 'bar']},
                restore: {},
                saveAsImage: {
                    backgroundColor: 'rgba(8,23,44,0.8)',
                }
            }
        },
        xAxis:  {
            name:'时间',
            type: 'category',
            boundaryGap: false,
            data: time
        },
        yAxis: {
            name:'数量',
            type: 'value',
            axisLabel: {
                formatter: '{value} '
            }
        },
        series: [
            {
                name:'总粉丝数',
                type:'line',
                data:fansDate,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'总微博数',
                type:'line',
                data:totalPostData,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'日常发帖',
                type:'line',
                data:dailyPost,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'热点跟随',
                type:'line',
                data:hotData,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'业务发帖',
                type:'line',
                data:businessData,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'跟踪转发',
                type:'line',
                data:traceData,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'影响力',
                type:'line',
                data:influeData,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'渗透力',
                type:'line',
                data:pentData,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            },
            {
                name:'安全性',
                type:'line',
                data:safeData,
                markPoint: {
                    data: [
                        {type: 'max', name: '最大值'},
                        {type: 'min', name: '最小值'}
                    ]
                },
                markLine: {
                    data: [
                        {type: 'average', name: '平均值'}
                    ]
                }
            }
        ]
    };
    myChart.setOption(option);
}
function historyTotalTable(dataTable) {
    var data=[dataTable];
    $('#history-2 p').show();
    $('#history-2').bootstrapTable('load', data);
    $('#history-2').bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 2,//单页记录数
        pageList:[2,5,10,20],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "名称",//标题
                field: "date_time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.date_time==''||row.date_time=='null'||row.date_time=='unknown'||!row.date_time){
                        return '未知';
                    }else {
                        return row.date_time;
                    };
                }
            },
            {
                title: "总粉丝数",//标题
                field: "user_fansnum",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "总微博数",//标题
                field: "total_post_sum",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "日常发帖",//标题
                field: "daily_post_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "热点跟随",//标题
                field: "hot_follower_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "业务发帖",//标题
                field: "business_post_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "跟踪转发",//标题
                field: "trace_follow_tweet_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "影响力",//标题
                field: "influence",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "渗透力",//标题
                field: "penetration",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "安全性",//标题
                field: "safe",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
        ],
    });
    $('#history-2 p').slideUp(700);
};
//定时发送任务列表
var timingTask_url='/weibo_xnr_manage/show_timing_tasks/?xnr_user_no='+ID_Num+'&start_time='+todayTimetamp()+'&end_time='+end_time;
public_ajax.call_request('get',timingTask_url,timingTask);
var TYPE={
    'origin':'原创','retweet':'转发','comment':'评论'
}
function timingTask(data) {
    $('#time p').show();
    $('#time').bootstrapTable('load', data);
    $('#time').bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 2,//单页记录数
        pageList:[2,5,10,20],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "编号",//标题
                field: "xnr_user_no",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "任务来源",//标题
                field: "task_source",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.task_source==''||row.task_source=='null'||row.task_source=='unknown'||!row.task_source){
                        return '未知';
                    }else {
                        return row.task_source;
                    };
                }
            },
            {
                title: "提交时间",//标题
                field: "create_time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.create_time==''||row.create_time=='null'||row.create_time=='unknown'){
                        return '未知';
                    }else {
                        return getLocalTime(row.create_time);
                    };
                }
            },
            {
                title: "预计发送时间",//标题
                field: "post_time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.post_time==''||row.post_time=='null'||row.post_time=='unknown'||!row.post_time){
                        return '未知';
                    }else {
                        return getLocalTime(row.post_time);
                    };
                }
            },
            {
                title: "发送状态",//标题
                field: "task_status",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.task_status==''||row.task_status=='null'||row.task_status=='unknown'||!row.task_status){
                        return '未知';
                    }else {
                        if (row.task_status==0){
                            return '未发送';
                        }else if (row.task_status==1){
                            return '已发送';
                        }else {return '未知';}
                    };
                }
            },
            {
                title: "备注",//标题
                field: "remark",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.remark==''||row.remark=='null'||row.remark=='unknown'){
                        return '无备注';
                    }else {
                        return row.remark;
                    };
                }
            },
            {
                title: "操作",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    var ID=row.id;
                    return '<span style="cursor: pointer;" onclick="lookRevise(\''+ID+'\',\''+row.task_status+'\')" title="查看详情"><i class="icon icon-link"></i></span>&nbsp;&nbsp;'+
                    //'<span style="cursor: pointer;" onclick="lookRevise(\''+ID+'\')" title="修改"><i class="icon icon-edit"></i></span>&nbsp;&nbsp;'+
                    '<span style="cursor: pointer;" onclick="revoked(\''+ID+'\')" title="撤销"><i class="icon icon-reply"></i></span>';
                }
            },
        ],
    });
    $('#time p').hide(700);
}

//操作
//=====查看====
var __ST;
function lookRevise(_id,ST) {
    __ST=ST;
    var saw_url='/weibo_xnr_manage/wxnr_timing_tasks_lookup/?task_id='+_id;
    public_ajax.call_request('get',saw_url,saw);
}
function saw(data) {
    var t1='无内容',t2='无备注',m='未知';
    if (data.post_time!=''||data.post_time!='null'||data.post_time!='unknown'||!data.post_time){
        m = getLocalTime(data.post_time);
    }
    if (data.text!=''||data.text!='null'||data.text!='unknown'||!data.text){
        t1= data.text;
    }
    if (data.remark!=''||data.remark!='null'||data.remark!='unknown'||!data.remark){
        t2= data.remark;
    }
    $("#details .taskid").text(data.id);
    $("#details .create_time").text(data.create_time);
    $("#details .details-1 input[type='radio'][value='"+data.task_source+"']").attr("checked",true);
    $("#details .details-2 input[type='radio'][value='"+data.operate_type+"']").attr("checked",true);
    $("#details .details-3 #_timing").attr("placeholder",m);
    $("#details .details-4 #words").val(t1);
    $("#details .details-5 #remarks").val(t2);
    if (__ST==1){
        $('#details .__modify').css({display:'none'});
    }
    $('#details').modal('show');
}
//修改内容参数
function sureModify() {
    var id=$("#details .taskid").text();
    var creat_time=$("#details .create_time").text();
    var task_source=$('#details .details-1 input:radio[name="dett"]:checked').val();
    var operate_type=$('#details .details-2 input:radio[name="opert"]:checked').val();
    var post_time=$("#details .details-3 #_timing").val(),mi='';
    var text=$("#details .details-4 #words").val();
    var remark=$("#details .details-5 #remarks").val();
    if (post_time){
        mi=Date.parse(new Date(post_time))/1000;
    }else {
        post_time=$("#details .details-3 #_timing").attr('placeholder');
        mi=Date.parse(new Date(post_time))/1000;
    }
    var againSave_url='/weibo_xnr_manage/wxnr_timing_tasks_change/?task_id='+id+'&task_source='+task_source+
        '&operate_type='+operate_type+'&create_time='+creat_time+'&post_time='+mi+'&text='+text+'&remark='+remark;
    public_ajax.call_request('get',againSave_url,successfail);
}
//撤销
var escTxt=0;
function revoked(_id) {
    escTxt=1;
    var delTask_url='/weibo_xnr_manage/wxnr_timing_tasks_revoked/?task_id='+_id;
    public_ajax.call_request('get',delTask_url,successfail);
}
//=========
function successfail(data) {
    var t ='操作成功';
    if (!data){
        t='操作失败';
        if(escTxt==1){t='消息已发送，无法撤回。';escTxt=0;}
    }else {
        setTimeout(function () {
            public_ajax.call_request('get',timingTask_url,timingTask);
        },700);
    };

    $('#successfail p').text(t);
    $('#successfail').modal('show');
}
//------历史消息type分页-------
var typeDown='new_show_history_posting',boxShoes='historyCenter',MID='message_type';
$('#container .rightWindow .news #myTabs li').on('click',function () {
    boxShoes=$(this).attr('box');
    htp=[];
    var middle=$(this).attr('midurl').split('&'),liNews_url='';
    var tm=$('input:radio[name="time3"]:checked').val();
    typeDown=middle[0];
    MID=middle[2];
    var $params=[];
    var paramsParent=$(this).find('a').attr('href');
    $(paramsParent+" .aa input:checkbox:checked").each(function (index,item) {
        $params.push($(this).val());
    });
    if ($params.length==0){$params.push(middle[1])}
    if (tm){
        if (tm!='mize'){
            liNews_url='/weibo_xnr_manage/'+middle[0]+'/?xnr_user_no='+ID_Num+'&'+middle[2]+'='+$params.join(',')+
                '&start_time='+getDaysBefore(tm)+'&end_time='+end_time;
        }else {
            var s=$(this).parents('.news').prev().find('#start_3').val();
            var d=$(this).parents('.news').prev().find('#end_3').val();
            if (s==''||d==''){
                $('#successfail p').text('时间不能为空。');
                $('#successfail').modal('show');
                return false;
            }else {
                liNews_url='/weibo_xnr_manage/'+middle[0]+'/?xnr_user_no='+ID_Num+'&'+middle[2]+'='+$params.join(',')+
                    '&start_time='+(Date.parse(new Date(s))/1000)+ '&end_time='+(Date.parse(new Date(d))/1000);
            }
        }
    }else {
        liNews_url='/weibo_xnr_manage/'+middle[0]+'/?xnr_user_no='+ID_Num+'&'+middle[2]+'='+$params.join(',')+
            '&start_time='+todayTimetamp()+'&end_time='+end_time;
    }
    public_ajax.call_request('get',liNews_url,historyNews);
})

//------历史消息type分页下的按钮选择-----
var htp=[];
$('#container .rightWindow .oli .news #content input').on('click',function () {
    var flag=$(this).parents('.tab-pane').attr('id');
    htp=[];
    $("#"+flag+" input:checkbox:checked").each(function (index,item) {
        htp.push($(this).val());
    });
    var content_type=htp.join(','),againHistoryNews_url='';
    var tm=$('input:radio[name="time3"]:checked').val();
    if (tm){
        if (tm!='mize'){
            againHistoryNews_url='/weibo_xnr_manage/'+typeDown+'/?xnr_user_no='+ID_Num+'&'+MID+'='+content_type+
                '&start_time='+getDaysBefore(tm)+'&end_time='+end_time;
        }else {
            var s=$(this).parents('.news').prev().find('#start_3').val();
            var d=$(this).parents('.news').prev().find('#end_3').val();
            if (s==''||d==''){
                $('#successfail p').text('时间不能为空。');
                $('#successfail').modal('show');
                return false;
            }else {
                againHistoryNews_url='/weibo_xnr_manage/'+typeDown+'/?xnr_user_no='+ID_Num+'&'+MID+'='+content_type+
                    '&start_time='+(Date.parse(new Date(s))/1000)+ '&end_time='+(Date.parse(new Date(d))/1000);
            }
        }
    }else {
        againHistoryNews_url='/weibo_xnr_manage/'+typeDown+'/?xnr_user_no='+ID_Num+'&'+MID+'='+content_type+
            '&start_time='+todayTimetamp()+'&end_time='+end_time;
    }
    public_ajax.call_request('get',againHistoryNews_url,historyNews);
})
var historyNews_url='/weibo_xnr_manage/new_show_history_posting/?xnr_user_no='+ID_Num+'&message_type=1'+
    '&start_time='+todayTimetamp()+'&end_time='+end_time;
// var historyNews_url='/weibo_xnr_manage/show_history_posting/?xnr_user_no='+ID_Num+'&task_source=daily_post'+
//     '&start_time='+todayTimetamp()+'&end_time='+end_time;
public_ajax.call_request('get',historyNews_url,historyNews);
function historyNews(data) {
    var showHide1='none',showHide2='inline-block',showHide3='none',showHide4='none',C3='';
    // border_1='border-left:1px solid slategrey;border-right:1px solid slategrey;';
    // border_2='border-left:1px solid slategrey;';
    if (boxShoes=='historyCenter'){showHide1='inline-block'};
    if (boxShoes=='myweibo'){showHide3='inline-block';C3='display:none';};
    if (boxShoes=='commentCOT'){showHide2='none';showHide4='inline-block';};
    if (boxShoes=='likes'){C3='display:none';};
    $('#'+boxShoes+' p').show();
    $('#'+boxShoes).bootstrapTable('load', data);
    $('#'+boxShoes).bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
        pageList:[2,5,10,20],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    var name,txt,img,time;
                    if (row.xnr_user_no==''||row.xnr_user_no=='null'||row.xnr_user_no=='unknown'||
                        row.nick_name==''||row.nick_name=='null'||row.nick_name=='unknown'){
                        name=row.uid;
                    }else {
                        name=row.xnr_user_no||row.nick_name;
                    };
                    if (row.timestamp==''||row.timestamp=='null'||row.timestamp=='unknown'||!row.timestamp){
                        time='未知';
                    }else {
                        time=getLocalTime(row.timestamp);
                    };
                    if (row.photo_url==''||row.photo_url=='null'||row.photo_url=='unknown'||!row.photo_url||!row.picture_url||
                        row.picture_url==''||row.picture_url=='null'||row.picture_url=='unknown'){
                        img='/static/images/unknown.png';
                    }else {
                        img=row.photo_url||row.picture_url;
                    };
                    var all='';
                    if (row.text==''||row.text=='null'||row.text=='unknown'){
                        txt='暂无内容';
                    }else {
                        if (row.text.length>=170){
                            txt=row.text.substring(0,170)+'...';
                            all='inline-block';
                        }else {
                            txt=row.text;
                            all='none';
                        }
                    };
                    var a=Number(row.retweeted).toString();
                    var b=Number(row.retweet).toString();
                    var retNum=(a||b);
                    var str=
                        '<div class="post_perfect">'+
                        '   <div class="post_center-hot">'+
                        '       <img src="'+img+'" class="center_icon">'+
                        '       <div class="center_rel" style="text-align: left;">'+
                        '           <a class="center_1" href="https://weibo.com/u/'+row.uid+'" style="color: #f98077;">'+name+'</a>&nbsp;&nbsp;'+
                        '           <span class="time" style="font-weight: 900;color:blanchedalmond;"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>&nbsp;&nbsp;'+
                        '           <button data-all="0" style="display: '+all+'" type="button" class="btn btn-primary btn-xs allWord" onclick="allWord(this)">查看全文</button>'+
                        '           <p class="allall" style="display: none;">'+row.text+'</p>'+
                        '           <i class="mid" style="display: none;">'+row.mid+'</i>'+
                        '           <i class="uid" style="display: none;">'+row.uid+'</i>'+
                        '           <i class="timestamp" style="display: none;">'+row.timestamp+'</i>'+
                        '           <span class="center_2">'+txt+
                        '           </span>'+
                        '           <div class="center_3">'+
                        '               <span class="cen3-1" onclick="retweet(this,\'日常发帖\')" style="display: '+showHide2+';"><i class="icon icon-share"></i>&nbsp;&nbsp;转发 <b style="'+C3+'">（'+retNum+'）</b></span>'+
                        '               <span class="cen3-2" onclick="showInput(this)" style="display:'+showHide2+';"><i class="icon icon-comments-alt"></i>&nbsp;&nbsp;评论<b style="'+C3+'">（'+row.comment+'）</b></span>'+
                        '               <span class="cen3-3" onclick="thumbs(this)" style="display:'+showHide2+';"><i class="icon icon-thumbs-up"></i>&nbsp;&nbsp;赞</span>'+
                        '               <span class="cen3-9" onclick="robot(this)" style="display:'+showHide2+';"><i class="icon icon-github-alt"></i>&nbsp;&nbsp;机器人回复</span>'+
                        '               <span class="cen3-4" onclick="joinlab(this)" style="display:'+showHide1+'"><i class="icon icon-upload-alt"></i>&nbsp;&nbsp;加入语料库</span>'+
                        // '               <span class="cen3-3" onclick="collect(this)" style="display:'+showHide3+';"><i class="icon icon-legal"></i>&nbsp;&nbsp;收藏</span>'+
                        '               <span class="cen3-5" onclick="dialogue(this)" style="display:'+showHide4+';"><i class="icon icon-book"></i>&nbsp;&nbsp;查看对话</span>'+
                        '               <span class="cen3-6" onclick="showInput(this)" style="display:'+showHide4+';"><i class="icon icon-comments-alt"></i>&nbsp;&nbsp;回复</span>'+
                        '           </div>'+
                        '           <div class="forwardingDown" style="width: 100%;display: none;">'+
                        '               <input type="text" class="forwardingIput" placeholder="转发内容"/>'+
                        '               <span class="sureFor" onclick="forwardingBtn()">转发</span>'+
                        '           </div>'+
                        '           <div class="commentDown" style="width: 100%;display: none;">'+
                        '               <input type="text" class="comtnt" placeholder="评论内容"/>'+
                        '               <span class="sureCom" onclick="comMent(this,\'日常发帖\')">评论</span>'+
                        '           </div>'+
                        '       </div>'+
                        '   </div>'+
                        '</div>';
                    return str;
                }
            },
        ],
    });
    $('#'+boxShoes+' p').slideUp(700);
}
//查看全文
// function allWord(_this) {
//     var a=$(_this).attr('data-all');
//     if (a==0){
//         $(_this).text('收起');
//         $(_this).parents('.center_rel').find('.center_2').html($(_this).next().text());
//         $(_this).attr('data-all','1');
//     }else {
//         $(_this).text('查看全文');
//         $(_this).parents('.center_rel').find('.center_2').text($(_this).next().text().substring(0,160)+'...');
//         $(_this).attr('data-all','0');
//     }
// }
//=====评论======
//查看对话
function dialogue(_this) {
    var mid = $(_this).parents('.center_rel').find('.mid').text(),start,end;
    var timeCH=$('input:radio[name="time3"]:checked').val();
    if (timeCH!='mize'){
        start=getDaysBefore(timeCH);end=end_time;
    }else {
        var s=$('.choosetime-3 #start_3').val();
        var d=$('.choosetime-3 #end_3').val();
        if (s==''||d==''){
            $('#successfail p').text('时间不能为空。');
            $('#successfail').modal('show');
            return false;
        }else {
            start=(Date.parse(new Date(s))/1000);end=(Date.parse(new Date(d))/1000);
        }
    }
    var dialogue_url='/weibo_xnr_manage/show_comment_dialog/?mid='+mid+
        '&start_time='+start+'&end_time='+end;
    // var dialogue_url='/weibo_xnr_manage/show_comment_dialog/?mid=4201556885068742&start_time=1517155200&end_time=1517298000'
    public_ajax.call_request('get',dialogue_url,dialogue_show)
};
function dialogue_show(data) {
    if (data.length!=0){
        var str='';
        $.each(data,function (index,row) {
            var name,txt,img,time;
            if (row.nick_name==''||row.nick_name=='null'||row.nick_name=='unknown'){
                name=row.uid;
            }else {
                name=row.nick_name;
            };
            if (row.photo_url==''||row.photo_url=='null'||row.photo_url=='unknown'){
                img='/static/images/unknown.png';
            }else {
                img=row.photo_url;
            };
            if (row.text==''||row.text=='null'||row.text=='unknown'){
                txt='暂无内容';
            }else {
                txt=row.text;
            };
            if (row.update_time==''||row.update_time=='null'||row.update_time=='unknown'){
                time='未知';
            }else {
                time=getLocalTime(row.update_time);
            };
            str+=
                '<div>'+
                '   <div class="_dialogue">'+
                '       <img src="'+img+'" class="center_icon">'+
                '       <div class="center_rel">'+
                '           <a class="center_1" href="https://weibo.com/u/'+row.uid+'" style="color: #f98077;">'+name+'</a>'+
                '           <span class="time" style="font-weight: 900;color:blanchedalmond;"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>  '+
                '           <i class="mid" style="display: none;">'+row.mid+'</i>'+
                '           <i class="uid" style="display: none;">'+row.uid+'</i>'+
                '           <i class="timestamp" style="display: none;">'+row.timestamp+'</i>'+
                '           <span class="center_2">'+txt+ '</span>'+
                '       </div>'+
                '   </div>'+
                '</div>';
        });
        $('#lookDialogue .dialogueContent').html(str);
        $('#lookDialogue').modal('show');
    }else {
        $('#successfail p').text('对话内容为空。');
        $('#successfail').modal('show');
    }
}
//收藏
function collect(_this) {

}
//操作返回结果
function postYES(data) {
    var f='';
    if (data[0]||data){
        f='操作成功';
    }else {
        f='操作失败';
    }
    $('#successfail p').text(f);
    $('#successfail').modal('show');
}
//===========
// =====关注列表====
$('.focusSEN .demo-label input').on('click',function () {
    var orderType=$(this).val();
    var ClickFocusOn_url='/weibo_xnr_manage/wxnr_list_concerns/?user_id='+ID_Num+'&order_type='+orderType;
    public_ajax.call_request('get',ClickFocusOn_url,focusOn);
})
var focusOn_url='/weibo_xnr_manage/wxnr_list_concerns/?user_id='+ID_Num+'&order_type=influence';
public_ajax.call_request('get',focusOn_url,focusOn);
function focusOn(data) {
    $('#focus p').show();
    $('#focus').bootstrapTable('load', data);
    $('#focus').bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 2,//单页记录数
        pageList: [2,5,10,20],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "头像",//标题
                field: "photo_url",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.photo_url==''||row.photo_url=='null'||row.photo_url=='unknown'){
                        return '<img style="width: 30px;height: 30px;" src="/static/images/unknown.png">';
                    }else {
                        return '<img style="width: 30px;height: 30px;" src="'+row.photo_url+'">';
                    };
                }
            },
            {
                title: "用户昵称",//标题
                field: "nick_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.nick_name==''||row.nick_name=='null'||row.nick_name=='unknown'){
                        return row.uid;
                    }else {
                        return row.nick_name;
                    };
                }
            },
            {
                title: "性别",//标题
                field: "sex",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.sex==''||row.sex=='null'||row.sex=='unknown'){
                        return '未知';
                    }else {
                        if (row.sex=='male'){return '男';}else if (row.sex=='female'){return '女'}else {return '未知'}
                    };
                }
            },
            {
                title: "关注来源",//标题
                field: "follow_source",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.follow_source==''||row.follow_source=='null'||row.follow_source=='unknown'||!row.follow_source){
                        return '未知';
                    }else {
                        return row.follow_source;
                    };
                }
            },
            {
                title: "话题领域",//标题
                field: "topic_string",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.topic_string==''||row.topic_string=='null'||row.topic_string=='unknown'||!row.topic_string){
                        return '未知';
                    }else {
                        return row.topic_string.replace(/&/g,',');
                    };
                }
            },
            {
                title: "影响力",//标题
                field: "influence",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.influence==''||row.influence=='null'||row.influence=='unknown'){
                        return 0;
                    }else {
                        return row.influence;
                    };
                }
            },
            {
                title: "敏感度",//标题
                field: "sensitive",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "关注状态",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    var ID=row.uid;
                    return '<span style="cursor: pointer;" onclick="focus_ornot(\''+ID+'\',\'cancel_follow_user\')" title="取消关注"><i class="icon icon-heart"></i></span>';
                        //'<span style="cursor: pointer;" onclick="lookDetails(\''+ID+'\')" title="查看详情"><i class="icon icon-link"></i></span>&nbsp;&nbsp;'+
                        //'<span style="cursor: pointer;" onclick="lookRevise(\''+ID+'\')" title="修改"><i class="icon icon-edit"></i></span>&nbsp;&nbsp;'+
                        //'<span style="cursor: pointer;" onclick="focus_ornot(\''+ID+'\',\'cancel_follow_user\')" title="取消关注"><i class="icon icon-heart-empty"></i></span>';
                }
            },
			 {
                title: "加入重点关注",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    var ID=row.uid;
                    return '<span style="cursor: pointer;" onclick="joinWindow(\''+ID+'\')" title="加入重点关注"><i class="icon icon-star"></i></span>';
                }
            },
        ],
    });
    $('#focus p').slideUp(700);
}
var $id_='';
function joinWindow(id){
	$id_=id;
	 $('#joinHW').modal('show');
}
function joinHeavy(){
	var useradd_url='/weibo_xnr_operate/trace_follow/?xnr_user_no='+ID_Num+'&uid_string='+$id_;
	public_ajax.call_request('get',useradd_url,addSuccess)
}
function addSuccess(data) {
    if (data[0]||data){
        $('#pormpt p').text('加入成功。');
        $('#pormpt').modal('show');
    }else {
        $('#pormpt p').text('加入失败');
        $('#pormpt').modal('show');
    }
}
//=====粉丝列表====
$('.fansSEN .demo-label input').on('click',function () {
    var orderType=$(this).val();
    var clikcFans_url='/weibo_xnr_manage/wxnr_list_fans/?user_id='+ID_Num+'&order_type='+orderType;
    public_ajax.call_request('get',clikcFans_url,fans);
})
var fans_url='/weibo_xnr_manage/wxnr_list_fans/?user_id='+ID_Num+'&order_type=influence';
public_ajax.call_request('get',fans_url,fans);
function fans(data) {
    $('#fans p').show();
    $('#fans').bootstrapTable('load', data);
    $('#fans').bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 2,//单页记录数
        pageList: [2,5,10,20],//分页步进值
        sidePagination: "client",//服务端分页
        searchAlign: "left",
        searchOnEnterKey: false,//回车搜索
        showRefresh: false,//刷新按钮
        showColumns: false,//列选择按钮
        buttonsAlign: "right",//按钮对齐方式
        locale: "zh-CN",//中文支持
        detailView: false,
        showToggle:false,
        sortName:'bci',
        sortOrder:"desc",
        columns: [
            {
                title: "头像",//标题
                field: "photo_url",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.photo_url==''||row.photo_url=='null'||row.photo_url=='unknown'){
                        return '<img style="width: 30px;height: 30px;" src="/static/images/unknown.png">';
                    }else {
                        return '<img style="width: 30px;height: 30px;" src="'+row.photo_url+'">';
                    };
                }
            },
            {
                title: "UID",//标题
                field: "uid",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "用户昵称",//标题
                field: "nick_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.nick_name==''||row.nick_name=='null'||row.nick_name=='unknown'){
                        return row.uid;
                    }else {
                        return row.nick_name;
                    };
                }
            },
            {
                title: "性别",//标题
                field: "sex",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.sex==''||row.sex=='null'||row.sex=='unknown'){
                        return '未知';
                    }else {
                        if (row.sex=='male'){return '男';}else if (row.sex=='female'){return '女'}else {return '未知'}
                    };
                }
            },
            {
                title: "粉丝来源",//标题
                field: "fan_source",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.fan_source==''||row.fan_source=='null'||row.fan_source=='unknown'||!row.fan_source){
                        return '未知';
                    }else {
                        return row.fan_source;
                    };
                }
            },
            {
                title: "所在地",//标题
                field: "user_location",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.user_location==''||row.user_location=='null'||row.user_location=='unknown'){
                        return '未知';
                    }else {
                        return row.user_location;
                    };
                }
            },
            {
                title: "影响力",//标题
                field: "influence",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.influence==''||row.influence=='null'||row.influence=='unknown'||!row.influence){
                        return 0;
                    }else {
                        return row.influence;
                    };
                }
            },
            {
                title: "敏感度",//标题
                field: "sensitive",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "关注状态",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    var ID=row.id;
                    return '<span style="cursor: pointer;" onclick="focus_ornot(\''+ID+'\',\'attach_fans_follow\')" title="直接关注"><i class="icon icon-heart-empty"></i></span>';
                    //'<span style="cursor: pointer;" onclick="lookRevise(\''+ID+'\')" title="查看详情"><i class="icon icon-link"></i></span>&nbsp;&nbsp;'+
                        //'<span style="cursor: pointer;" onclick="lookRevise(\''+ID+'\')" title="修改"><i class="icon icon-edit"></i></span>&nbsp;&nbsp;'+
                        //'<span style="cursor: pointer;" onclick="revoked(\''+ID+'\',\'attach_fans_follow\')" title="直接关注"><i class="icon icon-heart"></i></span>';
                }
            },
        ],
    });
    $('#fans p').slideUp(700);
}
//======查看详情===关注与否====

// function lookDetails(_id) {
//     var details_url='/weibo_xnr_manage/lookup_detail_weibouser/?uid='+_id;
//     public_ajax.call_request('get',details_url,detailsOK);
// }
// function detailsOK(data) {

// }

function focus_ornot(_id,mid) {
    var focusNOT_url='/weibo_xnr_manage/'+mid+'/?xnr_user_no='+ID_Num+'&uid='+_id;
    public_ajax.call_request('get',focusNOT_url,succeedFail);
}
//=========
function succeedFail(data) {
    var t ='操作成功';
    if (!data){t='操作失败'}else {
        setTimeout(function () {
            public_ajax.call_request('get',focusOn_url,focusOn);
            public_ajax.call_request('get',fans_url,fans);
        },700);
    };
    $('#focusOrNot p').text(t);
    $('#focusOrNot').modal('show');
}
