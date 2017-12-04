// ========================================================================================================
// flag_suppression.js
// ========================================================================================================

// Django provided by the Django website to handle csrf tokens
var tsr_number = parseInt(document.getElementById('TSR FLAG #').value) ;
// using jQuery
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
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function update_flag_table() {
    //updates the table to only show the data selected in the drop down menu
    tsr_number = document.getElementById('TSR FLAG #').value; 
    if(!(isNaN(parseInt(tsr_number)))){
        tsr_number = parseInt(tsr_number);
    }
    $('#flag_table').show();
    var dataset = $('#flag_table tbody').find('tr');
    dataset.each(function(index) {
        item = $(this);
        item.hide();

        var tsrTD = item.find('td:first-child');
        var TDVal = parseInt(tsrTD.text());
        if (TDVal == tsr_number)
            item.show();
        else if (tsr_number == 'All')
            item.show()  
        
      });
}

function flag_table_refresh_edit(e){
    //prevents the page from refreshing when editing the flags, calls function in Django Project views
    e.preventDefault();
    var listOfChecks = checkMarked();
    $.ajax({  //Call ajax function sending the option loaded
        url: 'ajax/mark_flags/',
        type: 'POST',
        traditional: true,
        data: {
           csrfmiddlewaretoken: getCookie('csrftoken'),
           listOfChecks: listOfChecks,
        },
         //This is the url of the ajax view where you make the search 
        success: function(data) {
            $('#flag_table_div').html(data);  // Get the results sended from ajax to here
            update_flag_table();
        }
    });   

}

function flag_table_reset(e){    
    //prevents the page from refreshing when editing the flags, calls function in Django Project views
    tsr_number = document.getElementById('TSR FLAG #').value; 
    if(!(isNaN(parseInt(tsr_number)))){
        tsr_number = parseInt(tsr_number);
    }
    e.preventDefault();
    $.ajax({  //Call ajax function sending the option loaded
        url: 'ajax/reset_flags/',
        type: 'POST',
        traditional: true,
        data: {
           csrfmiddlewaretoken: getCookie('csrftoken'),
           tsr_number:tsr_number,
        },
         //This is the url of the ajax view where you make the search 
        success: function(data) {
            $('#flag_table_div').html(data);  // Get the results sended from ajax to here
            update_flag_table();
        }
    });   

}

function checkMarked() {
    //Goes through all of the check boxes of MARK[] and returns the ones that are checked 
    var mark = document.getElementsByName("MARK[]");
    var markArr = [];
    for (var i=0; i < mark.length; i++) {
        if(mark[i].checked){
            markArr.push(mark[i].value);
            console.log(mark[i].value);
        }
    }
    return markArr;
}

update_flag_table();
