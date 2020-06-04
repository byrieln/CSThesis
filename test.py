import mysql.connector

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()

code = ""

rt = input("Enter departure and arrival: ")
if len(rt) == 8:
    rt = [rt[:4], rt[4:]]
    code = "icao"
else:
    rt = [rt[:3], rt[3:]]
    code = "iata"


query = "select * from airport where a_{} = '{}' or a_{} = '{}';".format(code, rt[0], code, rt[1])
cursor.execute(query)
rt = cursor.fetchall()

query = "select * from route where r_src = '{}' and r_dest = '{}';".format(rt[0][0], rt[1][0])
cursor.execute(query)

rt = cursor.fetchall()

for i in rt:
    query = "select l_icao, r_id, source.a_icao, dest.a_icao, source.r_plane from (route natural join airport) as source, (route natural join airport) as dest"