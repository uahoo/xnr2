var time2=Date.parse(new Date())/1000;
var timeUrl='/weibo_xnr_warming_new/show_date_warming/?account_name='+ID_Num+'&start_time='+todayTimetamp()+'&end_time='+time2;
public_ajax.call_request('get',timeUrl,calendar);
//
$('.choosetime .demo-label input').on('click',function () {
    var _val = $(this).val();
    var valCH=$('#typelist input:radio[name="focus"]:checked').val();
    if (_val == 'mize') {
        $(this).parents('.choosetime').find('#start').show();
        $(this).parents('.choosetime').find('#end').show();
        $(this).parents('.choosetime').find('#sure').css({display: 'inline-block'});
    } else {
        $('#group_emotion_loading').css('display', 'block');
        $(this).parents('.choosetime').find('#start').hide();
        $(this).parents('.choosetime').find('#end').hide();
        $(this).parents('.choosetime').find('#sure').hide();
        var timeUrl='/weibo_xnr_warming_new/show_date_warming/?account_name='+ID_Num+
            '&start_time='+getDaysBefore(_val)+'&end_time='+time2;
        public_ajax.call_request('get',timeUrl,calendar);
    }
});
$('#sure').on('click',function () {
    var s=$(this).parents('.choosetime').find('#start').val();
    var d=$(this).parents('.choosetime').find('#end').val();
    if (s==''||d==''){
        $('#pormpt p').text('时间不能为空。');
        $('#pormpt').modal('show');
    }else {
        $('#group_emotion_loading').css('display', 'block');
        var weiboUrl='/weibo_xnr_warming_new/show_date_warning/?account_name='+admin+'&start_time='+
            (Date.parse(new Date(s))/1000)+'&end_time='+(Date.parse(new Date(d))/1000);
        public_ajax.call_request('get',weiboUrl,calendar);
    }
});


var contentList = {};
function calendar(data){
    $.each(data,function (index,item) {
        contentList['exo_'+index]=item['weibo_date_warming_content'];
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
                var name,txt='',agoDay,time,time_2,keywords;
                if (dataArray[i].date_name==''||dataArray[i].date_name=='null'||dataArray[i].date_name=='unknown'||!dataArray[i].date_name){
                    name='未命名';
                }else {
                    name=dataArray[i].date_name;
                };
                if (dataArray[i].keywords==''||dataArray[i].keywords=='null'||dataArray[i].keywords=='unknown'||!dataArray[i].keywords){
                    keywords = '暂无描述';
                }else {
                    keywords = dataArray[i].keywords.join('，');
                };
                if (dataArray[i].create_time==''||dataArray[i].create_time=='null'||dataArray[i].create_time=='unknown'||!dataArray[i].create_time){
                    time='未知';
                }else {
                    time=getLocalTime(dataArray[i].create_time);
                };
                if (dataArray[i].date_time==''||dataArray[i].date_time=='null'||dataArray[i].date_time=='unknown'||!dataArray[i].date_time){
                    time_2='未知';
                }else {
                    time_2=dataArray[i].date_time;
                };
                if (dataArray[i].countdown_days==''||dataArray[i].countdown_days=='null'||dataArray[i].countdown_days=='unknown'||!dataArray[i].countdown_days){
                    agoDay = '暂无统计';
                }else {
                    if (dataArray[i].countdown_days.toString().indexOf('-')==-1){
                        agoDay = '距离下一次该日期还有 '+dataArray[i].countdown_days+' 天';
                    }else {
                        agoDay = dataArray[i].countdown_days.toString().replace(/-/g,'距离今天已经过去 ')+' 天';
                    }
                };
                html_c =
                    '<div class="post_perfect">'+
                    '   <div class="post_center-hot">'+
                    '       <img src="/static/images/post-6.png" alt="" class="center_icon">'+
                    '       <div class="">'+
                    '           <a class="center_1" href="###" style="color: #f98077;">'+name+'</a>&nbsp;'+
                    '           <a class="_id" style="display: none;">'+dataArray[i]._id+'</a>'+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="日期"><i class="icon icon-lightbulb"></i>&nbsp;&nbsp;时间节点：'+time_2+'</span> &nbsp;&nbsp;'+
                    // '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="创建日期"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>  '+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="距离今天过去多久"><i class="icon icon-bullhorn"></i>&nbsp;&nbsp;'+agoDay+'</span>  &nbsp;&nbsp;'+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="关键词"><i class="icon icon-bell-alt"></i>&nbsp;&nbsp;'+keywords+'</span>  '+
                    '           <div class="center_2 DsAuto'+i+'"></div>'+//<span style="color:#f98077;">敏感微博内容：</span>
                    '       </div>'+
                    '    </div>'+
                    '</div>';
                oTBody.rows[i].insertCell(0);
                oTBody.rows[i].cells[0].innerHTML = html_c;
                startTable(i,keywords);
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
                    var name,txt='',agoDay,time,time_2,keywords;
                    if (dataArray[i].date_name==''||dataArray[i].date_name=='null'||dataArray[i].date_name=='unknown'||!dataArray[i].date_name){
                        name='未命名';
                    }else {
                        name=dataArray[i].date_name;
                    };
                    if (dataArray[i].keywords==''||dataArray[i].keywords=='null'||dataArray[i].keywords=='unknown'||!dataArray[i].keywords){
                        keywords = '暂无描述';
                    }else {
                        keywords = dataArray[i].keywords.join('，');
                    };
                    if (dataArray[i].create_time==''||dataArray[i].create_time=='null'||dataArray[i].create_time=='unknown'||!dataArray[i].create_time){
                        time='未知';
                    }else {
                        time=getLocalTime(dataArray[i].create_time);
                    };
                    if (dataArray[i].date_time==''||dataArray[i].date_time=='null'||dataArray[i].date_time=='unknown'||!dataArray[i].date_time){
                        time_2='未知';
                    }else {
                        time_2=dataArray[i].date_time;
                    };
                    if (dataArray[i].countdown_days==''||dataArray[i].countdown_days=='null'||dataArray[i].countdown_days=='unknown'||!dataArray[i].countdown_days){
                        agoDay = '暂无统计';
                    }else {
                        if (dataArray[i].countdown_days.toString().indexOf('-')==-1){
                            agoDay = '距离下一次该日期还有 '+dataArray[i].countdown_days+' 天';
                        }else {
                            agoDay = dataArray[i].countdown_days.toString().replace(/-/g,'距离今天已经过去 ')+' 天';
                        }
                    };
                    html_c =
                        '<div class="post_perfect">'+
                        '   <div class="post_center-hot">'+
                        '       <img src="/static/images/post-6.png" alt="" class="center_icon">'+
                        '       <div class="">'+
                        '           <a class="center_1" href="###" style="color: #f98077;">'+name+'</a>&nbsp;'+
                        '           <a class="_id" style="display: none;">'+dataArray[i]._id+'</a>'+
                        '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="日期"><i class="icon icon-lightbulb"></i>&nbsp;&nbsp;时间节点：'+time_2+'</span> &nbsp;&nbsp;'+
                        // '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="创建日期"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>  '+
                        '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="距离今天过去多久"><i class="icon icon-bullhorn"></i>&nbsp;&nbsp;'+agoDay+'</span>  &nbsp;&nbsp;'+
                        '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="关键词"><i class="icon icon-bell-alt"></i>&nbsp;&nbsp;'+keywords+'</span>  '+
                        '           <div class="center_2 DsAuto'+i+'"></div>'+//<span style="color:#f98077;">敏感微博内容：</span>
                        '       </div>'+
                        '    </div>'+
                        '</div>';
                    oTBody.rows[i].insertCell(0);
                    oTBody.rows[i].cells[0].innerHTML = html_c;
                    startTable(i,keywords);
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
                var name,txt='',agoDay,time,time_2,keywords;
                if (dataArray[i+a].date_name==''||dataArray[i+a].date_name=='null'||dataArray[i+a].date_name=='unknown'||!dataArray[i+a].date_name){
                    name='未命名';
                }else {
                    name=dataArray[i+a].date_name;
                };
                if (dataArray[i+a].keywords==''||dataArray[i+a].keywords=='null'||dataArray[i+a].keywords=='unknown'||!dataArray[i+a].keywords){
                    keywords = '暂无描述';
                }else {
                    keywords = dataArray[i+a].keywords.join('，');
                };
                if (dataArray[i+a].create_time==''||dataArray[i+a].create_time=='null'||dataArray[i+a].create_time=='unknown'||!dataArray[i+a].create_time){
                    time='未知';
                }else {
                    time=getLocalTime(dataArray[i+a].create_time);
                };
                if (dataArray[i+a].date_time==''||dataArray[i+a].date_time=='null'||dataArray[i+a].date_time=='unknown'||!dataArray[i+a].date_time){
                    time_2='未知';
                }else {
                    time_2=dataArray[i+a].date_time;
                };
                if (dataArray[i+a].countdown_days==''||dataArray[i+a].countdown_days=='null'||dataArray[i+a].countdown_days=='unknown'||!dataArray[i+a].countdown_days){
                    agoDay = '暂无统计';
                }else {
                    if (dataArray[i+a].countdown_days.toString().indexOf('-')==-1){
                        agoDay = '距离下一次该日期还有 '+dataArray[i+a].countdown_days+' 天';
                    }else {
                        agoDay = dataArray[i+a].countdown_days.toString().replace(/-/g,'距离今天已经过去 ')+' 天';
                    }
                };
                html_c =
                    '<div class="post_perfect">'+
                    '   <div class="post_center-hot">'+
                    '       <img src="/static/images/post-6.png" alt="" class="center_icon">'+
                    '       <div class="">'+
                    '           <a class="center_1" href="###" style="color: #f98077;">'+name+'</a>&nbsp;'+
                    '           <a class="_id" style="display: none;">'+dataArray[i+a]._id+'</a>'+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="日期"><i class="icon icon-lightbulb"></i>&nbsp;&nbsp;时间节点：'+time_2+'</span> &nbsp;&nbsp;'+
                    // '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="创建日期"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>  '+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="距离今天过去多久"><i class="icon icon-bullhorn"></i>&nbsp;&nbsp;'+agoDay+'</span>  &nbsp;&nbsp;'+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="关键词"><i class="icon icon-bell-alt"></i>&nbsp;&nbsp;'+keywords+'</span>  '+
                    '           <div class="center_2 DsAuto'+(a+i)+'"></div>'+//<span style="color:#f98077;">敏感微博内容：</span>
                    '       </div>'+
                    '    </div>'+
                    '</div>';
                oTBody.rows[i].cells[0].innerHTML = html_c;
                //数组从第i+a开始取值
                startTable(a+i,keywords);
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
                var name,txt='',agoDay,time,time_2,keywords;
                if (dataArray[i+a].date_name==''||dataArray[i+a].date_name=='null'||dataArray[i+a].date_name=='unknown'||!dataArray[i+a].date_name){
                    name='未命名';
                }else {
                    name=dataArray[i+a].date_name;
                };
                if (dataArray[i+a].keywords==''||dataArray[i+a].keywords=='null'||dataArray[i+a].keywords=='unknown'||!dataArray[i+a].keywords){
                    keywords = '暂无描述';
                }else {
                    keywords = dataArray[i+a].keywords.join('，');
                };
                if (dataArray[i+a].create_time==''||dataArray[i+a].create_time=='null'||dataArray[i+a].create_time=='unknown'||!dataArray[i+a].create_time){
                    time='未知';
                }else {
                    time=getLocalTime(dataArray[i+a].create_time);
                };
                if (dataArray[i+a].date_time==''||dataArray[i+a].date_time=='null'||dataArray[i+a].date_time=='unknown'||!dataArray[i+a].date_time){
                    time_2='未知';
                }else {
                    time_2=dataArray[i+a].date_time;
                };
                if (dataArray[i+a].countdown_days==''||dataArray[i+a].countdown_days=='null'||dataArray[i+a].countdown_days=='unknown'||!dataArray[i+a].countdown_days){
                    agoDay = '暂无统计';
                }else {
                    if (dataArray[i+a].countdown_days.toString().indexOf('-')==-1){
                        agoDay = '距离下一次该日期还有 '+dataArray[i+a].countdown_days+' 天';
                    }else {
                        agoDay = dataArray[i+a].countdown_days.toString().replace(/-/g,'距离今天已经过去 ')+' 天';
                    }
                };
                html_c =
                    '<div class="post_perfect">'+
                    '   <div class="post_center-hot">'+
                    '       <img src="/static/images/post-6.png" alt="" class="center_icon">'+
                    '       <div class="">'+
                    '           <a class="center_1" href="###" style="color: #f98077;">'+name+'</a>&nbsp;'+
                    '           <a class="_id" style="display: none;">'+dataArray[i+a]._id+'</a>'+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="日期"><i class="icon icon-lightbulb"></i>&nbsp;&nbsp;时间节点：'+time_2+'</span> &nbsp;&nbsp;'+
                    // '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="创建日期"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>  '+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="距离今天过去多久"><i class="icon icon-bullhorn"></i>&nbsp;&nbsp;'+agoDay+'</span>  &nbsp;&nbsp;'+
                    '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="关键词"><i class="icon icon-bell-alt"></i>&nbsp;&nbsp;'+keywords+'</span>  '+
                    '           <div class="center_2 DsAuto'+(i+a)+'"></div>'+//<span style="color:#f98077;">敏感微博内容：</span>
                    '       </div>'+
                    '    </div>'+
                    '</div>';
                oTBody.rows[i].cells[0].innerHTML = html_c;
                startTable(a+i,keywords);
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
            var name,txt='',agoDay,time,time_2,keywords;
            if (dataArray[i+a].date_name==''||dataArray[i+a].date_name=='null'||dataArray[i+a].date_name=='unknown'||!dataArray[i+a].date_name){
                name='未命名';
            }else {
                name=dataArray[i+a].date_name;
            };
            if (dataArray[i+a].keywords==''||dataArray[i+a].keywords=='null'||dataArray[i+a].keywords=='unknown'||!dataArray[i+a].keywords){
                keywords = '暂无描述';
            }else {
                keywords = dataArray[i+a].keywords.join('，');
            };
            if (dataArray[i+a].create_time==''||dataArray[i+a].create_time=='null'||dataArray[i+a].create_time=='unknown'||!dataArray[i+a].create_time){
                time='未知';
            }else {
                time=getLocalTime(dataArray[i+a].create_time);
            };
            if (dataArray[i+a].date_time==''||dataArray[i+a].date_time=='null'||dataArray[i+a].date_time=='unknown'||!dataArray[i+a].date_time){
                time_2='未知';
            }else {
                time_2=dataArray[i+a].date_time;
            };
            if (dataArray[i+a].countdown_days==''||dataArray[i+a].countdown_days=='null'||dataArray[i+a].countdown_days=='unknown'||!dataArray[i+a].countdown_days){
                agoDay = '暂无统计';
            }else {
                if (dataArray[i+a].countdown_days.toString().indexOf('-')==-1){
                    agoDay = '距离下一次该日期还有 '+dataArray[i+a].countdown_days+' 天';
                }else {
                    agoDay = dataArray[i+a].countdown_days.toString().replace(/-/g,'距离今天已经过去 ')+' 天';
                }
            };
            html_c =
                '<div class="post_perfect">'+
                '   <div class="post_center-hot">'+
                '       <img src="/static/images/post-6.png" alt="" class="center_icon">'+
                '       <div class="">'+
                '           <a class="center_1" href="###" style="color: #f98077;">'+name+'</a>&nbsp;'+
                '           <a class="_id" style="display: none;">'+dataArray[i+a]._id+'</a>'+
                '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="日期"><i class="icon icon-lightbulb"></i>&nbsp;&nbsp;时间节点：'+time_2+'</span> &nbsp;&nbsp;'+
                // '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="创建日期"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>  '+
                '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="距离今天过去多久"><i class="icon icon-bullhorn"></i>&nbsp;&nbsp;'+agoDay+'</span>  &nbsp;&nbsp;'+
                '           <span class="time" style="font-weight: 900;color:blanchedalmond;" title="关键词"><i class="icon icon-bell-alt"></i>&nbsp;&nbsp;'+keywords+'</span>  '+
                '           <div class="center_2 DsAuto'+(a+i)+'"></div>'+//<span style="color:#f98077;">敏感微博内容：</span>
                '       </div>'+
                '    </div>'+
                '</div>';
            oTBody.rows[i].cells[0].innerHTML = html_c;
            startTable(a,keywords);
        }
    }

    $('#group_emotion_loading').css('display', 'none');

}

function startTable(index,key) {
    weibo(index,contentList['exo_'+index],key);
}
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

function weibo(idx,data,words) {
    $('.DsAuto'+idx).bootstrapTable('load', data);
    $('.DsAuto'+idx).bootstrapTable({
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
                    var item=row;
                    var str_new='';
                    var text,text2,all='',img,time,name='';
                    if (item.nick_name==''||item.nick_name=='null'||item.nick_name=='unknown'||!item.nick_name){
                        name=item.uid;
                    }else {
                        name=item.nick_name;
                    };
                    if (item.photo_url==''||item.photo_url=='null'||item.photo_url=='unknown'||!item.photo_url){
                        img='/static/images/unknown.png';
                    }else {
                        img=item.photo_url;
                    };
                    if (item.timestamp==''||item.timestamp=='null'||item.timestamp=='unknown'){
                        time='未知';
                    }else {
                        time=getLocalTime(item.timestamp);
                    };
                    if (item.text==''||item.text=='null'||item.text=='unknown'||!item.text){
                        text='暂无内容';
                    }else {
                        if (item.sensitive_words_string||!isEmptyObject(item.sensitive_words_string)){
                            var s=item.text;
                            var keywords=item.sensitive_words_string.split('&');
                            for (var f=0;f<keywords.length;f++){
                                s=s.toString().replace(new RegExp(keywords[f],'g'),'<b style="color:#ef3e3e;">'+keywords[f]+'</b>');
                            }
                            text=s;

                            var rrr=item.text;
                            if (rrr.length>=160){
                                rrr=rrr.substring(0,160)+'...';
                                all='inline-block';
                            }else {
                                rrr=item.text;
                                all='none';
                            }
                            for (var f of keywords){
                                rrr=rrr.toString().replace(new RegExp(f,'g'),'<b style="color:#ef3e3e;">'+f+'</b>');
                            }
                            text2=rrr;
                        }else {
                            text=item.text;
                            if (text.length>=160){
                                text2=text.substring(0,160)+'...';
                                all='inline-block';
                            }else {
                                text2=text;
                                all='none';
                            }
                        };
                    };
                    str_new+=
                        '<div class="everySpeak everyUser">'+
                        '        <div class="speak_center">'+
                        // '            <img src="'+img+'" alt="" class="center_icon">'+
                        '            <div class="center_rel center_rel_weibo" style="text-align: left;">'+
                        '                <img src="'+img+'" alt="" class="center_icon">'+
                        '                <a class="center_1" onclick="jumpWeiboThis(this)" style="color: #f98077;">'+name+'</a>'+
                        '                <a class="mid" style="display: none;">'+item.mid+'</a>'+
                        '                <a class="uid" style="display: none;">'+item.uid+'</a>'+
                        '                <a class="timestamp" style="display: none;">'+item.timestamp+'</a>'+
                        '                <span class="time" style="font-weight: 900;color:#f6a38e;"><i class="icon icon-time"></i>&nbsp;&nbsp;'+time+'</span>  '+
                        '                <button data-all="0" style="display:'+all+'" type="button" class="btn btn-primary btn-xs allWord" onclick="allWord(this)">查看全文</button>'+
                        '                <p class="allall1" style="display:none;">'+text+'</p>'+
                        '                <p class="allall2" style="display:none;">'+text2+'</p>'+
                        '                <span class="center_2">'+text2+'</span>'+
                        '                <div class="center_3">'+
                        '                    <span class="cen3-1" onclick="retweet(this,\'预警\')"><i class="icon icon-share"></i>&nbsp;&nbsp;转发（<b class="forwarding">'+item.retweeted+'</b>）</span>'+
                        '                    <span class="cen3-2" onclick="showInput(this)"><i class="icon icon-comments-alt"></i>&nbsp;&nbsp;评论（<b class="comment">'+item.comment+'</b>）</span>'+
						'                    <span class="cen3-2" onclick="commentList(this)"><i class="icon icon-list"></i>&nbsp;&nbsp;查看评论</span>'+
                        '                    <span class="cen3-3" onclick="thumbs(this)"><i class="icon icon-thumbs-up"></i>&nbsp;&nbsp;赞</span>'+
                        '                    <span class="cen3-5" onclick="joinPolice(this,\'时间\')"><i class="icon icon-plus-sign"></i>&nbsp;&nbsp;加入预警库</span>'+
                        '                    <span class="cen3-9" onclick="robot(this)"><i class="icon icon-github-alt"></i>&nbsp;&nbsp;机器人回复</span>'+
                        '                    <span class="cen3-6" onclick="oneUP(this,\'时间\')"><i class="icon icon-upload-alt"></i>&nbsp;&nbsp;上报</span>'+
						'                    <span title="关注用户" onclick="focusUser(this)"><i class="icon icon-heart"></i>&nbsp;&nbsp;关注用户</span>'+
                        '                </div>'+
                        '                <div class="forwardingDown" style="width: 100%;display: none;">'+
                        '                   <input type="text" class="forwardingIput" placeholder="转发内容"/>'+
                        '                   <span class="sureFor" onclick="forwardingBtn()">转发</span>'+
                        '                </div>'+
                        '                <div class="commentDown" style="width: 100%;display: none;">'+
                        '                    <input type="text" class="comtnt" placeholder="评论内容"/>'+
                        '                    <span class="sureCom" onclick="comMent(this,\'预警\')">评论</span>'+
                        '                </div>'+
                        '            </div>'+
                        '        </div>';
                    return str_new;
                }
            },
        ],
    });
}
