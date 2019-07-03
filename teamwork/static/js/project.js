var currentProject;
var plans = [];
var activeTab = 0;
var chartTab=0;

//在story下面某一计划子项下面添加一子项
function addLineNext(target) {
  var li = $(target).parents('.task-item');
  li.after('<li class="list-group-item task-item" style="padding:0"><div style="height:50px;"><div class="form-group task-line"><div class="task-before">☞</div><div style="flex:1"><input class="form-control plan-content" placeholder="please input plan"/></div><div class="duration-container"><input class="form-control duration" placeholder="duration" type="number"></div><div class="task-after"><span style="padding-left:4px;font-size: 2.2rem;">h</span><span  title="switch task status" class="task-status"><i class="iconfont icon-weiwancheng"   onclick="toggleStatus(this,0)" data-status="0"></i></span><span  title="add task next"><i class="iconfont icon-Add"  onclick="addLineNext(this)"></i></span><span title="remove task"><i class="iconfont icon-jian  text-danger" onclick="removeLine(this)" ></i></span></div></div></div></li>')
}

//移除story下面某一计划子项
function removeLine(target) {
  var ul = $(target).parents('.task-list');
  if (ul.children().length > 1) {
    $(target).parents('.task-item').remove();
  } else {

  }

}

//打开计划编辑页面时，加载之前保存在服务器的计划数据
function loadProjectPlan(id) {
  currentProject = id;
  plans = [];
  activeTab = 0;
  $.ajax({
    url: '/project/' + currentProject + '/plan/ajax/load',
    success: function (res) {
      if (res.plans) {
        plans = res.plans;
        var tag = true;
        for (var i in plans) {
          if (!plans[i].period) {
            tag = false;
            break;
          }else{
            plans[i].disablePeriod=true;
          }
        }
        if (!tag) {
          plans = [];
        }
        //加载数据成功，渲染计划表单
        renderPlanList(true)
      } else {

      }

    },
    fail: function () {

    }

  })
}

/**
 * when user click "add story" button to add a story
 * @param target
 */
function addStory(target) {

  var li = $(target).parents(".story-item");
  li.after(' <li class="story-item"><div class="story-container"><div style="height: 50px;line-height: 50px;padding:4px 0"><div class="col-sm-9"><input class="form-control story-title" placeholder="Please input your user story"></div><div class="col-sm-1 story-icon"><i class="iconfont icon-down-circle-o" onclick="toggleShow(this)" title="show tasks"></i></div><div class="col-sm-1  story-icon"><i class="iconfont icon-Add"  onclick="addStory(this)" title="add story"></i></div><div class="col-sm-1  story-icon"><i class="iconfont icon-jian"  onclick="deleteStory(this)"  title="delete story"></i></div></div><div class="task-container"><ul class="list-group task-list"><li class="list-group-item task-item" style="padding:0" data-finish=""><div style="height:50px;"><div class="form-group task-line"><div class="task-before">☞</div><div style="flex:1"><input class="form-control plan-content" placeholder="please input task"/></div><div class="duration-container"><input class="form-control duration" placeholder="duration" type="number"></div><div class="task-after"><span style="padding-left:4px;font-size: 2.2rem;">h</span><span  title="switch task status"  class="task-status"><i class="iconfont icon-weiwancheng"   onclick="toggleStatus(this,0)" data-status="0"></i></span><span  title="add task next"><i class="iconfont icon-Add"  onclick="addLineNext(this)"></i></span><span title="remove task"><i class="iconfont icon-jian  text-danger" onclick="removeLine(this)" ></i></span></div></div></div></li></ul></div></div></li>')
}

//删除story
function deleteStory(target) {
  var ul = $(target).parents('#stories');
  if (ul.children().length > 1) {
    $(target).parents('.story-item').remove();
  } else {

  }
}

//切换计划的状态（未完成、进行中、已完成）
function toggleStatus(target, status, finish) {
  if(plans[activeTab].period.length>0){
    var ps=plans[activeTab].period.split("-");
    var startDate=Date.parse(ps[0]);
    var endDate=Date.parse(ps[0])+24*3600000;
    var now=(new Date()).getTime();
    if(now<startDate||now>=endDate){
      alert("Now is out of period,can't update status");
      return ;
    }
  }
  if (status == 0) {
    $(target)[0].className = "iconfont  icon-jinhangzhong text-warning";
    $(target).attr("onclick", "toggleStatus(this,1)");
    $(target).attr("data-status", "1")
  } else if (status == 1) {

    $(target)[0].className = "iconfont  icon-wancheng text-info";
    $(target).attr("onclick", "toggleStatus(this,2)");
    $(target).attr("data-status", "2")
  } else if (status == 2) {
    if (!finish) {
      $(target)[0].className = "iconfont icon-weiwancheng text-danger";
      $(target).attr("onclick", "toggleStatus(this,0)");
      $(target).attr("data-status", "0")
    }
  }
}

//保存全部计划至服务器
function savePlans() {
  var volid = collectePlansData();
  if (!volid) {
    alert("Please input all fileds");
    return;
  }
  var data = {
    plans: JSON.stringify(plans)
  }
  $.ajax({
    method: 'POST',
    data: data,
    url: '/project/' + currentProject + '/plan/ajax/save_plan',
    success: function (res) {
       if(res.code==0){
         plans=res.data;
         for(var i in plans){
           plans[i].disablePeriod=true;
         }
         renderPlanList(true);
         alert("save success");
       }
    }
  })
}

//渲染计划表单数据
function renderPlanList(renderContent) {
  var plan = {
    stories: []
  };
  if (plans.length == 0) {

    var story = {
      title: "",
      tasks: [{
        title: "",
        duration: 1,
        status: 0
      }]
    }
    plan.period = ""
    plan.stories.push(story);
    plans.push(plan)
  } else {
    plan = plans[activeTab];
  }
  var tabhtml = "";
  var contentHtml = "";
  for (var i in plans) {
    tabhtml += '<div class="tab-item ' + (i == activeTab ? "active" : "") + '"><span onclick="switchPlanTab(this,' + i + ')">Sprint plan ' + (parseInt(i) + 1) + '</span><a style="margin-left:20px;font-size:2rem;" onclick="removePlanTab(this,' + i + ')"><i class="fa fa-remove "></i></a></div>'
  }
  $(".tab-list").html(tabhtml);
  if (renderContent) {
    if(plan.disablePeriod){
     $("#plandate").attr("disabled","")
    }else{
      $("#plandate").removeAttr("disabled");
      var minDate;
      if(plans.length>1){
        var lastPlan=plans[plans.length-2];
        minDate=new Date(Date.parse(lastPlan.period.split("-")[1])+24*3600000);
      }else{
        minDate=new Date();
      }
      $("#plandate").daterangepicker({
        minDate:minDate
      });
    }

    $("#plandate").val(plan.period);
    var stories = plan.stories;
    for (var j in stories) {
      var story = stories[j];

      contentHtml += '<li class="story-item"><div class="story-container"><div style="height: 50px;line-height: 50px;padding:4px 0"><div class="col-sm-9">';
      contentHtml += '<input class="form-control story-title" placeholder="Please input your user story" value="' + story.title + '"></div>';
      contentHtml += '<div class="col-sm-1 story-icon"><i class="iconfont icon-down-circle-o" onclick="toggleShow(this)" title="show tasks"></i></div><div class="col-sm-1  story-icon"><i class="iconfont icon-Add" onclick="addStory(this)" title="add story"></i></div><div class="col-sm-1  story-icon"><i class="iconfont icon-jian" onclick="deleteStory(this)" title="delete story"></i></div></div><div class="task-container"><ul class="list-group task-list">';
      var tasks = story.tasks;
      for (var m in tasks) {
        var iconstr = "";
        switch (tasks[m].status) {
          case 0:
            iconstr = 'icon-weiwancheng text-danger';
            break;
          case 1:
            iconstr = 'icon-jinhangzhong text-warning';
            break;
          case 2:
            iconstr = 'icon-wancheng text-info';
            break;
        }
        contentHtml += '<li class="list-group-item task-item" style="padding:0"  data-finish="'+(tasks[m].finish_time?tasks[m].finish_time:"")+'"><div style="height:50px;"><div class="form-group task-line"><div class="task-before">☞</div><div style="flex:1"><input class="form-control plan-content" placeholder="please input your task" value="' + tasks[m].title + '"/></div><div class="duration-container"><input class="form-control duration" placeholder="duration" type="number" value="' + tasks[m].duration + '"></div><div class="task-after"><span style="padding-left:4px;font-size: 2.2rem;">h</span><span title="switch task status" finish_time class="task-status"><i class="iconfont ' + iconstr + '" onclick="toggleStatus(this,' + tasks[m].status + ',' + ((tasks[m].finish_time!=undefined&&tasks[m].finish_time!="")?"true" : "false") + ')" data-status="'+tasks[m].status+'"></i></span><span title="add task next"><i class="iconfont icon-Add" onclick="addLineNext(this)"></i></span><span title="remove task"><i class="iconfont icon-jian  text-danger" onclick="removeLine(this)"></i></span></div></div></div></li>';
      }
      contentHtml += '</ul></div></div></li>';
    }

    $("#stories").html(contentHtml);
  }

}

//获取计划表中数据。若有输入框未填写则返回false，否则返回true。更新选中plan对应计划数据对象
function collectePlansData() {

  var currentPlan = {};
  var period=$("#plandate").val();
  if (period.length == 0) {
    return false;
  }
  currentPlan.period=period;
  var stories = [];
  var tag = true;
  $(".story-item").each(function (k) {
    var title = $(this).find(".story-title").val();
    if (title.length == 0) {
      tag = false;
      return false;
    }
    var story = {
      title: title,
      tasks: []
    }

    $(this).find(".task-list .task-item").each(function (l) {
      var task={};
      var taskTitle=$(this).find(".plan-content").val();
      var taskDuration=$(this).find(".duration").val();
      var finish=$(this).attr("data-finish");
      if (taskTitle.length == 0) {
        tag = false;
        return ;
      }
      if (taskDuration.length == 0) {
        tag = false;
        return ;
      }
      var status=parseInt($(this).find(".task-status i").attr("data-status"));
      task.title=taskTitle;
      task.duration=taskDuration;
      task.status=status;
      task.finish_time=finish;
      story.tasks.push(task);
    })

    stories.push(story);

  })
  if (!tag) {
    return false;
  }
  currentPlan.stories=stories;
  currentPlan.disablePeriod= true;
  plans[activeTab] = currentPlan;
  return true;
}

//切换点击的story显示/隐藏计划明细
function toggleShow(target) {
  if ($(target)[0].className == "iconfont icon-down-circle-o") {
    $(target).attr("title", "")
    $(target)[0].className = "iconfont icon-up-circle-o";
    $(target).parent().parent().parent().find(".task-container").show()

  } else {
    $(target)[0].className = "iconfont icon-down-circle-o";
    $(target).parent().parent().parent().find(".task-container").hide()
  }

}

//点击+，添加计划
function addSprintPlan() {
  //save current  data
  var volid = collectePlansData();
  if (!volid) {
    alert("Please input all fileds");
    return;
  }
  $(".tab-list .active").removeClass('active');
  var plan = {
    stories: []
  };
  var story = {
    title: "",
    tasks: [{
      title: "",
      duration: 1,
      status: 0
    }]
  }
  plan.period = ""
  plan.stories.push(story);
  if (plans == null) {
    plans = [];
  }
  plans.push(plan);
  activeTab = plans.length - 1;
  renderPlanList(true)
}

//点击X,删除计划
function removePlanTab(target, index) {
  if (plans.length > 1) {
    //remove plan in plans array
    plans = plans.filter(function (item, i) {
      return i != index;
    })
    //remove the tab
    $(target).parent().remove();
    if (index == activeTab) {
      //The actived tab is removed
      if (activeTab == 0) {
        //The actived tab is the first,acitve first tab after removed
        activeTab = 0;
      } else {
        //The actived tab is not the first,acitve before one
        activeTab = index - 1;
      }
      renderPlanList(true)
    } else {
      activeTab = activeTab - 1;
      renderPlanList(false);
      var minDate;
      if(plans.length>1){
        var lastPlan=plans[plans.length-2];
        minDate=new Date(Date.parse(lastPlan.period.split("-")[1])+24*3600000);
      }else{
        minDate=new Date();
      }

      $("#plandate").daterangepicker({
        minDate:minDate
      });
    }
  }
}

//切换被激活显示的计划
function switchPlanTab(target, index) {
  var volid = collectePlansData();
  if (!volid) {
    alert("Please input all fileds");
    return;
  }
  activeTab = index;
  renderPlanList(true)
}

//从服务器加载计划数据
function loadChartData(id){
  $.ajax({
    url: '/project/' + id + '/plan/ajax/load',
    success: function (res) {
      if (res.plans) {
        plans = res.plans;
        if(plans.length==0){
          alert("There is no data for rendering the chart.")
        }else{
          chartTab=0;
          //显示第一个计划图表
          loadChart()
        }
      }
    },
    fail: function () {

    }

  })
}

//切换要显示的计划图表（每个计划对应一个图表）
function switchChartTab(index){
  chartTab=index;
  loadChart();
}

function loadChart() {
  //激活选中的plan tab
  var tabHtml="";
  for(var i in plans){
    tabHtml+='<div class="tab-item '+(i==chartTab?"active":"")+'"><span onclick="switchChartTab('+parseInt(i)+')">Sprint plan '+(parseInt(i)+1)+'</span></div>'
  }
  $(".chart-tab").html(tabHtml);
  //计算图表横纵坐标数据
  var plan=plans[chartTab];
  var mTasks={};
  var totalHours=0;
  var period=plan.period;
  var ps=period.split("-");
  var startDate=Date.parse(ps[0]);
  var endDate=Date.parse(ps[1])
  var day=(endDate-startDate)/(24*3600000);
  var labels=[];
  var dataBase=[];
  var stories=plan.stories;
  for(var j in stories){
     var tasks=stories[j].tasks;
     for(var m in tasks){
       var du=parseInt(tasks[m].duration);
       totalHours+=du;
       if(tasks[m].status==2){
         var ft=tasks[m].finish_time.substring(0,10);
         if(mTasks[ft]){
           mTasks[ft]+=du;
         }else{
           mTasks[ft]=du;
         }
       }
     }
  }
  var days=[];
  for(var k=0;k<=day+2;k++){
    labels.push(k+"");
    if(k<=day+1){
      dataBase.push(totalHours*k/(day+1));
      days.push(new Date(startDate+(k-1)*24*3600000).Format("yyyy-MM-dd"));
    }
  }
  var currentData=0;
  var realData=[];
  var keys=Object.keys(mTasks);
  for(var i in days){
    var dayHours=0;
    for(var j in keys){
      if(days[i]==keys[j]){
        dayHours=mTasks[keys[j]];
      }
    }
    currentData+=dayHours;
    realData.push(currentData)
  }
  //绘制图表，参考百度echart文档
  var myChart = echarts.init(document.getElementById('myChart'));
  var option = {
    grid: {
        left: '3%',
        right: '3%',
        bottom: '8%',
        containLabel: true
    },
    xAxis: {
        type: 'category',
        name:"day",
        nameLocation:"center",
        boundaryGap: false,
        nameGap:20,
        nameTextStyle:{
          fontWeight:'bold'
        },
        data: labels
    },
    yAxis: {
        type: 'value',
        name:"finish hour",
        nameLocation:"center",
        boundaryGap: false,
        nameGap:20,
         nameTextStyle:{
          fontWeight:'bold'
        },
        nameRotate:90
    },
    series: [{
      type:'line',
      name:"day",
      data: dataBase,
      lineStyle:{
         color:'green'
      }
    },
      {
       type:'line',
        name:"finish hour",
        data: realData,
        lineStyle:{
         color:'orange'
      }
      }
    ]
  };
  myChart.setOption(option);
}


//日期格式化
Date.prototype.Format = function(fmt) {
  var o = {
    "M+": this.getMonth() + 1,
    "d+": this.getDate(),
    "h+": this.getHours(),
    "m+": this.getMinutes(),
    "s+": this.getSeconds(),
    "q+": Math.floor((this.getMonth() + 3) / 3),
    "S": this.getMilliseconds()
  };
  if(/(y+)/.test(fmt))
    fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
  for(var k in o)
    if(new RegExp("(" + k + ")").test(fmt))
      fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
  return fmt;
}

