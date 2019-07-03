$('.content-wrapper').css("min-height",$(window).height()-106)
function changeCheck(target){
  var checked=$(target)[0].checked;
  $(target).parent().parent().find("li input").each(function(item,index){
     $(this)[0].checked=checked;
  });
}


function beforePostEmail(){
   var receivers=[];
   $("#receiver").find("li input").each(function(item,index){
      if($(this)[0].checked){
        receivers.push($(this).prev().text().trim())
      }
   });
   if(receivers.length==0){
      $("#receiver").tooltip("show");
      setTimeout(function(){
         $("#receiver").tooltip("hide");
      },2000)
      return false;
   }
   var subject=$("#id_subject").val();
   var content=$("#id_content").val();
   var email={
         subject:subject,
         content:content,
         receivers:receivers
      }
   var data={
      email:JSON.stringify(email)
   }
   console.log(data);
   $.ajax({
      url:emailSendUrl,
      method:"POST",
      data:data,
      success:function(res){
         if(res.code==0){
            window.location.href="/course/"+res.course+"/";
         }
      }
   })
   return false;
}

