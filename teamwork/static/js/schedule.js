// schedule.js
// Allows user to edit their schedule using Full Calendar.

// Don't begin execution until page is ready, this is a fullCalendar requirement.
$(document).ready(function() {

    // Function triggered by submit button
    // verfies events and then calls helper function
    // postEvents to send all client side events to server.
    $('#submit-events').on('submit', function(event){
        // Prevent default behavior of submit form.
        event.preventDefault();
        // Get map of all events added on client side so far.
        var eventsOnSubmit = $('#calendar').fullCalendar('clientEvents');

        if (!Array.isArray(eventsOnSubmit) || !eventsOnSubmit.length) {
          // Array does not exist, is not an array, or is empty.
          $('#emptyAlert').css('display', 'block');
          //alert("Did you forget to fill out your availability?")
        }
        else {
          // Prepare to send event list to server.
          postEvents(eventsOnSubmit);
        }
    });

    // Ajax post call to server, converts circular data structure
    // to list then to JSON.
    function postEvents(cEvents) {
        $.ajax({
            url: 'ajax/save_event/',
            type: 'POST',
            data: {
              // Need to stringfy cEvents (circular structure), but must first
              // iterate through and create a simplier representation.
              jsonEvents: JSON.stringify(cEvents.map(function (e)
              {
                  return {
                      start: e.start,
                      end: e.end,
                      title: e.title,
                  }
              }))
            },
            success: function (response) {
              // Get the response from server and process it
              // In this case simply alert the user.
              alert(response);
            },
            error: function (xhr) {
              // Open JS debugger if ya goofed. Alert with last object.
              // This should really trigger a 500 server error.
              debugger;
              alert(xhr);
          }
        });
    }

    // Intilize the calendar. Options and callbacks set below.
    $('#calendar').fullCalendar({
        // Only show agendaWeek view for edit_schedule
        header: {
          left: 'none',
          center: 'none',
          right: 'none'
        },
        // Day of week shouldn't contain hard coded date.
        columnFormat: 'ddd',
        businessHours: {
            // days of week. an array of zero-based day of week integers (0=Sunday)
            dow: [ 1, 2, 3, 4, 5], // Monday - Friday

            start: '8:00', // a start time (10am in this example)
            end: '22:00', // an end time (6pm in this example)
        },
        defaultView: 'agendaWeek',

        defaultDate: '2017-04-12',

        // Can click day/week names to navigate views
        navLinks: true,

        // Here Sean -andgates
        allDaySlot: false,

        // Allow users to resize events.
        editable: true,

        // Allow "more" link when too many events.
        eventLimit: true,

        // Allow selection for select function.
        selectable: true,
        selectHelper: true,

        // Function called on select event.
        // Adapted from https://fullcalendar.io/js/fullcalendar-3.4.0/demos/selectable.html
        select: function(start, end) {
          // Title is always Busy in edit_schedule
          var title = 'Busy';
          // Event Object to be passed to renderEvent
          var eventData;

          // Always true (likely change this to a check for "all day")
          if (title) {
            // Populate the Event Object. TODO: Add attributes.
            eventData = {
              title: title,
              start: start,
              end: end
            };
            // Render the event object with 'stick' set to true
            // so events persist unless page refresh.
            $('#calendar').fullCalendar('renderEvent', eventData, true);

          }
          // Unselct event area before exiting select method.
          $('#calendar').fullCalendar('unselect');
        },
        // Prepopulate events to make temporary test data.
        events: []

    }) // End fullCalendar initialization.


}); // End main function.
