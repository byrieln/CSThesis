async function submission() {
	const form = document.getElementById("update");
	const data = {
		"dep": form[0].value,
		"arr": form[1].value,
		"range": form[2].value,
		"rwy":form[3].value
	};
	if (data.dep == "" || data.arr == "" || data.range=="" || data.rwy==""){
		console.log("Invalid data!");
		return;
	}
	//NOTE FOR SEPTERMBER 30
	//document.getElementById("output").style.visibility
	//element.children[].checked
	//element.children[].getAttribute('name')
	
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
	for(let i = 0; i < data.route.length-1; i++){
		//add data to sidebar
		if (i != 0){
			addSidebar(data.route[i], sidebar);
		}
		
		//add data to route
		add = document.createElement("tr");
		popRow(add, [data.route[i], data.route[i+1], data.lengths[i], data.weather[i]]);
		add.setAttribute("id", "tableRow");
		table.appendChild(add);
	}
	
	//add an update button the the sidebar
	
	//add the table to the result
	result.appendChild(table);
	
	showOutput();
}

function addSidebar(stop, sidebar) {
	//add a checkbox to the sidebar
	var check = document.createElement("input");
	check.setAttribute("type","checkbox");
	check.setAttribute("name",stop);
	check.setAttribute("value",stop);
	check.checked=true;
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