To run the website, run server.py with python. Before running, several packages must be installed, including flask and mysql connector. 

Mysql connector settings must be updated in both route.py and range.py. 

In the current state, it also requires a valid version of Apache Spark be installed at the location /opt/spark/
	To disable spark:
		comment out line 6 and 53 of route.py and uncomment line 54. 
		comment out lines 11, 12, 13 , and 42 of range.py and uncomment line 43. 

	If permanently disabling spark, all .csv and .ipynb files may be deleted. 