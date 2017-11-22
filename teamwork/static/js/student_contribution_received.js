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

var colors_array = [];
var member_length = document.getElementById('Member').options.length;
for(let i = 0; i < member_length; i++) {
    colors_array.push(getRandomColor());
}

function makeBarChart() {
    let member_contributions = JSON.parse(document.getElementById('contributions_of_members').value)
    let tsr_number = parseInt(document.getElementById('TSR #').value) - 1;
    let number_of_members = document.getElementById('Member').options.length
    var local_labels = [];
    for(let i = 0; i < number_of_members; i++) {
        let current_member = document.getElementById('Member').options[i].text;
        local_labels.push(current_member);
        document.getElementById(current_member).style = "background-color:" + colors_array[i];
    }
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
        datasets: []
    };
    for(let i = 0; i < number_of_members; i++) {
        barChartData.datasets.push(
        {
            fillColor: colors_array[i],
            strokeColor: 'black',
            borderWidth: 1,
            data: member_contributions[i][tsr_number]
        }
        )
    }

    var ctx = document.getElementById("local_student_contribution").getContext("2d");
    try {
        new Chart(ctx).Bar(barChartData, barChartOptions)
    } catch(myError) {
        console.log(myError.message)
    }
}

function make_historical_barchart() {
    let tsr_numbers_array = JSON.parse(document.getElementById('tsr_numbers').value)
    let current_student = document.getElementById('Member').value;
    let current_student_index = document.getElementById('Member').selectedIndex;
    let historical_labels = [];
    for(let i = 0; i < tsr_numbers_array.length; i++) {
        historical_labels.push("TSR #" + tsr_numbers_array[i]);
    }
    //let member_contributions = JSON.parse(document.getElementById('contributions_of_members').value)
    let historical_averages = JSON.parse(document.getElementById('member_averages').value)
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
    var last_element = tsr_numbers_array.pop();
    let my_data_array = []
    for(let i = 0; i < last_element; i++) {
        my_data_array.push(historical_averages[i][current_student_index]);
    }
    let barChartData = {
            labels: historical_labels,
            datasets: [{
                fillColor: colors_array[current_student_index],
                strokeColor: 'black',
                borderWidth: 1,
                data: my_data_array
            }]
    };
    let ctx = document.getElementById("historical_student_contribution").getContext("2d");
    new Chart(ctx).Bar(barChartData, barChartOptions)
}

makeBarChart();
make_historical_barchart();