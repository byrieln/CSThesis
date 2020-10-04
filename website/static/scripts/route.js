var haveFleet = false;



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
		entry = document.createElement("div");
		entry.setAttribute("class","fleetDiv");
		
		check = document.createElement("input");
		check.setAttribute("type", "checkbox");
		check.setAttribute("class", "fleetEntry");
		check.setAttribute("name",fleet[i].icao);
		entry.appendChild(check);
		
		check = document.createElement("label");
		check.setAttribute("for", fleet[i].icao);
		
		temp = document.createElement("div");
		temp.setAttribute("class", "dropName");
		temp.innerHTML = fleet[i].name;
		check.appendChild(temp);
		
		temp = document.createElement("div");
		temp.setAttribute("class", "dropType");
		temp.innerHTML = fleet[i].icao + "/" + fleet[i].iata;
		check.appendChild(temp);
		
		entry.appendChild(check);
		
		document.getElementById("fleetDropdown").appendChild(entry);
		
		document.getElementById("fleetDropdown").appendChild(document.createElement("br"));
	}
}

async function dropButton() {
	console.log("dropbutton");
	
	document.getElementById("fleetDropdown").classList.toggle("show");
	
}

function dropdownFilter() {
  var input, filter, ul, li, a, i;
  input = document.getElementById("fleetInput");
  filter = input.value.toUpperCase();
  div = document.getElementById("fleetDropdown");
  a = div.getElementsByTagName("div");
  console.log(a);
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
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