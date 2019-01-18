var operateType='info_detect';
var from_ts=Date.parse(new Date(new Date().setHours(0,0,0,0)))/1000;
var to_ts=Date.parse(new Date())/1000;
$('.title .perTime .demo-label input').on('click',function () {
    var _val=$(this).val();
    if (_val=='resize'){
        $('.titTime').show();
    }else {
        if (_val==0){
            from_ts=todayTimetamp();
        }else {
            from_ts=getDaysBefore(_val);
        }
        $('#content-1-word p').show();
        $('#hot_post p').show();
        $('#userList p').show();
       // public_ajax.call_request('get',word_url,wordCloud);
	//	public_ajax.call_request('get',word_url2,wordCloud2);
        public_ajax.call_request('get',hotPost_url,hotPost);
        public_ajax.call_request('get',activePost_url,activeUser);
        $('.titTime').hide();
    }
});
//选择时间范围
$('.timeSure').on('click',function () {
    $('#content-1-word p').show();
    $('#hot_post p').show();
    $('#userList p').show();
    var from = $('.start').val();
    var to = $('.end').val();
    from_ts=Date.parse(new Date(from))/1000;
    to_ts=Date.parse(new Date(to))/1000;
    if (from_ts==''||to_ts==''){
        $('#pormpt p').text('请检查选择的时间（不能为空）');
        $('#pormpt').modal('show');
    }else {
       // public_ajax.call_request('get',word_url,wordCloud);
		//public_ajax.call_request('get',word_url2,wordCloud2);
        public_ajax.call_request('get',hotPost_url,hotPost);
        public_ajax.call_request('get',activePost_url,activeUser);
    }
});
//----关键词云
var word_url='/facebook_xnr_monitor/lookup_full_keywordstring/?xnr_no='+ID_Num+'&from_ts='+from_ts+'&to_ts='+to_ts;
//public_ajax.call_request('get',word_url,wordCloud);
var word_url2='/facebook_xnr_monitor/lookup_weibo_keywordstring/?from_ts='+from_ts+'&to_ts='+to_ts+'&xnr_no='+ID_Num;
//public_ajax.call_request('get',word_url2,wordCloud2);
//require.config({
  //  paths: {
    //    echarts: '/static/js/echarts-2/build/dist',
   // }
//});
function wordCloud(data) {
    $('#content-1-word p').show();
    if (data.length==0||isEmptyObject(data)){
        $('#content-1-word').css({textAlign:"center",lineHeight:"300px",fontSize:'24px'}).text('暂无数据');
    }else {
        var wordSeries=[];
        for (var k in data){
            wordSeries.push(
                {
                    name: k,
                    value: data[k]*200,
                    itemStyle: createRandomItemStyle()
                }
            )
        }
        require(
            [
                'echarts',
                'echarts/chart/wordCloud'
            ],
            //关键词
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChart = ec.init(document.getElementById('content-1-word'));
                option = {
                    title: {
                        text: '',
                    },
                    // tooltip: {
                    //     show: true,
                    // },
                    series: [{
                        type: 'wordCloud',
                        size: ['90%', '90%'],
                        textRotation : [0, 0, 0, 0],
                        textPadding: 0,
                        autoSize: {
                            enable: true,
                            minSize: 18
                        },
                        data: wordSeries
                    }]
                };
                myChart.setOption(option);
            }
        );
    }
    $('#content-1-word p').slideUp(700);
}
function wordCloud2(data) {
    if (data.length==0||isEmptyObject(data)){
       $('#content-2-word').css({textAlign:"center",lineHeight:"300px",fontSize:'24px'}).text('暂无数据');
    }else {
        var wordSeries=[];
        for (var k in data){
            wordSeries.push(
                {
                    name: k,
                    value: data[k]*200,
                    itemStyle: createRandomItemStyle()
                }
            )
        }
        require(
            [
                'echarts',
                'echarts/chart/wordCloud'
            ],
            //关键词
            function (ec) {
                // 基于准备好的dom，初始化echarts图表
                var myChart = ec.init(document.getElementById('content-2-word'));
                option = {
                    title: {
                        text: '虚拟人关注',
						 textStyle:{color:'#fff'}
                    },
                    // tooltip: {
                    //     show: true,
                    // },
                    series: [{
                        type: 'wordCloud',
                        size: ['90%', '90%'],
                        textRotation : [0, 0, 0, 0],
                        textPadding: 0,
                        autoSize: {
                            enable: true,
                            minSize: 18
                        },
                        data: wordSeries
                    }]
                };
                myChart.setOption(option);
            }
        );
    }
    $('#content-2-word p').slideUp(700);
}
//热门帖子
$('#theme-2 .demo-radio').on('click',function () {
    $('#hot_post p').show();
    var classify_id=$(this).val();
    var order_id=$('#theme-3 input:radio[name="demo"]:checked').val();
    var NEWhotPost_url='/facebook_xnr_monitor/lookup_hot_posts/?from_ts='+from_ts+'&to_ts='+to_ts+
        '&xnr_no='+ID_Num+'&classify_id='+classify_id+'&order_id='+order_id;
    public_ajax.call_request('get',NEWhotPost_url,hotPost);
});
$('#theme-3 .demo-radio').on('click',function () {
    $('#hot_post p').show();
    var classify_id=$('#theme-2 input:radio[name="demo-radio"]:checked').val();
    var order_id=$(this).val();
    var NEWhotPost_url='/facebook_xnr_monitor/lookup_hot_posts/?from_ts='+from_ts+'&to_ts='+to_ts+
        '&xnr_no='+ID_Num+'&classify_id='+classify_id+'&order_id='+order_id;
    public_ajax.call_request('get',NEWhotPost_url,hotPost);
});
var hotPost_url='/facebook_xnr_monitor/lookup_hot_posts/?from_ts='+from_ts+'&to_ts='+to_ts+
    '&xnr_no='+ID_Num+'&classify_id=0&order_id=1';
public_ajax.call_request('get',hotPost_url,hotPost);
function hotPost(data) {
    $('#hot_post').bootstrapTable('load', data);
    $('#hot_post').bootstrapTable({
        data:data,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
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
                title: "",//标题
                field: "",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    var name,txt,img,txt2,all='';
                    if (row.nick_name==''||row.nick_name=='null'||row.nick_name=='unknown'||!row.nick_name){
                        name=row.uid;
                    }else {
                        name=row.nick_name;
                    };
                    if (row.photo_url==''||row.photo_url=='null'||row.photo_url=='unknown'||!row.photo_url){
                        img='/static/images/unknown.png';
                    }else {
                        img=row.photo_url;
                    };
                    if (row.text==''||row.text=='null'||row.text=='unknown'){
                        txt='暂无内容';
                    }else {
                        if (row.sensitive_words_string||!isEmptyObject(row.sensitive_words_string)){
                            var keyword=row.sensitive_words_string.split('&');
                            for (var f of keyword){
                                txt=row.text.toString().replace(new RegExp(f,'g'),'<b style="color:#ef3e3e;">'+f+'</b>');
                            }
                            var rrr=row.text;
                            if (rrr.length>=160){
                                rrr=rrr.substring(0,160)+'...';
                                all='inline-block';
                            }else {
                                rrr=row.text;
                                all='none';
                            }
                            for (var f of keyword){
                                txt2=rrr.toString().replace(new RegExp(f,'g'),'<b style="color:#ef3e3e;">'+f+'</b>');
                            }
                        }else {
                            txt=row.text;
                            if (txt.length>=160){
                                txt2=txt.substring(0,160)+'...';
                                all='inline-block';
                            }else {
                                txt2=txt;
                                all='none';
                            }
                        };
                    };
                    var str=
                        '<div class="post_perfect" style="margin-bottom:10px;width:920px;">'+
                        '   <div class="post_center-hot">'+
                        '       <img src="'+img+'" alt="" class="center_icon">'+
                        '       <div class="center_rel">'+
                        '           <a class="center_1" href="###" style="color: #f98077;">'+name+'</a>&nbsp;'+
                        '           <i class="fid" style="display: none;">'+row.fid+'</i>'+
                        '           <i class="uid" style="display: none;">'+row.uid+'</i>'+
                        '           <i class="timestamp" style="display: none;">'+row.timestamp+'</i>'+
                        '           <span class="time" style="font-weight: 900;color:#f6a38e;"><i class="icon icon-time"></i>&nbsp;&nbsp;'+getLocalTime(row.timestamp)+'</span>  '+
                        '           <button data-all="0" style="display:'+all+'" type="button" class="btn btn-primary btn-xs allWord" onclick="allWord(this)">查看全文</button>'+
                        '           <p class="allall1" style="display:none;">'+txt+'</p>'+
                        '           <p class="allall2" style="display:none;">'+txt2+'</p>'+
                        '           <span class="center_2">'+txt2+'</span>'+
                        '           <div class="_translate" style="display: none;"><b style="color: #f98077;">译文：</b><span class="tsWord"></span></div>'+
                        '           <div class="center_3">'+
                        '               <span class="cen3-1" onclick="retweet(this,\''+operateType+'\')"><i class="icon icon-share"></i>&nbsp;&nbsp;分享（<b class="forwarding">'+row.share+'</b>）</span>'+
                        '               <span class="cen3-2" onclick="showInput(this)"><i class="icon icon-comments-alt"></i>&nbsp;&nbsp;评论（<b class="comment">'+row.comment+'</b>）</span>'+
                        '               <span class="cen3-3" onclick="thumbs(this)"><i class="icon icon-thumbs-up"></i>&nbsp;&nbsp;喜欢(<b class="like">'+row.favorite+'</b>)</span>'+
                        '               <span class="cen3-4" onclick="emailThis(this)"><i class="icon icon-envelope"></i>&nbsp;&nbsp;私信</span>'+
                        '               <span class="cen3-9" onclick="robot(this)"><i class="icon icon-github-alt"></i>&nbsp;&nbsp;机器人回复</span>'+
                        '               <span class="cen3-5" onclick="joinlab(this)"><i class="icon icon-signin"></i>&nbsp;&nbsp;加入语料库</span>'+
                        '               <span class="cen3-5" onclick="translateWord(this)"><i class="icon icon-exchange"></i>&nbsp;&nbsp;翻译</span>'+
                        '           </div>'+
                        '           <div class="forwardingDown" style="width: 100%;display: none;">'+
                        '               <input type="text" class="forwardingIput" placeholder="分享内容"/>'+
                        '               <span class="sureFor" onclick="forwardingBtn()">分享</span>'+
                        '           </div>'+
                        '           <div class="commentDown" style="width: 100%;display: none;">'+
                        '               <input type="text" class="comtnt" placeholder="评论内容"/>'+
                        '               <span class="sureCom" onclick="comMent(this,\''+operateType+'\')">评论</span>'+
                        '           </div>'+
                        '           <div class="emailDown" style="width: 100%;display: none;">'+
                        '               <input type="text" class="infor" placeholder="私信内容"/>'+
                        '               <span class="sureEmail" onclick="letter(this)">发送</span>'+
                        '           </div>'+
                        '       </div>'+
                        '    </div>'+
                        '</div>';
                    return str;
                }
            },
        ],
    });
    $('#hot_post p').slideUp(700);
    $('.hot_post .search .form-control').attr('placeholder','输入关键词快速搜索相关微博（回车搜索）');
}

//活跃用户
$('#user-1 .demo-radio').on('click',function () {
    var classify_id=$('#user-1 input:radio[name="deadio"]:checked').val();
    var NEWactivePost_url='/facebook_xnr_monitor/lookup_active_user/?xnr_no='+ID_Num+'&from_ts='+
        from_ts+'&to_ts='+to_ts+'&classify_id=0';
    public_ajax.call_request('get',NEWactivePost_url,activeUser);
});
var activePost_url='/facebook_xnr_monitor/lookup_active_user/?xnr_no='+ID_Num+'&from_ts='+
    from_ts+'&to_ts='+to_ts+'&classify_id=0';
public_ajax.call_request('get',activePost_url,activeUser);
var act_user_list=[];
function activeUser(persondata) {
    $('#userList p').show();
    $('.userList #userList').bootstrapTable('load', persondata);
    $('.userList #userList').bootstrapTable({
        data:persondata,
        search: true,//是否搜索
        pagination: true,//是否分页
        pageSize: 5,//单页记录数
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
                title: "添加关注",//标题
                field: "select",
                checkbox: true,
                align: "center",//水平
                valign: "middle"//垂直
            },
            {
                title: "头像",//标题
                field: "url",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.url==''||row.url=='null'||row.url=='unknown'||!row.url){
                        return '<img style="width: 20px;height: 20px;" src="/static/images/unknown.png"/>';
                    }else {
                        return '<img style="width: 20px;height: 20px;" src="'+row.url+'"/>';
                    };
                }
            },
            {
                title: "用户ID",//标题
                field: "uid",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                // formatter: function (value, row, index) {
                //     return row[1];
                // }
            },
            {
                title: "昵称",//标题
                field: "uname",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.uname==''||row.uname=='null'||row.uname=='unknown'){
                        return '无昵称';
                    }else {
                        return row.uname;
                    };
                }
            },
            {
                title: "注册地",//标题
                field: "location",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.location==''||row.location=='null'||row.location=='unknown'){
                        return '未知';
                    }else {
                        return row.location;
                    };
                }
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
                title: "发帖数",//标题
                field: "total_number",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.total_number==''||row.total_number=='null'||row.total_number=='unknown'||!row.total_number){
                        return '0';
                    }else {
                        return row.total_number;
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
                        return '0';
                    }else {
                        return row.influence.toFixed(2);
                    };
                }
            },
            // {
            //     title: "网民详情",//标题
            //     field: "",//键名
            //     sortable: true,//是否可排序
            //     order: "desc",//默认排序方式
            //     align: "center",//水平
            //     valign: "middle",//垂直
            //     formatter: function (value, row, index) {
            //         return '<span style="cursor: pointer;" onclick="networkPeo(\''+row.id+'\')" ' +
            //             'title="查看详情"><i class="icon icon-link"></i></span>'
            //     },
            // },
        ],
        onCheck:function (row) {
            act_user_list.push(row.uid);_judge()
        },
        onUncheck:function (row) {
            act_user_list.removeByValue(row.uid);_judge()
        },
        onCheckAll:function (row) {
            act_user_list.push(row.uid);_judge()
        },
        onUncheckAll:function (row) {
            act_user_list.removeByValue(row.uid);_judge()
        },
    });
    $('#userList p').slideUp(700);
};
function _judge() {
    if (act_user_list.length==0){
        $('.userList .addFocus').addClass('disableCss');
    }else {
        $('.userList .addFocus').removeClass('disableCss');
    }
}
$('.userList .addFocus').on('click',function () {
    var add_url='/facebook_xnr_monitor/attach_fans_batch/?xnr_user_no_list='+ID_Num+'&fans_id_list='+act_user_list.join(',');
    public_ajax.call_request('get',add_url,postYES);
})

//关注该用户
function focusThis(_this) {
    var uid = $(_this).parents('.post_perfect').find('.uid').text();
    var post_url_6='/facebook_xnr_monitor/attach_fans_follow/?xnr_user_no='+ID_Num+'&uid='+uid;
    public_ajax.call_request('get',post_url_6,postYES)
}
//操作返回结果
function postYES(data) {
    var f='';
    if (data[0]||data||data[0][0]){
        f='操作成功';
    }else {
        f='操作失败';
    }
    $('#pormpt p').text(f);
    $('#pormpt').modal('show');
}
