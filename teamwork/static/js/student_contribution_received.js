var colors_array = [
    "#CD5C5C", "#FFD700", "#ADFF2F", "#00FFFF",
    "#FFC0CB", "#E6E6FA", "#704214", "#778BA5",
    "#CB410B", "#BFC1C2"
];
// Variables for local_barchart
// ---------------------------------------------------------------------------------------------
var member_contributions = JSON.parse(document.getElementById('contributions_of_members').value)
var number_of_members = document.getElementById('Member').options.length
var tsr_number = parseInt(document.getElementById('TSR #').value) - 1;
var local_labels = [];

for(let i = 0; i < number_of_members; i++) {
    let current_member = document.getElementById('Member').options[i].text;
    local_labels.push(current_member);
    document.getElementById(current_member).style = "background-color:" + colors_array[i];
    document.getElementById("raw_" + current_member).style = "background-color:" + colors_array[i];
}
// End of local_barchart variable initializations
// ---------------------------------------------------------------------------------------------

function make_local_barchart() {
/*
* make_local_barchart generates a ChartJS horizontal barchart based on
* what TSR number is selected on the page, then showing the results of contributions
* received in that TSR for each member of a team from each other.
*/
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
/*
* update_local_barchart resets the local_barchart data to reflect
* the newly selected TSR number.
*/
    tsr_number = parseInt(document.getElementById('TSR #').value) - 1;

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

// Variables for historical_barchart
// ---------------------------------------------------------------------------------------------
var tsr_numbers_array = JSON.parse(document.getElementById('tsr_numbers').value)
var current_student = document.getElementById('Member').value;
var current_student_index = document.getElementById('Member').selectedIndex;
var historical_averages = JSON.parse(document.getElementById('member_averages').value);
var historical_labels = [];
var member_historical_averages = [];
for(let i = 0; i < tsr_numbers_array.length; i++) {
    member_historical_averages.push(historical_averages[i][current_student_index]);
    historical_labels.push("TSR #" + tsr_numbers_array[i]);
}
// End of historical_barchart variable initializations
// ---------------------------------------------------------------------------------------------

function make_historical_barchart() {
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

    member_historical_averages = [];
    current_student = document.getElementById('Member').value;
    current_student_index = document.getElementById('Member').selectedIndex;
    for(let i = 0; i < tsr_numbers_array.length; i++) {
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