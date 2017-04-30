var event_list = [];
// Submit post on submit
$('#post-form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    save_one(event_list);
});

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');


function save_one(eventData) {
    console.log(eventData);
    $.ajax({
        type: "POST",
        url: "ajax/save_event/",
        //url: "",
        headers: {
            "X-CSRFToken": csrftoken,
            "Content-Type": "application/json",
        },
        data: eventData,
        //dataType: "text",
        // error: {
        //    console.log("I had an error! :(");
        // },
        success: function(data){
            console.log("success");
            console.log(data);
        },
        failure: function(data){
            console.log("failure");
            console.log(data);
        },
    });

}

  $(function () {

  $('#calendar').fullCalendar({
      header: {
        left: 'none',
        center: 'title',
        right: 'agendaWeek'
      },
      defaultDate: '2017-04-12',
      defaultView: 'agendaWeek',
      navLinks: true, // can click day/week names to navigate views
      selectable: true,
      selectHelper: true,
      select: function(start, end) {
        var title = 'Busy';
        var eventData;
        if (title) {
          eventData = {
            title: title,
            start: start,
            end: end
          };
          //console.log("HI THERE" + eventData.start);
          $('#calendar').fullCalendar('renderEvent', eventData, true); // stick? = true
          event_list.push(eventData);
          //save_one(event_list);
        }
        //console.log($('#calendar').fullCalendar('clientEvents'));
        console.log("Event list:");
        console.log(event_list);
        //save_one(($('#calendar').fullCalendar('clientEvents')));
        //save_one(event_list);
        $('#calendar').fullCalendar('unselect');
      },
      editable: true,
      eventLimit: true, // allow "more" link when too many events
      events: []
    });
  });
