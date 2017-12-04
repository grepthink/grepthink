// ======================================================
// Doughnut Chart
// ======================================================

var total_students = document.getElementById("total_students").value;
var total_projects = document.getElementById("total_projects").value;
var students_not = document.getElementById("students_not").value;
var students_projects = document.getElementById("students_projects").value;

var studs_in_pro = (students_projects/total_students);
var studs_not_in_pro = (students_not/total_students);

var doughnutOptions = {
	type: 'doughnut',
	data: {
		datasets: [{
			data: [
				studs_in_pro,
				studs_not_in_pro
			],
			backgroundColor: ['#1789D4', '#CB4B16'],
			label: 'Stuff'
		}],
		labels: [
			'IN',
			'OUT'
		]
	},
	options: {
		responsive: true,
		cutoutPercentage : 25,
		animation: {
			easing: "easeOutBounce",
		}
	}
};

console.log(total_students);
console.log(total_projects);
console.log(students_not);
console.log(students_projects);

var ctx = document.getElementById("doughnutChart").getContext("2d");
var mydoughnutChart = new Chart(ctx, doughnutOptions);
