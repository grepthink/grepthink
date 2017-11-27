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

function make_local_barchart() {
    let member_contributions = JSON.parse(document.getElementById('contributions_of_members').value)
    let tsr_number = parseInt(document.getElementById('TSR #').value) - 1;
    let number_of_members = document.getElementById('Member').options.length
    var local_labels = [];
    for(let i = 0; i < number_of_members; i++) {
        let current_member = document.getElementById('Member').options[i].text;
        local_labels.push(current_member);
        document.getElementById(current_member).style = "background-color:" + colors_array[i];
    }

    let barChartData = {
        labels: local_labels,
        datasets: []
    };

    for(let i = 0; i < number_of_members; i++) {
        barChartData.datasets.push(
        {
            label: local_labels[i],
            backgroundColor: colors_array[i],
            borderColor: 'black',
            borderWidth: 1,
            data: member_contributions[i][tsr_number]
        });
    }

    var ctx = document.getElementById("local_student_contribution").getContext("2d");
    window.my_local_barchart = new Chart(ctx, {
        type: 'horizontalBar',
        data: barChartData,
        options: {
            // Elements options apply to all of the options unless overridden in a dataset
            // In this case, we are setting the border of each horizontal bar to be 2px wide
            elements: {
                rectangle: {
                    borderWidth: 2,
                }
            },
            responsive: true,
            scales: {
                xAxes: [{
                    ticks: {
                        min: 0,
                        max: 100,
                        stepSize: 10
                    }
                }]
            },
            title: {
                display: true,
                text: "Students' Contribution Scores Received"
            }
        }
    });
}

function update_local_barchart() {
    let member_contributions = JSON.parse(document.getElementById('contributions_of_members').value)
    let tsr_number = parseInt(document.getElementById('TSR #').value) - 1;
    let number_of_members = document.getElementById('Member').options.length
    var local_labels = [];
    for(let i = 0; i < number_of_members; i++) {
        let current_member = document.getElementById('Member').options[i].text;
        local_labels.push(current_member);
        document.getElementById(current_member).style = "background-color:" + colors_array[i];
    }

    my_local_barchart.data.datasets = [];
    for(let i = 0; i < number_of_members; i++) {
        my_local_barchart.data.datasets.push(
        {
            label: local_labels[i],
            backgroundColor: colors_array[i],
            borderColor: 'black',
            borderWidth: 1,
            data: member_contributions[i][tsr_number]
        });
    }
    window.my_local_barchart.update();
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
    var last_element = tsr_numbers_array.pop();
    let my_data_array = []
    for(let i = 0; i < last_element; i++) {
        my_data_array.push(historical_averages[i][current_student_index]);
    }
    let barChartData = {
            labels: historical_labels,
            datasets: [{
                label: current_student,
                backgroundColor: colors_array[current_student_index],
                borderColor: 'black',
                borderWidth: 1,
                data: my_data_array
            }]
    };

    var ctx = document.getElementById("historical_student_contribution").getContext("2d");
    window.my_historical_barchart = new Chart(ctx, {
        type: 'bar',
        data: barChartData,
        options: {
            elements: {
                rectangle: {
                    borderWidth: 2,
                }
            },
            responsive: true,
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 100,
                        stepSize: 10
                    }
                }]
            },
            title: {
                display: true,
                text: "Historical Averages"
            }
        }
    });
}

function update_historical_barchart() {
    my_historical_barchart.data = [];

    let tsr_numbers_array = JSON.parse(document.getElementById('tsr_numbers').value)
    let current_student = document.getElementById('Member').value;
    let current_student_index = document.getElementById('Member').selectedIndex;
    let historical_labels = [];
    for(let i = 0; i < tsr_numbers_array.length; i++) {
        historical_labels.push("TSR #" + tsr_numbers_array[i]);
    }

    let historical_averages = JSON.parse(document.getElementById('member_averages').value)
    var last_element = tsr_numbers_array.pop();
    let member_historical_averages = [];
    for(let i = 0; i < last_element; i++) {
        member_historical_averages.push(historical_averages[i][current_student_index]);
    }
    let barChartData = {
            labels: historical_labels,
            datasets: [{
                label: current_student,
                backgroundColor: colors_array[current_student_index],
                borderColor: 'black',
                borderWidth: 1,
                data: member_historical_averages
            }]
    };
    my_historical_barchart.data = barChartData;
    window.my_historical_barchart.update();
}

make_local_barchart();
make_historical_barchart();