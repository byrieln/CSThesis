from json import loads
import mysql.connector
from math import sin, cos, sqrt, atan2, radians, ceil, degrees

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()

def rangeResponse(data):
    """
    takes string request data as input
    outputs trip json
    """
    route = {}
    data = loads(data)
    dist = distance(data['dep'], data['arr'])
   
    legs = ceil(dist/int(data['range']))
    
    if legs == 1:
        route = {
            'legs': 1,
            '0':{
                'dep':data['dep'],
                'arr':data['arr'],
                'dist':dist
            }
        }
    
    
    return legs

def coords(airport):
    query = "select a_lat, a_long from airport where a_{} = '{}';".format(codeType(airport), airport)
    cursor.execute(query)
    result = cursor.fetchall()
    
    return [result[0][0], result[0][1]]

def getAirportInfo(code):
    query = "select * from airport where a_{} = '{}';".format(codeType(code), code)
    cursor.execute(query)
    fetch = cursor.fetchall()
    result = []
    for i in fetch[0]:
        result.append(i)
    return result

def distance(dep, arr):
    radius = 3443.9 #The radius of the earth in nautical miles
    
    src = coords(dep)
    dest = coords(arr)
    
    lata = radians(src[0])
    longa = radians(src[1])
    latb = radians(dest[0])
    longb = radians(dest[1])

    dlon = longb - longa
    dlat = latb - lata

    a = sin(dlat/2)**2 + cos(lata) * cos(latb) * sin(dlon/2)**2
    c = 2  * atan2(sqrt(a), sqrt(1-a))

    distance = radius * c

    print("Src: {}, Dest: {}, Distance: {}, midpoint: {}, {}".format(getAirportInfo(dep)[0], getAirportInfo(arr)[0], int(distance), degrees((lata+latb)/2), degrees((longa+longb)/2)))
    return int(distance)



def codeType(code):
    if len(code) == 4:
        return "icao"
    elif len(code) == 3:
        return "iata"
    else:
        return "error"

data = b'{"dep":"bikf","arr":"jfk","range":"1250"}'
print(rangeResponse(data))