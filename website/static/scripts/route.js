var haveFleet = false;
var fleet = [];
var departure = "";
var arrival = "";
$("dropButton").ready(getFleet());
$("dropButton").click(dropButton());
$("dropOption").click(countFleet());



$(document).ready(function() {
	$('#update input').change(function(){
		document.getElementById("submission").innerHTML = "Search";
		console.log("Update update");
	});
});

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


function countFleet(){
	//console.log("recount");
	fleet = []
	var div = document.getElementById("fleetDropdown");
	for(let i = 2; i < div.children.length; i++){
		if(div.children[i].tagName == "LABEL"){
			if(div.children[i].children[0].checked){
				fleet.push(div.children[i].children[0].name);
			}
		}
	}
	document.getElementsByClassName("dropButton")[0].innerHTML = "Fleet (" + fleet.length + " selected):";
	//console.log(fleet.length);
}

async function getFleet(){
	if (haveFleet==true) {
		console.log("Already have fleet");
		return;
	}
	console.log("Getting fleet");
	const param = {
		headers: {
			'Content-Type':'text/plain'
		},
		method:"POST",
		body:JSON.stringify("")
	};
	//Send the POST request object to /range
	fetch("/fleet", param)
	.then(function(response) {
		return response.json();
	}).then(function(body) {
		addFleet(body);
	});
}

function addFleet(fleet){
	console.log("fleet "+haveFleet);
	haveFleet = true;
	console.log(fleet);
	var check, temp, entry;
	for(let i = 0; i < fleet.length; i++){
		entry = document.createElement("label");
		entry.setAttribute("class","dropOption");
		//entry.setAttribute("for", fleet[i].icao);
		
		
		check = document.createElement("input");
		check.setAttribute("type", "checkbox");
		check.setAttribute("class", "fleetEntry");
		check.setAttribute("name",fleet[i].icao);
		check.setAttribute("onclick", "countFleet()");
		entry.appendChild(check);
		
		if (fleet[i].iata == ""){
			entry.innerHTML += fleet[i].icao + "\t\t" + fleet[i].name+ "<br>";
		}
		else{
			entry.innerHTML += fleet[i].icao + "/" + fleet[i].iata + "\t" + fleet[i].name + "<br>";
		}
		
		document.getElementById("fleetDropdown").appendChild(entry);
		
		//document.getElementById("fleetDropdown").appendChild(document.createElement("br"));
		dropButton();
	}
}

async function dropButton() {
	console.log("dropbutton");
	
	document.getElementById("fleetDropdown").classList.toggle("show");
	
}

function dropdownFilter() {
	console.log("Dropdown Filter");
	var input, filter, ul, li, a, i;
	input = document.getElementById("fleetInput");
	filter = input.value.toUpperCase();
	a = document.getElementsByClassName("dropOption")
	console.log(a);
	for (i = 0; i < a.length; i++) {
		txtValue = a[i].textContent || a[i].innerHTML;
		if (a[i].innerHTML.includes(filter)) {
			a[i].style.display = "";
		} else {
			a[i].style.display = "none";
		}
	}
} 

async function submission() {
	const form = document.getElementById("update");
	const data = {
		"dep": form[0].value,
		"arr": form[1].value,
		"fleet":fleet,
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
	fetch("/route", param)
	.then(function(response) {
		return response.json();
	}).then(function(body) {
		redraw(body);
	});
}

//draw the responses
function redraw(data){
	/**
	Redraw the response data
	**/
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
	var row = document.createElement("tr");
	add = ["Departure", "Arrival", "Airline", "Airplane", "Distance","Weather at Destination"];
	
	for (let i = 0; i < add.length; i++){		
		var cell = document.createElement("th");
		cell.setAttribute("id",add[i]);
		cell.setAttribute("class","tableHead");
		cell.innerHTML = add[i];
		row.appendChild(cell);
	}
	table.appendChild(row);
	

	
	//populate data
	for(let i = 0; i < data.skip.length; i++){
		addSidebar(data.skip[i], sidebar, false);
		
		
	}
	
	
	for(let i = 0; i < data.route.length; i++){
		//add data to sidebar
		if (i != 0){
			addSidebar(data.route[i], sidebar, true);
		}
		
		//add a jquery listener that triggers the function any time a sidebar checkbox is clicked
		$(".sidebarAirport").on("click", function(){
			document.getElementById("submission").innerHTML = "Update";
		});
		
		//add data to route
		popRow(table, data.route[i], data.lengths[i], data.weather[i]);
		
	}
	
	//add an update button the the sidebar
	
	//add the table to the result
	result.appendChild(table);
	
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

function popRow(table, route, length, weather){
	var row = document.createElement("tr");
	var labels = ["Departure", "Arrival", "Airline", "Airplane", "Distance","Weather at Destination"];
	for(let i = 0; i < labels.length; i++){
		
		var cell = document.createElement("th");
		cell.setAttribute("id",labels[i]);
		cell.setAttribute("class","tableCell");
		if (i == 0){
			cell.innerHTML = "(" + route.depICAO + "/" + route.depIATA + ") " + route.dep;
		} else if (i==1){
			cell.innerHTML = "(" + route.arrICAO + "/" + route.arrIATA + ") " + route.arr;
		} else if (i==2){
			cell.innerHTML = route.flight[0][0];
		} else if (i==3){
			cell.innerHTML = route.flight[0][1]
		} else if (i==4){
			cell.innerHTML = length;
		} else if (i==5) {
			cell.innerHTML = weather;
		}
		row.appendChild(cell);
	}
	row.setAttribute("class", "tableRow");
	table.appendChild(row);
	for(let j = 1; j < route.flight.length; j++){
		row = document.createElement("tr");
		
		for (let i = 0; i < labels.length; i++){
			if (i == 2 || i ==3 ){ //if adding the airline or airplane, add data
				cell = document.createElement("th");
				if (i == 2){
					cell.innerHTML = route.flight[j][0]
				}
				else {
					cell.innerHTML = route.flight[j][1]
				}
			}
			else{
				cell = document.createElement("th");
				cell.innerHTML = "";
			}
			cell.setAttribute("id",labels[i]);
			cell.setAttribute("class","tableCell");
			row.appendChild(cell);
		}
		row.setAttribute("class", "tableRow");
		table.appendChild(row);
	}
	
	
	
	return row
}