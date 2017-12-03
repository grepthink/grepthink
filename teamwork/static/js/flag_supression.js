// ========================================================================================================
// flag_suppression.js
// ========================================================================================================

// Django provided by the Django website to handle csrf tokens
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
    /**/
    var tsr_number= parseInt(document.getElementById('TSR FLAG #').value);
    $('#flag_table').show();
    var dataset = $('#flag_table tbody').find('tr');
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
}


update_flag_table();
