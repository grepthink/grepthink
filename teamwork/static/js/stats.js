// ======================================================
// Doughnut Chart
// ======================================================

// Doughnut Chart Options
var doughnutOptions = {
	//Boolean - Whether we should show a stroke on each segment
	segmentShowStroke : true,

	//String - The colour of each segment stroke
	segmentStrokeColor : "#fff",

	//Number - The width of each segment stroke
	segmentStrokeWidth : 2,

	//The percentage of the chart that we cut out of the middle.
	percentageInnerCutout : 50,

	//Boolean - Whether we should animate the chart
	animation : true,

	//Number - Amount of animation steps
	animationSteps : 100,

	//String - Animation easing effect
	animationEasing : "easeOutBounce",

	//Boolean - Whether we animate the rotation of the Doughnut
	animateRotate : true,

	//Boolean - Whether we animate scaling the Doughnut from the centre
	animateScale : true,

	//Function - Will fire on animation completion.
	onAnimationComplete : null
}

var studs_in_pro = (students_not/total_students);
var studs_not_in_pro = (students_in/total_students);


// Doughnut Chart Data
var doughnutData = [
	{
		value: studs_in_pro,
		color: "#1789D4"
	},
	{
		value : studs_not_in_pro,
		color : "#CB4B16"
	}
]


//Get the context of the Doughnut Chart canvas element we want to select
var ctx = document.getElementById("doughnutChart").getContext("2d");

// Create the Doughnut Chart
var mydoughnutChart = new Chart(ctx).Doughnut(doughnutData, doughnutOptions);
