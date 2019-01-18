var has_url = '/weibo_xnr_manage/show_completed_weiboxnr/?account_no='+admin;
var notHao_url = '/weibo_xnr_manage/show_uncompleted_weiboxnr/?account_no='+admin;
public_ajax.call_request('GET',has_url,has_table);
public_ajax.call_request('GET',notHao_url,not_yet);
function has_table(has_data) {
    var person=eval(has_data);
    $('.has_list #haslist').bootstrapTable('load', person);
    $('.has_list #haslist').bootstrapTable({
        data:person,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 10,//单页记录数
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
                title: "编号",//标题
                field: "xnr_user_no",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[1];
                // }
            },
            {
                title: "创建时间",//标题
                field: "create_time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.create_time==''||row.create_time=='null'||row.create_time=='unknown'||!row.create_time){
                        return '暂无';
                    }else {
                        return getLocalTime(row.create_time);
                    };
                }
            },
            {
                title: "渗透领域",//标题
                field: "domain_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.domain_name==''||row.domain_name=='null'||row.domain_name=='unknown'){
                        return '暂无';
                    }else {
                        return row.domain_name;
                    }
                },
            },
            {
                title: "角色定位",//标题
                field: "role_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.role_name==''||row.role_name=='null'||row.role_name=='unknown'){
                        return '暂无';
                    }else {
                        return row.role_name;
                    }
                },
            },
            {
                title: "活跃时间",//标题
                field: "active_time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.active_time==''||row.active_time=='null'||row.active_time=='unknown'||!row.active_time){
                        return '暂无';
                    }else {
                        var t=row.active_time.split(','),str='';
                        for(var k of t){
                            str+=k+'时 ';
                        }
                        return str;
                    };
                },
            },
            {
                title: "粉丝数",//标题
                field: "fans_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "历史发帖量",//标题
                field: "history_post_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "历史评论数",//标题
                field: "history_comment_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "今日发帖量",//标题
                field: "today_comment_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
            },
            {
                title: "今日提醒",//标题
                field: "today_remind_num",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    return '<a style="cursor: pointer;color:white;" onclick="alarm(\''+row.xnr_user_no+'\')"><i class="icon icon-bell-alt"></i>&nbsp;&nbsp;'+row.today_remind_num+'</a>';
                },
            },
            {
                title: '操作',//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    return '<a style="cursor: pointer;color:white;" onclick="comeIn(\''+row.xnr_user_no+'\',\''+row.nick_name+'\')" title="进入"><i class="icon icon-link"></i></a>&nbsp;&nbsp;'+
                        '<a style="cursor: pointer;color:white;" onclick="go_on(\''+row.xnr_user_no+'\',\'1\',\''+row.xnr_user_no+'\')" title="修改"><i class="icon icon-edit"></i></a>&nbsp;&nbsp;'+
                        '<a style="cursor: pointer;color:white;" onclick="deluser(\''+row.xnr_user_no+'\',\'1\')" title="删除"><i class="icon icon-trash"></i></a>';
                },
            },
        ],
    });
    $('.has_list #haslist p').slideUp(700);
};
function not_yet(no_data) {
    var undone_person=eval(no_data);
    $('.undone_list #undonelist').bootstrapTable('load', undone_person);
    $('.undone_list #undonelist').bootstrapTable({
        data:undone_person,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 10,//单页记录数
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
                title: "创建时间",//标题
                field: "create_time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.create_time==''||row.create_time=='null'||row.create_time=='unknown'||!row.create_time){
                        return '未知';
                    }else {
                        return getLocalTime(row.create_time);
                    };
                }
            },
            {
                title: "渗透领域",//标题
                field: "domain_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.domain_name==''||row.domain_name=='null'||row.domain_name=='unknown'){
                        return '暂无';
                    }else {
                        return row.domain_name;
                    }
                },
            },
            {
                title: "角色定位",//标题
                field: "role_name",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.role_name==''||row.role_name=='null'||row.role_name=='unknown'){
                        return '暂无';
                    }else {
                        return row.role_name;
                    }
                },
            },
            {
                title: "活跃时间",//标题
                field: "active_time",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.active_time==''||row.active_time=='null'||row.active_time=='unknown'||!row.active_time){
                        return '暂无';
                    }else {
                        var t=row.active_time.split(','),str='';
                        for(var k of t){
                            str+=k+'时 ';
                        }
                        return str;
                    };
                },
            },
            {
                title: '操作',//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    return '<a style="cursor: pointer;color: white;" onclick="go_on(\''+row.xnr_user_no+'\',\'2\',\''+row.xnr_user_no+'\')" title="继续"><i class="icon icon-fire"></i></a>'+
                        '<a style="cursor: pointer;color: white;display:inline-block;margin-left:50px;" onclick="deluser(\''+row.xnr_user_no+'\',\'2\')" title="删除"><i class="icon icon-trash"></i></a>';
                },
            },
        ],
    });
    $('.undone_list #undonelist p').slideUp(700);
};
//今日提醒
function alarm(id) {
    var clock_url = '/weibo_xnr_manage/xnr_today_remind/?xnr_user_no='+id;
    public_ajax.call_request('GET',clock_url,clock);
}
function clock(data) {
    $('#alarm .ala-1 p').text(data['post_remind_content']);
    var str='',r=0;
    for (var i of data['date_remind_content']){
        r++;
        str+='<p><span class="badge" style="margin-right: 5px;vertical-align: baseline;">'+r+'</span>'+i+'</p>';
    }
    $('#alarm .ala-2 div').html(str);
    $('#alarm').modal('show');
}
//删除虚拟人
var uploadUser,delID;
function deluser(id,flag) {
    uploadUser=flag;
    delID=id;
    $('#delPrompt').modal('show');
}
function sureDelXnr() {
    var del_url = '/weibo_xnr_manage/delete_weibo_xnr/?xnr_user_no='+delID;
    public_ajax.call_request('GET',del_url,success_fail);
}
//继续创建未完成的虚拟人
function go_on(id,flag,taskID) {
    localStorage.setItem('go_mod_user',id);
    //window.open('/registered/virtualCreated/?continueUser='+flag+'&flag=1&taskID='+taskID);
	window.location.href = '/registered/virtualCreated/?continueUser='+flag+'&flag=1&taskID='+taskID;	

    // var go_url = '/weibo_xnr_manage/change_continue_xnrinfo/?xnr_user_no='+id;
    // public_ajax.call_request('GET',go_url,success_fail);
}
//进入操作统计
var comingID,comingNAME;
function comeIn(id,name) {
    comingID=id;comingNAME=name;
    $('#choosePerson_3').modal('show');
}
$('#choosePerson_3 .sure_in').on('click',function () {
    var userType=$('#choosePerson_3 input:radio[name="choose_3"]:checked').val();
    if (userType){
        var id_or_name='';
        if (userType=='隐身'){
            id_or_name=comingID;
        }else {
            id_or_name=comingNAME;
        }
        localStorage.setItem('user',comingID);
        localStorage.setItem('userName',id_or_name);
        //window.open('/control/operationControl/');
		window.location.href = '/control/operationControl/';
    }else {
        $('#succee_fail #words').text('请选择登录方式');
        $('#succee_fail').modal('show');
    }

});

function success_fail(data) {
    var word='';
    if (data){
        word='删除成功。';
        setTimeout(function () {
            if (uploadUser=='1'){
                public_ajax.call_request('GET',has_url,has_table);
            }else {
                public_ajax.call_request('GET',notHao_url,not_yet);
            }
        },1000);
    }else {
        word='删除失败。';
    }
    $('#succee_fail #words').text(word);
    $('#succee_fail').modal('show');
}




