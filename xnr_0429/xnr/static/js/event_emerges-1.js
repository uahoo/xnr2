var time2=Date.parse(new Date())/1000;
var weiboUrl='/weibo_xnr_warming_new/show_event_warming/?xnr_user_no='+ID_Num+'&start_time='+todayTimetamp()+'&end_time='+time2;
public_ajax.call_request('get',weiboUrl,weibo);
//时间选择
$('.choosetime .demo-label input').on('click',function () {     
    var _val = $(this).val();
    if (_val == 'mize') {
        $(this).parents('.choosetime').find('#start').show();
        $(this).parents('.choosetime').find('#end').show();
        $(this).parents('.choosetime').find('#sure').css({display: 'inline-block'});
    } else {
        $('#group_emotion_loading').show();
        $(this).parents('.choosetime').find('#start').hide();
        $(this).parents('.choosetime').find('#end').hide();
        $(this).parents('.choosetime').find('#sure').hide();
        var weiboUrl='/weibo_xnr_warming_new/show_event_warming/?xnr_user_no='+ID_Num+'&start_time='+getDaysBefore(_val)+'&end_time='+time2;
        public_ajax.call_request('get',weiboUrl,weibo);
    }
});
$('#sure').on('click',function () {
     $('#group_emotion_loading').show();
    var s=$(this).parents('.choosetime').find('#start').val();
    var d=$(this).parents('.choosetime').find('#end').val();
    if (s==''||d==''){
        $('#pormpt p').text('时间不能为空。');
        $('#pormpt').modal('show');
    }else {
        var weiboUrl='/weibo_xnr_warming_new/show_event_warming/?xnr_user_no='+ID_Num+'&start_time='+
            (Date.parse(new Date(s))/1000)+'&end_time='+(Date.parse(new Date(d))/1000);
        public_ajax.call_request('get',weiboUrl,weibo);
    }
});

//文本信息
var contentList = {};
function weibo(data){
    $.each(data,function (index,item) {
        contentList['exo_'+index]=item;
    })
    // $('#input-table').css('display', 'block');
    var dataArray = data;
    var PageNo=document.getElementById('PageNo');                   //设置每页显示行数
    var InTb=document.getElementById('input-table');               //表格
    var Fp=document.getElementById('F-page');                      //首页
    var Nep=document.getElementById('Nex-page');                  //下一页
    var Prp=document.getElementById('Pre-page');                  //上一页
    var Lp=document.getElementById('L-page');                     //尾页
    var S1=document.getElementById('s1');                         //总页数
    var S2=document.getElementById('s2');                         //当前页数
    var currentPage;                                              //定义变量表示当前页数
    var SumPage;

    if(PageNo.value!="")                                       //判断每页显示是否为空
    {
        InTb.innerHTML='';                                     //每次进来都清空表格
        S2.innerHTML='';                                        //每次进来清空当前页数
        currentPage=1;                                          //首页为1
        S2.appendChild(document.createTextNode(currentPage));
        S1.innerHTML='';                                        //每次进来清空总页数
        if(dataArray.length%PageNo.value==0)                    //判断总的页数
        {
            SumPage=parseInt(dataArray.length/PageNo.value);
        }
        else
        {
            SumPage=parseInt(dataArray.length/PageNo.value)+1
        }
        S1.appendChild(document.createTextNode(SumPage));
        var oTBody=document.createElement('tbody');               //创建tbody
        oTBody.setAttribute('class','In-table');                   //定义class
        InTb.appendChild(oTBody);                                     //将创建的tbody添加入table
        var html_c = '';

        if(dataArray==''){
            html_c = "<p style='text-align: center'>暂无内容</p>";
            oTBody.innerHTML = html_c;
        }else{
            for(i=0;i<parseInt(PageNo.value);i++)
            {                                                          //循环打印数组值
                oTBody.insertRow(i);
                html_c =
                    '<div class="everyEvent everyUser" style="margin:0 auto;text-align: left;">'+
                    '        <div class="event_center">'+
                    '            <div style="margin:10px;">'+
                    // '                <label class="demo-label">'+
                    // '                    <input class="demo-radio" type="checkbox" name="demo-checkbox">'+
                    // '                    <span class="demo-checkbox demo-radioInput"></span>'+
                    // '                </label>'+
                    '                <img src="/static/images/post-6.png" class="center_icon">'+
                    '                <a class="center_1 centerNAME">'+dataArray[i].event_name.replace(/&/g,'#')+'</a>'+
                    '                <a class="_id" style="display: none;">'+dataArray[i]._id+'</a>'+
                    '                <a class="report" onclick="oneUP(this,\'事件\')" style="margin-left: 50px;"><i class="icon icon-upload-alt"></i>  上报</a>'+
                    '            </div>'+
                    '            <div class="centerdetails" style="padding-left:40px;">'+
                    '                <div class="event-1">'+
                    '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 主要参与用户</p>'+
                    '                    <div class="mainJoin">'+
                    '                        <div class="mainJoinTable'+i+'"></div>'+
                    '                    </div>'+
                    '                </div>'+
                    '                <div class="event-2">'+
                    '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 相关典型微博</p>'+
                    '                    <div class="mainWeibo">'+
                    '                        <div class="mainWeiboTable'+i+'"></div>'+
                    '                    </div>'+
                    '                </div>'+
                    '            </div>'+
                    '        </div>'+
                    '    </div>';
                oTBody.rows[i].insertCell(0);
                oTBody.rows[i].cells[0].innerHTML = html_c;
                startTable(i);
            }
        }
    }

    Fp.onclick=function()
    {

        if(PageNo.value!="")                                       //判断每页显示是否为空
        {
            InTb.innerHTML='';                                     //每次进来都清空表格
            S2.innerHTML='';                                        //每次进来清空当前页数
            currentPage=1;                                          //首页为1
            S2.appendChild(document.createTextNode(currentPage));
            S1.innerHTML='';                                        //每次进来清空总页数
            if(dataArray.length%PageNo.value==0)                    //判断总的页数
            {
                SumPage=parseInt(dataArray.length/PageNo.value);
            }
            else
            {
                SumPage=parseInt(dataArray.length/PageNo.value)+1
            }
            S1.appendChild(document.createTextNode(SumPage));
            var oTBody=document.createElement('tbody');               //创建tbody
            oTBody.setAttribute('class','In-table');                   //定义class
            InTb.appendChild(oTBody);                                     //将创建的tbody添加入table
            var html_c = '';
            if(dataArray==''){
                html_c = "<p style='width:840px;text-align: center'>暂无内容</p>";
                oTBody.innerHTML = html_c;
            }else{
                for(i=0;i<parseInt(PageNo.value);i++)
                {                                                          //循环打印数组值
                    oTBody.insertRow(i);
                    html_c =
                        '<div class="everyEvent everyUser" style="margin:0 auto 20px;text-align: left;">'+
                        '        <div class="event_center">'+
                        '            <div style="margin:10px;">'+
                        // '                <label class="demo-label">'+
                        // '                    <input class="demo-radio" type="checkbox" name="demo-checkbox">'+
                        // '                    <span class="demo-checkbox demo-radioInput"></span>'+
                        // '                </label>'+
                        '                <img src="/static/images/post-6.png" class="center_icon">'+
                        '                <a class="center_1 centerNAME">'+dataArray[i].event_name.replace(/&/g,'#')+'</a>'+
                        '                <a class="_id" style="display: none;">'+dataArray[i]._id+'</a>'+
                        '                <a class="report" onclick="oneUP(this,\'事件\')" style="margin-left: 50px;"><i class="icon icon-upload-alt"></i>  上报</a>'+
                        '            </div>'+
                        '            <div class="centerdetails" style="padding-left:40px;">'+
                        '                <div class="event-1">'+
                        '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 主要参与用户</p>'+
                        '                    <div class="mainJoin">'+
                        '                        <div class="mainJoinTable'+i+'"></div>'+
                        '                    </div>'+
                        '                </div>'+
                        '                <div class="event-2">'+
                        '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 相关典型微博</p>'+
                        '                    <div class="mainWeibo">'+
                        '                        <div class="mainWeiboTable'+i+'"></div>'+
                        '                    </div>'+
                        '                </div>'+
                        '            </div>'+
                        '        </div>'+
                        '    </div>';
                    oTBody.rows[i].insertCell(0);
                    oTBody.rows[i].cells[0].innerHTML = html_c;
                    startTable(i);
                }
            }
        }
    }

    Nep.onclick=function()
    {
        if(currentPage<SumPage)                                 //判断当前页数小于总页数
        {
            InTb.innerHTML='';
            S1.innerHTML='';
            if(dataArray.length%PageNo.value==0)
            {
                SumPage=parseInt(dataArray.length/PageNo.value);
            }
            else
            {
                SumPage=parseInt(dataArray.length/PageNo.value)+1
            }
            S1.appendChild(document.createTextNode(SumPage));
            S2.innerHTML='';
            currentPage=currentPage+1;
            S2.appendChild(document.createTextNode(currentPage));
            var oTBody=document.createElement('tbody');
            oTBody.setAttribute('class','In-table');
            InTb.appendChild(oTBody);
            var a;                                                 //定义变量a
            a=PageNo.value*(currentPage-1);                       //a等于每页显示的行数乘以上一页数
            var c;                                                  //定义变量c
            if(dataArray.length-a>=PageNo.value)                  //判断下一页数组数据是否小于每页显示行数
            {
                c=PageNo.value;
            }
            else
            {
                c=dataArray.length-a;
            }
            for(i=0;i<c;i++)
            {
                oTBody.insertRow(i);
                oTBody.rows[i].insertCell(0);
                html_c =
                    '<div class="everyEvent everyUser" style="margin:0 auto 20px;text-align: left;">'+
                    '        <div class="event_center">'+
                    '            <div style="margin:10px;">'+
                    // '                <label class="demo-label">'+
                    // '                    <input class="demo-radio" type="checkbox" name="demo-checkbox">'+
                    // '                    <span class="demo-checkbox demo-radioInput"></span>'+
                    // '                </label>'+
                    '                <img src="/static/images/post-6.png" class="center_icon">'+
                    '                <a class="center_1 centerNAME">'+dataArray[i+a].event_name.replace(/&/g,'#')+'</a>'+
                    '                <a class="_id" style="display: none;">'+dataArray[i+a]._id+'</a>'+
                    '                <a class="report" onclick="oneUP(this,\'事件\')" style="margin-left: 50px;"><i class="icon icon-upload-alt"></i>  上报</a>'+
                    '            </div>'+
                    '            <div class="centerdetails" style="padding-left:40px;">'+
                    '                <div class="event-1">'+
                    '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 主要参与用户</p>'+
                    '                    <div class="mainJoin">'+
                    '                        <div class="mainJoinTable'+(i+a)+'"></div>'+
                    '                    </div>'+
                    '                </div>'+
                    '                <div class="event-2">'+
                    '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 相关典型微博</p>'+
                    '                    <div class="mainWeibo">'+
                    '                        <div class="mainWeiboTable'+(i+a)+'"></div>'+
                    '                    </div>'+
                    '                </div>'+
                    '            </div>'+
                    '        </div>'+
                    '    </div>';
                oTBody.rows[i].cells[0].innerHTML = html_c;
                //数组从第i+a开始取值
                startTable(a+i);
            }
        }
    }

    Prp.onclick=function()
    {
        if(currentPage>1)                        //判断当前是否在第一页
        {
            InTb.innerHTML='';
            S1.innerHTML='';
            if(dataArray.length%PageNo.value==0)
            {
                SumPage=parseInt(dataArray.length/PageNo.value);
            }
            else
            {
                SumPage=parseInt(dataArray.length/PageNo.value)+1
            }
            S1.appendChild(document.createTextNode(SumPage));
            S2.innerHTML='';
            currentPage=currentPage-1;
            S2.appendChild(document.createTextNode(currentPage));
            var oTBody=document.createElement('tbody');
            oTBody.setAttribute('class','In-table');
            InTb.appendChild(oTBody);
            var a;
            a=PageNo.value*(currentPage-1);
            for(i=0;i<parseInt(PageNo.value);i++)
            {
                oTBody.insertRow(i);
                oTBody.rows[i].insertCell(0);
                html_c =
                    '<div class="everyEvent everyUser" style="margin:0 auto 20px;text-align: left;">'+
                    '        <div class="event_center">'+
                    '            <div style="margin:10px;">'+
                    // '                <label class="demo-label">'+
                    // '                    <input class="demo-radio" type="checkbox" name="demo-checkbox">'+
                    // '                    <span class="demo-checkbox demo-radioInput"></span>'+
                    // '                </label>'+
                    '                <img src="/static/images/post-6.png" class="center_icon">'+
                    '                <a class="center_1 centerNAME">'+dataArray[i+a].event_name.replace(/&/g,'#')+'</a>'+
                    '                <a class="_id" style="display: none;">'+dataArray[i+a]._id+'</a>'+
                    '                <a class="report" onclick="oneUP(this,\'事件\')" style="margin-left: 50px;"><i class="icon icon-upload-alt"></i>  上报</a>'+
                    '            </div>'+
                    '            <div class="centerdetails" style="padding-left:40px;">'+
                    '                <div class="event-1">'+
                    '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 主要参与用户</p>'+
                    '                    <div class="mainJoin">'+
                    '                        <div class="mainJoinTable'+(i+a)+'"></div>'+
                    '                    </div>'+
                    '                </div>'+
                    '                <div class="event-2">'+
                    '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 相关典型微博</p>'+
                    '                    <div class="mainWeibo">'+
                    '                        <div class="mainWeiboTable'+(i+a)+'"></div>'+
                    '                    </div>'+
                    '                </div>'+
                    '            </div>'+
                    '        </div>'+
                    '    </div>';
                oTBody.rows[i].cells[0].innerHTML = html_c;
                console.log(a+i)
                startTable(a+i);
            }
        }
    }

    Lp.onclick=function()
    {
        InTb.innerHTML='';
        S1.innerHTML='';
        if(dataArray.length%PageNo.value==0)
        {
            SumPage=parseInt(dataArray.length/PageNo.value);
        }
        else
        {
            SumPage=parseInt(dataArray.length/PageNo.value)+1
        }
        S1.appendChild(document.createTextNode(SumPage));
        S2.innerHTML='';
        currentPage=SumPage;
        S2.appendChild(document.createTextNode(currentPage));
        var oTBody=document.createElement('tbody');
        oTBody.setAttribute('class','In-table');
        InTb.appendChild(oTBody);
        var a;
        a=PageNo.value*(currentPage-1);
        var c;
        if(dataArray.length-a>=PageNo.value)
        {
            c=PageNo.value;
        }
        else
        {
            c=dataArray.length-a;
        }
        for(i=0;i<c;i++)
        {
            oTBody.insertRow(i);
            oTBody.rows[i].insertCell(0);
            html_c =
                '<div class="everyEvent everyUser" style="margin:0 auto 20px;text-align: left;">'+
                '        <div class="event_center">'+
                '            <div style="margin:10px;">'+
                // '                <label class="demo-label">'+
                // '                    <input class="demo-radio" type="checkbox" name="demo-checkbox">'+
                // '                    <span class="demo-checkbox demo-radioInput"></span>'+
                // '                </label>'+
                '                <img src="/static/images/post-6.png" class="center_icon">'+
                '                <a class="center_1 centerNAME">'+dataArray[i+a].event_name.replace(/&/g,'#')+'</a>'+
                '                <a class="_id" style="display: none;">'+dataArray[i+a]._id+'</a>'+
                '                <a class="report" onclick="oneUP(this,\'事件\')" style="margin-left: 50px;"><i class="icon icon-upload-alt"></i>  上报</a>'+
                '            </div>'+
                '            <div class="centerdetails" style="padding-left:40px;">'+
                '                <div class="event-1">'+
                '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 主要参与用户</p>'+
                '                    <div class="mainJoin">'+
                '                        <div class="mainJoinTable'+(i+a)+'"></div>'+
                '                    </div>'+
                '                </div>'+
                '                <div class="event-2">'+
                '                    <p style="font-size: 16px;color:#01b4ff;"><i class="icon icon-bookmark"></i> 相关典型微博</p>'+
                '                    <div class="mainWeibo">'+
                '                        <div class="mainWeiboTable'+(i+a)+'"></div>'+
                '                    </div>'+
                '                </div>'+
                '            </div>'+
                '        </div>'+
                '    </div>';
            oTBody.rows[i].cells[0].innerHTML = html_c;
            startTable(a);
        }
    }

    $('#group_emotion_loading').css('display', 'none');
}

function startTable(index) {
    mainJoin(contentList['exo_'+index]['main_user_info'],index)
    mainWeibo(contentList['exo_'+index]['main_weibo_info'],index);
}
function mainJoin(data,idx) {
    $('.mainJoinTable'+idx).bootstrapTable('load', data);
    $('.mainJoinTable'+idx).bootstrapTable({
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
                title: "头像",//标题
                field: "photo_url",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.photo_url==''||row.photo_url=='null'||row.photo_url=='unknown'||!row.photo_url){
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
                    if (row.nick_name==''||row.nick_name=='unknown'||row.nick_name=='numm'||!row.nick_name){
                        return row.uid;
                    }else {
                        return row.nick_name;
                    }
                },
            },
            {
                title: "关注数",//标题
                field: "favoritesnum",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.favoritesnum==''||row.favoritesnum=='unknown'||row.favoritesnum=='numm'||!row.favoritesnum){
                        return '-';
                    }else {
                        return row.favoritesnum;
                    }
                },
            },
            {
                title: "粉丝数",//标题
                field: "fansnum",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    if (row.fansnum==''||row.fansnum=='unknown'||row.fansnum=='numm'||!row.fansnum){
                        return '-';
                    }else {
                        return row.fansnum;
                    }
                },
            },
            // {
            //     title: '操作',//标题
            //     field: "",//键名
            //     sortable: true,//是否可排序
            //     order: "desc",//默认排序方式
            //     align: "center",//水平
            //     valign: "middle",//垂直
            //     formatter: function (value, row, index) {
            //         return '<a style="cursor: pointer;" onclick="details()" title="查看详情"><i class="icon icon-edit"></i></a>';
            //     },
            // },
        ],
    });
}
function mainWeibo(_data,idx) {
    $('.mainWeiboTable'+idx).bootstrapTable('load', _data);
    $('.mainWeiboTable'+idx).bootstrapTable({
        data:_data,
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
                field: "uid",//键名
                sortable: true,//是否可排序
                order: "desc",//默认排序方式
                align: "center",//水平
                valign: "middle",//垂直
                formatter: function (value, row, index) {
                    var text,text2,time,img,all='',name;
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
                    if (row.text==''||row.text=='null'||row.text=='unknown'||!row.text){
                        text='暂无内容';
                    }else {
                        if (row.sensitive_words_string||!isEmptyObject(row.sensitive_words_string)){
                            var keywords=row.sensitive_words_string.split('&');;
                            var s=row.text;
                            for (var f=0;f<keywords.length;f++){
                                s=s.toString().replace(new RegExp(keywords[f],'g'),'<b style="color:#ef3e3e;">'+keywords[f]+'</b>');
                            }
                            text=s;
                            var rrr=row.text;
                            if (rrr.length>=160){
                                rrr=rrr.substring(0,160)+'...';
                                all='inline-block';
                            }else {
                                rrr=row.text;
                                all='none';
                            }
                            for (var f of keywords){
                                rrr=rrr.toString().replace(new RegExp(f,'g'),'<b style="color:#ef3e3e;">'+f+'</b>');
                            }
                            text2=rrr;
                        }else {
                            text=row.text;
                            if (text.length>=160){
                                text2=text.substring(0,160)+'...';
                                all='inline-block';
                            }else {
                                text2=text;
                                all='none';
                            }
                        };
                    };
                    if (row.timestamp==''||row.timestamp=='null'||row.timestamp=='unknown'||!row.timestamp){
                        time='未知';
                    }else {
                        time=getLocalTime(row.timestamp);
                    };
                    var sye_1='',sye_2='';
                    if (Number(row.sensitive) < 50){
                        sye_1='border-color: transparent transparent #131313';
                        sye_2='color: yellow';
                    }
                    var rel_str=
                        '<div class="center_rel">'+
                        '   <div class="icons" style="'+sye_1+'">'+
                        '       <i class="icon icon-warning-sign weiboFlag" style="'+sye_2+'"></i>'+
                        '   </div>'+
                        '   <img src="'+img+'" alt="" class="center_icon">'+
                        '   <a class="center_1" onclick="jumpWeiboThis(this)" style="color:#f98077;">'+name+'</a>'+
                        '   <span class="cen3-1" style="color:#f6a38e;"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>'+
                        '   <a class="mid" style="display: none;">'+row.mid+'</a>'+
                        '   <a class="uid" style="display: none;">'+row.uid+'</a>'+
                        '   <a class="timestamp" style="display: none;">'+row.timestamp+'</a>'+
                        '   <button data-all="0" style="display:'+all+'" type="button" class="btn btn-primary btn-xs allWord" onclick="allWord(this)">查看全文</button>'+
                        '   <p class="allall1" style="display:none;">'+text+'</p>'+
                        '   <p class="allall2" style="display:none;">'+text2+'</p>'+
                        '   <span class="center_2">'+text2+'</span>'+
                        '   <div class="center_3">'+
                        '       <span class="cen3-1" onclick="retweet(this,\'预警\')"><i class="icon icon-share"></i>&nbsp;&nbsp;转发（<b class="forwarding">'+row.retweeted+'</b>）</span>'+
                        '       <span class="cen3-2" onclick="showInput(this)"><i class="icon icon-comments-alt"></i>&nbsp;&nbsp;评论（<b class="comment">'+row.comment+'</b>）</span>'+
                        '       <span class="cen3-3" onclick="thumbs(this)"><i class="icon icon-thumbs-up"></i>&nbsp;&nbsp;赞</span>'+
                        '       <span class="cen3-5" onclick="joinPolice(this)"><i class="icon icon-plus-sign"></i>&nbsp;&nbsp;加入预警库</span>'+
                        '       <span class="cen3-9" onclick="robot(this)"><i class="icon icon-github-alt"></i>&nbsp;&nbsp;机器人回复</span>'+
                        '       <span title="关注用户" onclick="focusUser(this)"><i class="icon icon-heart"></i>&nbsp;&nbsp;关注用户</span>'+
                        '    </div>'+
                        '    <div class="forwardingDown" style="width: 100%;display: none;">'+
                        '       <input type="text" class="forwardingIput" placeholder="转发内容"/>'+
                        '       <span class="sureFor" onclick="forwardingBtn()">转发</span>'+
                        '    </div>'+
                        '    <div class="commentDown" style="width: 100%;display: none;">'+
                        '        <input type="text" class="comtnt" placeholder="评论内容"/>'+
                        '        <span class="sureCom" onclick="comMent(this,\'预警\')">评论</span>'+
                        '    </div>'+
                        '</div>'
                    return rel_str;
                }
            },
        ],
    });
};
//操作返回结果
function postYES(data) {
    var f='';
    if (data[0]||data){
        f='操作成功';
    }else {
        f='操作失败';
    }
    $('#pormpt p').text(f);
    $('#pormpt').modal('show');
}
