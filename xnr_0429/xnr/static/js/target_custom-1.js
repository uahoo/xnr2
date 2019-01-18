//加载
var domainName='',roleName='';
//渗透领域
var WFT_url,firstStep,secondStep;
if ((flag==1)||(_gostart_USER.indexOf('W')==0)){
    WFT_url='/weibo_xnr_create';
    firstStep='WBfirstStep';
    secondStep='WBsecondStep';
}else if ((flag==4)||(_gostart_USER.indexOf('F')==0)){
    WFT_url='/facebook_xnr_create';
    firstStep='FBfirstStep';
    secondStep='FBsecondStep';
}else if ((flag==5)||(_gostart_USER.indexOf('T')==0)){
    WFT_url='/twitter_xnr_create';
    firstStep='TWfirstStep';
    secondStep='TWsecondStep';
}
var field_url=WFT_url+'/show_domain/?submitter='+admin;
public_ajax.call_request('get',field_url,field);
function field(data) {
    if(isEmptyObject(data)||(!data)){
        $('.nextButton').addClass('disableCss');
        $('#pormpt p').text('抱歉，您没有可以推荐的领域，请先去创建领域。');
        $('#pormpt').modal('show');
        return false;
    }else {
        var str='',plk=0;
        for (var k in data){
			if(plk==0){ 
				defalutDomain=data[k];
	        	var creatDEFAULT=WFT_url+'/domain2role/?domain_name='+data[k];
	            public_ajax.call_request('get',creatDEFAULT,creatrole)
			}
            str+=
                '<label class="demo-label" title="'+data[k]+'">'+
                '   <input class="demo-radio" type="radio" name="demo1" id="'+k+'" value="'+data[k]+'">'+
                '   <span class="demo-checkbox demo-radioInput"></span> '+data[k]+
                '</label>';
			plk++;
        }
        $('#container .tit-2 .field').html(str);
        $('input[name=demo1]').on('click',function () {
            domainName=$(this).parent().attr('title');
            var nameLEN=$(this).attr('name').toString();
            var creat_url=WFT_url+'/domain2role/?domain_name='+domainName;
            public_ajax.call_request('get',creat_url,creat_1)
        });
    }

}
function creatrole(data){
	if(data.length!=0){
		defalutRole=data[0];
	}else {
		$('#pormpt p').text('抱歉，该领域正在计算中，请稍后查看角色身份。');
        $('#pormpt').modal('show');
	}
}
var $one=JSON.parse(localStorage.getItem(firstStep));
if ($one){
    domainName=$one.domain_name;
    roleName=$one.role_name;
    inModalData($one);
}
var goUSER=JSON.parse(localStorage.getItem('goONuser'));
if (goUSER){
    inModalData(goUSER);
}
//模板导入
var modalAllData,$$political_side,$$psy_feature,$$daily_interests;
function inModalData(data) {
    modalAllData=data;
    var tt=data.domains||data.domain_name;
    domainName=tt;roleName=data.role_name||data.roleName;
    setTimeout(function () {
        $(".field input[type='radio'][value='"+tt+"']").attr("checked",true);
    },500);
    var creat_url=WFT_url+'/domain2role/?domain_name='+(data.domains||data.domain_name);
    //public_ajax.call_request('get',creat_url,creat_1);
    var creat_url_2=WFT_url+'/role2feature_info/?domain_name='+(data.domains||data.domain_name)+'&role_name='+(data.role_name||data.roleName);
    //public_ajax.call_request('get',creat_url_2,creat_2);
    setTimeout(function () {
        public_ajax.call_request('get',creat_url,creat_1);
        public_ajax.call_request('get',creat_url_2,creat_2);
    },1000);
    $$political_side=data.political_side;
    try {
        if(data.psy_feature.indexOf('&')>=0){
            $$psy_feature=data.psy_feature.split('&');
        }else {
            $$psy_feature=data.psy_feature.split(',');
        }
    }catch (e){
        $$psy_feature=[];
        $.each(data.psy_feature,function (index,item) {
            $$psy_feature.push(item[0]);
        })
    }
    /*if(data.psy_feature.indexOf('&')>=0){
        $$psy_feature=data.psy_feature.split('&');
    }else {
        $$psy_feature=data.psy_feature.split(',');
    }*/

	try{
		var bus=data.business_goal.toString().indexOf('&')==-1?data.business_goal.split(',|，'):data.business_goal.split('&');
	    for (var f of bus){
        	$(".build-4 input[name='demo66'][type='checkbox'][value='"+f+"']").attr("checked",true);
    	}
	}catch(e){
		$(".build-4 input[name='demo66'][type='checkbox'][value='"+data.business_goal+"']").attr("checked",true);
	}
	try{
		var day=data.daily_interests.toString().indexOf('&')==-1?data.daily_interests.split(',|，'):data.daily_interests.split('&');;
    	for (var f of day){
        	$(".build-5 input[name='demo6'][type='checkbox'][value='"+f+"']").attr("checked",true);
    	}
	}catch(e){
	    $(".build-5 input[name='demo6'][type='checkbox'][value='"+data.daily_interests+"']").attr("checked",true);
	}
    if (data.monitor_keywords){
        $('.build-6 .keywords').val(data.monitor_keywords.toString().replace(/&/g,'，'))
    }else {
        $('.build-6 .keywords').attr('placeholder','暂无关键词');
    }
    var active_time,day_post_num;
    if (data.active_time=='unknown'||data.active_time=='null'||data.active_time==''||!data.active_time){active_time='未知'}else{active_time=data.active_time};
    if (data.day_post_num=='unknown'||data.day_post_num=='null'||data.day_post_num==''||!data.day_post_num){day_post_num='未知'}else{day_post_num=data.day_post_num};

    //第二步
    /*if(!$one){
        var nickName,age,location,sex,career,description;

        if (data.nick_name=='unknown'||data.nick_name=='null'||data.nick_name==''||!data.nick_name){nickName='无昵称'}else{nickName=data.nick_name};
        if (data.age=='unknown'||data.age=='null'||data.age==''||!data.age){age=0}else{age=data.age};
        if (data.location=='unknown'||data.location=='null'||data.location==''||!data.location){location='未知'}else{location=data.location};
        if (data.gender==1){sex='男'}else if(data.gender==2){sex='女'}else{sex='未知'};
        if (data.career=='unknown'||data.career=='null'||data.career==''||!data.career){career='未知'}else{career=data.career};
        if (data.description=='unknown'||data.description=='null'||data.description==''||!data.description){description='无描述'}else{description=data.description};
        var second={
            'nick_name':nickName,
            'age':age,
            'location':location,
            'sex':sex,
            'career':career,
            'description':description,
            'active_time':active_time,
            'day_post_num':day_post_num,
        }
        localStorage.setItem(secondStep,JSON.stringify(second));
    }*/


}
//==========模板

function creat_1(data) {
    addLabel(data,'opt-1','demo2');
}
function creat_2(data) {
    addLabel(data,'opt-2&opt-3','demo3&demo4');
}
var m;
function addLabel(data,className,name) {
    m=Number(name.charAt(name.length-1));
    var _string;
    if (m>3){
        var c=className.split('&'),n=name.split('&'),f=0;
        for (var k = 0;k<2;k++){
            var ary=[];
            if (k==0){
                $.each(data['political_side'],function (index,item) {
                    if (item[0]=='mid'){item[0]='中立'}else if (item[0]=='left'){item[0]='左倾'}else
                    if (item[0]=='right'){item[0]='右倾'}
                    ary.push(item[0].toString());
                });
                _string=labelSTR(ary,n[k]);
            }else if (k==1){
                $.each(data['psy_feature'],function (index,item) {
                    ary.push(item[0].toString());
                });
                _string=labelSTR(ary,n[k],'checkbox');
            }
            $('#container .buildOption .'+c[k]).empty().html(_string);
            f++;
        };
    }else {
        _string=labelSTR(data,name);
        $('#container .buildOption .'+className).empty().html(_string);
        $('input[name='+name+']').on('click',function () {
            roleName=$(this).parent().attr('title');
            var creat_url_2=WFT_url+'/role2feature_info/?domain_name='+domainName+'&role_name='+roleName;
            public_ajax.call_request('get',creat_url_2,creat_2)
        });
    }
};
function labelSTR(data,name,radioCheckbox='radio') {
    var str='';
    if (data.length==0){
        if (name=='demo2'){
            str='暂无数据';
            return str;
        }else if (name=='demo3'){
            data=['左倾','中立','右倾'];
        }else if (name='demo4'){
            data=['中性','积极','悲伤','焦虑','生气','厌恶','消极其他'];
        }
    }
    for(var i=0;i<data.length;i++){
        var cc='';
        if (roleName==data[i]){cc='checked'};
        if ($$political_side==data[i]){cc='checked'};
        if ($$psy_feature){
            for (var f of $$psy_feature){
                if (f==data[i]){
                    cc='checked';
                }
            }
        };
        str+= '<label class="demo-label" title="'+data[i]+'">'+
            '   <input class="demo-radio" value="'+data[i]+'" type="'+radioCheckbox+'" name="'+name+'" '+cc+'>'+
            '   <span class="demo-checkbox demo-radioInput"></span> '+data[i]+
            '</label>';
    }

    return str;
}

//保存结果
//http://219.224.134.213:9090/weibo_xnr_create/save_step_one/?domain_name=维权群体&role_name=政府机构及人士
// &psy_feature=积极，中立，悲伤&political_side=中立&business_goal=扩大影响，渗透&monitor_keywords=维权，律师&daily_interests=旅游，美食
var daily='';
$('.nextButton').on('click',function () {
    domainName=$('.field input:radio[name="demo1"]:checked').val();
    var psyFeature=[],dailyInterests=[],politicalSide='',business=[];
    $(".opt-3 input[type=checkbox]:checkbox:checked").each(function (index,item) {
        psyFeature.push($(this).val());
    });
    $(".opt-2 input[type=radio]:radio:checked").each(function (index,item) {
        politicalSide=$(this).val().toString();
    });
    $(".opt-5 input[type=checkbox]:checkbox:checked").each(function (index,item) {
        dailyInterests.push($(this).val());
    });
    $(".opt-4 input[type=checkbox]:checkbox:checked").each(function (index,item) {
        business.push($(this).val());
    });
    var businessGoal= business.join(',');
    var monitorKeywords= $('.opt-6 .keywords').val().toString().replace(/，/g,',');
    if (domainName==''||roleName==''||psyFeature.length==0||dailyInterests.length==0||politicalSide==''||businessGoal==''||monitorKeywords==''){
        $('#prompt p').text('请检查您选择和添加的信息。（不能为空）');
        $('#prompt').modal('show');
    }else {
        daily=dailyInterests.join(',');
        var saveFirst_url=WFT_url+'/save_step_one/?domain_name='+domainName+'&role_name='+roleName+
        '&psy_feature='+psyFeature.join(',')+'&political_side='+politicalSide+'&business_goal='+businessGoal+
        '&monitor_keywords='+monitorKeywords+'&daily_interests='+daily;
        // window.open('/registered/virtualCreated/?domainName='+domainName+'&roleName='+roleName+'&daily='+daily+
        // '&psyFeature='+psyFeature.join(',')+'&politicalSide='+politicalSide+'&businessGoal='+businessGoal+
        // '&monitorKeywords='+monitorKeywords);
        var first={
            'domain_name':domainName,
            'role_name':roleName,
            'daily_interests':daily,
            'psy_feature':psyFeature.join(','),
            'political_side':politicalSide,
            'business_goal':businessGoal,
            'monitor_keywords':monitorKeywords,
        };
        localStorage.setItem(firstStep,JSON.stringify(first));
        //public_ajax.call_request('get',saveFirst_url,in_second);
        window.open('/registered/virtualCreated/?flag='+flag);
    }
});
function in_second(data) {
    if (data){
        window.open('/registered/virtualCreated/?flag='+flag);
    }else {
        $('#prompt p').text('您输入的内容有误，请刷新页面重新输入。');
        $('#prompt').modal('show');
    }
}
