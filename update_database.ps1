Invoke-WebRequest https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat -o data/airports.dat
Invoke-WebRequest https://raw.githubusercontent.com/jpatokal/openflights/master/data/airlines.dat -o data/airlines.dat
Invoke-WebRequest https://raw.githubusercontent.com/jpatokal/openflights/master/data/countries.dat -o data/countries.dat
#Invoke-WebRequest https://raw.githubusercontent.com/jpatokal/openflights/master/data/planes.dat -o data/planes.dat
Invoke-WebRequest https://raw.githubusercontent.com/jpatokal/openflights/master/data/routes.dat -o data/routes.dat
#Invoke-WebRequest https://en.wikipedia.org/wiki/Special:Export/List_of_aircraft_type_designators -o data/planes.xml
Invoke-WebRequest https://en.wikipedia.org/wiki/List_of_aircraft_type_designators -o data/planes.html