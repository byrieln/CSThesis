var departure = "";
var arrival = "";

$(document).ready(function() {
	$('#update input').change(function(){
		document.getElementById("submission").innerHTML = "Search";
		console.log("Update update");
	});
});




async function submission() {
	const form = document.getElementById("update");
	const data = {
		"dep": form[0].value,
		"arr": form[1].value,
		"range": form[2].value,
		"rwy":form[3].value,
		"skipAirports":[]
	};
	if (data.dep == "" || data.arr == "" || data.range=="" || data.rwy==""){
		console.log("Invalid data!");
		return;
	}

	
	//if the departure and arrival airports are the same as the previous result, send a list of airport to skip
	var result = document.getElementById("output");
	//console.log(result.style.visibility);
	if (result.style.visibility == "visible"){
		//console.log(departure + " " + data.dep + " " + arrival + " " + data.arr);
		if (departure == data.dep && arrival == data.arr){
			result = document.getElementById("sidebar");
			//console.log("result " + result);
			for (let i = 0; i < result.children.length; i++){
				//console.log(result.children[i].tagName);
				if (result.children[i].tagName == "INPUT" && result.children[i].checked == false){
					data.skipAirports.push(result.children[i].getAttribute("name"));
					console.log("skip " + result.children[i].getAttribute("name"));
				}
			}
		}
	}
	departure = data.dep;
	arrival = data.arr;
	
	
	//create a POST request with the data
	const param = {
		headers: {
			'Content-Type':'text/plain'
		},
		method:"POST",
		body:JSON.stringify(data)
	};
	console.log(data);
	showLoading();
	//Send the POST request object to /range
	fetch("/range", param)
	.then(function(response) {
		return response.json();
	}).then(function(body) {
		redraw(body);
	});
}



function showLoading(){
	//show the Loading element and hide the others
	document.getElementById("output").style.visibility = "hidden";
	document.getElementById("noResult").style.visibility = "hidden";
	document.getElementById("loading").style.visibility = "visible";
}
function showOutput(){
	//show the Output element and hide the others
	document.getElementById("output").style.visibility = "visible";
	document.getElementById("noResult").style.visibility = "hidden";
	document.getElementById("loading").style.visibility = "hidden";
}
function showNoResult(){
	//show the No Result element and hide the others
	document.getElementById("output").style.visibility = "hidden";
	document.getElementById("noResult").style.visibility = "visible";
	document.getElementById("loading").style.visibility = "hidden";
}

//draw the responses
function redraw(data){
	/**
	Redraw the response data
	**/
	console.log(data);
	//get variables for the sidebar and result
	var sidebar = document.getElementById("sidebar");
	var result = document.getElementById("result");
	
	if (data.route=="No Route"){
		showNoResult();
		return;
	}
	
	//reset current data
	sidebar.innerHTML = "";
	result.innerHTML = "";
	
	console.log("redraw");
	console.log(data.route);
	
	//made a sidebar header
	var add = document.createElement("h4");
	add.innerHTML = "Airports:";
	sidebar.appendChild(add);
	
	//make a table header in the result
	var table = document.createElement("table");
	add = document.createElement("tr");
	popRow(add, ["Departure","Arrival","Distance","Weather at Destination"]);
	add.setAttribute("id","tableHead");
	table.appendChild(add);
	
	//populate data
	for(let i = 0; i < data.skip.length; i++){
		addSidebar(data.skip[i], sidebar, false);
	}
	
	
	for(let i = 0; i < data.route.length-1; i++){
		//add data to sidebar
		if (i != 0){
			addSidebar(data.route[i], sidebar, true);
		}
		
		//add a jquery listener that triggers the function any time a sidebar checkbox is clicked
		$(".sidebarAirport").on("click", function(){
			document.getElementById("submission").innerHTML = "Update";
		});
		
		//add data to route
		add = document.createElement("tr");
		popRow(add, [data.route[i], data.route[i+1], data.lengths[i], data.weather[i]]);
		add.setAttribute("id", "tableRow");
		table.appendChild(add);
	}
	
	//add an update button the the sidebar
	
	//add the table to the result
	result.appendChild(table);
	
	weather = document.getElementById('weather');
	add = document.createElement("h4");
	add.innerText = "Weather Challenges:";
	weather.innerHTML = "";
	weather.appendChild(add);
	
	pred = data.predict;
	if (pred.delay.length > 0){
		add = document.createElement("p");
		add.setAttribute("id", "delay");
		add.innerText = "Delay likely at ";
		for (let i = 0; i < pred.delay.length; i++){
			if (i == pred.delay.length -1){
				if(pred.delay.length != 1){
					add.innerText += "and "
				}
				add.innerText += pred.delay[i]+". Consider loading additional fuel in case of holding.";
			}else{
				add.innerText += pred.delay[i]+", ";
			}
		}
		weather.appendChild(add);
		weather.appendChild(document.createElement("br"));
	}
	if (pred.divert.length > 0){
		add = document.createElement("p");
		add.setAttribute("id", "divert");
		add.innerText = "Diversions likely at ";
		for (let i = 0; i < pred.divert.length; i++){
			if (i == pred.divert.length -1){
				if(pred.divert.length != 1){
					add.innerText += "and "
				}
				add.innerText += pred.divert[i]+". Consider loading addition fuel for diversions and keeping an eye on weather at nearby airports. ";
			}else{
				add.innerText += pred.divert[i]+", ";
			}
		}
		weather.appendChild(add);
		weather.appendChild(document.createElement("br"));
	}
	if (pred.cancel.length > 0){
		add = document.createElement("p");
		add.setAttribute("id", "cancel");
		add.innerText = "Cancellations likely at ";
		for (let i = 0; i < pred.cancel.length; i++){
			if (i == pred.cancel.length -1){
				if(pred.cancel.length != 1){
					add.innerText += "and "
				}
				add.innerText += pred.cancel[i]+". Considering adding deselecting these airports in the left sidebar. ";
			}else{
				add.innerText += pred.cancel[i]+", ";
			}
		}
		weather.appendChild(add);
		weather.appendChild(document.createElement("br"));
	}
	if (pred.cancel.length == 0 && pred.divert.length == 0 && pred.cancel.length == 0){
		add = document.createElement("p");
		add.innerText = "No weather delays predicted. Have a good trip!";
		weather.appendChild(add);
		weather.appendChild(document.createElement("br"));
	}
	
	showOutput();
}

function addSidebar(stop, sidebar, checked) {
	//add a checkbox to the sidebar
	var check = document.createElement("input");
	check.setAttribute("type","checkbox");
	check.setAttribute("name",stop);
	check.setAttribute("value",stop);
	check.setAttribute("class","sidebarAirport");
	check.checked=checked;
	sidebar.appendChild(check);
	
	//add a label to the checkbox
	check = document.createElement("label");
	check.setAttribute("for", stop);
	check.innerHTML = stop;
	sidebar.appendChild(check);
	
	//add a line break
	sidebar.appendChild(document.createElement("br"));
	
}

function popRow(row, data){
	var labels = ["Departure","Arrival","Distance","Weather"];
	for(let i = 0; i < data.length; i++){
		var cell = document.createElement("th");
		cell.setAttribute("id",labels[i]);
		cell.setAttribute("class","tableCell");
		cell.innerHTML = data[i];
		row.appendChild(cell);
	}
}