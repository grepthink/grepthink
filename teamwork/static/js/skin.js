// Set up the variable to save the optional UI color design, and get the current color
var skins = ["skin-green-light","skin-green"];
var ls=window.localStorage;
var current_skin=ls.getItem("current_skin");
if(!current_skin){
  current_skin=0;
}
// Set up a monitor to keep watch over the motion of the user ( see whether the user have click the button
var start;
    window.onload = function () {
         start = setInterval(function(){
            if (document.readyState == "complete") {

               try{
                  if(current_skin==1){
                     $('body.skin-blue').removeClass(skins[0]);
                  }
                  $('body.skin-blue').addClass(skins[current_skin]);
                  clearInterval(start);
               }catch(err){
                   return true;
               }
             }
          }, 0.0001);
    }

//The equation will change the color of UI after user press the button
function switchSkin(){
    var ns;
    if(current_skin==0){
      skinName=skins[1];
      ns=1;
    }else{
      skinName=skins[0];
      ns=0;
    }
    $('body.skin-blue').removeClass(skins[current_skin]);
    $('body.skin-blue').addClass(skinName);
    ls.setItem("current_skin",ns);
    current_skin = ns;
}
