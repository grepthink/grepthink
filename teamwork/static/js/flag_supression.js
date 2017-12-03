//var tsr_number = parseInt(document.getElementById('TSR FLAG #').value) ;
$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});



function update_flag_table() {
    var tsr_number= parseInt(document.getElementById('TSR FLAG #').value);
    $('#flag_table').show();
    var dataset = $('#flag_table tbody').find('tr');
    /*dataset.show();*/
    dataset.each(function(index) {
        item = $(this);
        item.hide();

        var tsrTD = item.find('td:first-child');
        var TDVal = parseInt(tsrTD.text());
        if (TDVal == tsr_number)
            item.show();
        else if (tsr_number == 0)
            item.show()  
        
      });
/* 
    $.ajax({
        url:''
        method:''


    })
}

function doFunction(e){       
    e.preventDefault();
    $.ajax({  //Call ajax function sending the option loaded
        url: 'ajax/mark_flags/',
        type: 'POST',
         //This is the url of the ajax view where you make the search 
        success: function(data) {
            $('#flag_table_div').html(data);  // Get the results sended from ajax to here
        }
    });   
*/

}


update_flag_table();
