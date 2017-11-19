//Used the following answer for making random colors:
//https://stackoverflow.com/a/1484514
function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}

function makeBarChart() {
    let member_contributions = JSON.parse(document.getElementById('contributions_of_members').value)
    let tsr_number = parseInt(document.getElementById('TSR #').value) - 1;
    let current_student = document.getElementById('Member').value;
    let current_student_index = document.getElementById('Member').selectedIndex;
    var local_labels = [];
    for(let i = 0; i < (document.getElementById('Member').options.length); i++) {
        local_labels.push(document.getElementById('Member').options[i].text);
    }
    //var other_members = (document.getElementById('other_members').value).split(",");
    //var other_member_contributions = (document.getElementById('other_member_contributions').value).split(",")
    let barChartOptions = {
        //Boolean - Whether we should show a stroke on each segment
        barShowStroke : true,
        scaleOverride: true,
        scaleSteps: 10,
        scaleStepWidth: 10,
        scaleStartValue: 0,
        scaleLineColor: "rgba(0,0,0,.1)",
        scaleLineWidth: 1,
        scaleShowLabels: true,
        scaleLabel: "<%=value%>",
        scaleFontFamily: "'Arial'",
        scaleFontSize: 12,
        scaleFontStyle: "normal",
        scaleFontColor: "#666",
        scaleShowGridLines: !0,
        scaleGridLineColor: "rgba(0,0,0,.05)",
        scaleGridLineWidth: 1,

        //Number - The width of each segment stroke
        barStrokeWidth : 2,

        //Boolean - Whether we should animate the chart
        animation : true,

        //Number - Amount of animation steps
        animationSteps : 100,

        //String - Animation easing effect
        animationEasing : "easeOutBounce",
    };
    let barChartData = {
        labels: local_labels,
        datasets: [{
            fillColor: getRandomColor(),
            strokeColor: 'black',
            borderWidth: 1,
            data: member_contributions[tsr_number][current_student_index]
        }]
    };

    var ctx = document.getElementById("local_student_contribution").getContext("2d");
    new Chart(ctx).Bar(barChartData, barChartOptions)
}

function make_historical_barchart() {
    let tsr_numbers_array = JSON.parse(document.getElementById('tsr_numbers').value)
    let historical_labels = [];
    for(let i = 0; i < (document.getElementById('Member').options.length); i++) {
        historical_labels.push(document.getElementById('Member').options[i].text);
    }
    let historical_averages = JSON.parse(document.getElementById('member_averages').value)
    //var other_members = (document.getElementById('other_members').value).split(",");
    //var other_member_contributions = (document.getElementById('other_member_contributions').value).split(",")
    let barChartOptions = {
        //Boolean - Whether we should show a stroke on each segment
        barShowStroke : true,
        scaleOverride: true,
        scaleSteps: 10,
        scaleStepWidth: 10,
        scaleStartValue: 0,
        scaleLineColor: "rgba(0,0,0,.1)",
        scaleLineWidth: 1,
        scaleShowLabels: true,
        scaleLabel: "<%=value%>",
        scaleFontFamily: "'Arial'",
        scaleFontSize: 12,
        scaleFontStyle: "normal",
        scaleFontColor: "#666",
        scaleShowGridLines: !0,
        scaleGridLineColor: "rgba(0,0,0,.05)",
        scaleGridLineWidth: 1,

        //Number - The width of each segment stroke
        barStrokeWidth : 2,

        //Boolean - Whether we should animate the chart
        animation : true,

        //Number - Amount of animation steps
        animationSteps : 100,

        //String - Animation easing effect
        animationEasing : "easeOutBounce",
    };
    let barChartData = {
        labels: historical_labels,
        datasets: []
    };
    var last_element = tsr_numbers_array.pop();
    for(let i = 0; i < last_element; i++) {
        barChartData.datasets.push(
        {
            fillColor: getRandomColor(),
            strokeColor: 'black',
            borderWidth: 1,
            data: historical_averages[i]
        }
        )
    }

    let ctx = document.getElementById("historical_student_contribution").getContext("2d");
    new Chart(ctx).Bar(barChartData, barChartOptions)
}

makeBarChart();
make_historical_barchart();