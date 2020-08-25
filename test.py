a = 0.5

print((sqrt(a/(1-a)))==(sqrt(a)))












"""import mysql.connector

from math import sin, cos, sqrt, atan2, radians

radius = 3443.9 #The radius of the earth in nautical miles

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()

code = ""

#rt = input("Enter departure and arrival: ")
rt = "bikfekch"
if len(rt) == 8:
    rt = [rt[:4], rt[4:]]
    code = "icao"
else:
    rt = [rt[:3], rt[3:]]
    code = "iata"


query = "select * from airport where a_{} = '{}' or a_{} = '{}';".format(code, rt[0], code, rt[1])
cursor.execute(query)
rt = cursor.fetchall()

src = [rt[0][5], rt[0][6]]
dest = [rt[1][5], rt[1][6]]


lata = radians(src[0])
longa = radians(src[1])
latb = radians(dest[0])
longb = radians(dest[1])

dlon = longb - longa
dlat = latb - lata

a = sin(dlat/2)**2 + cos(lata) * cos(latb) * sin(dlon/2)**2
c = 2  * atan2(sqrt(a), sqrt(1-a))

distance = radius * c

print("Src: {}, Dest: {}, Distance: {}".format(rt[0][0], rt[1][0], distance))

"""