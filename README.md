# CSThesis
Flight slimulation route selection tool. 

This repository contains all files need to setup and run the tool.
The main folder of this tool contains three folders and a python script. 

The "data" folder contains two .dat, a .txt, and a .json file which contain the data to populate a database. 

The "databse" folder contains a .sql file, which creates a MySQL database called "routegen" for the project to use and the four tables to populate it. 
	It does not configure a user for the Python MySQL connector to use, which must be done manually. 
	
"import.py" imports data from files in the "data" folder into the database. Some steps must be done before running:

	A version of the Python mysql connector must be installed. I use 2.2.9.
	The database access for the mysql connector must be configured. The connecter requires a user to connect as, which needs to be configured through mysql.
	Lines 6-9 of import.py must be changed to fit local mysql connection settings. 
	
To run the website, see readme.md within the "website" folder.