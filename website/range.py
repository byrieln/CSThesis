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
    
    #mids = findMidpoints(data['dep'], data['arr'], legs)
    
    #airports = []
    #for i in mids:
        #airports.append(findNrst(i[0], i[1], data['rwy']))
    
    #return mids
    
    return findNext([data['dep']], data['dep'], data['arr'], data['range'], data['rwy'])

def findNext(route, stop, arr, maxRange, rwy):
    stopCoords = coords(stop)
    lat = stopCoords[0]
    long = stopCoords[1]
    calc = "(3443.9 * 2  * atan((sqrt(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2)))/(sqrt(1-(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2))))))".format(lat, lat, long, lat, lat, long)
    query = "select *, round({}) as 'Distance' from airport where a_rwy is not null AND a_rwy > {} HAVING Distance < {} ORDER BY Distance DESC LIMIT 100;".format(calc, rwy, maxRange)
    cursor.execute(query)
    airports = list(cursor.fetchall())
    best = [-1, stop, 999999]
    for i in range(len(airports)):
        dist = distance(airports[i][4], arr)
        if  dist < best[2]:
            best = [i, airports[i][4], dist]
        print(best)
    
    route.append(best[1])
    
    if best[2] < int(maxRange):
        route.append(arr)
        return route
    
    return findNext(route, best[1], arr, maxRange, rwy)
    
    
    
def findNrst(lat, long, rwy):
    radius = 3443.9 #The radius of the earth in nautical miles
    calc = "(3443.9 * 2  * atan((sqrt(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2)))/(sqrt(1-(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2))))))".format(lat, lat, long, lat, lat, long)
    query = "select *, round({}) as 'Distance' from airport where a_rwy is not null AND a_rwy > {} ORDER BY Distance ASC LIMIT 50;".format(calc, rwy)
    cursor.execute(query)
    out = cursor.fetchall()
    for i in range(len(out)):
        out[i] = list(out[i])
    return out

def findMidpoints(dep, arr, legs):
    src = coords(dep)
    dest = coords(arr)
    
    points = []
    for i in range(1, legs):
        print(i, legs)
        points.append([(i/legs)*(src[0]+dest[0]), (i/legs)*(src[1]+dest[1])])
    
    return points


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

    #print("Src: {}, Dest: {}, Distance: {}, midpoint: {}, {}".format(getAirportInfo(dep)[0], getAirportInfo(arr)[0], int(distance), degrees((lata+latb)/2), degrees((longa+longb)/2)))
    return int(distance)



def codeType(code):
    if len(code) == 4:
        return "icao"
    elif len(code) == 3:
        return "iata"
    else:
        return "error"

data = b'{"dep":"klax","arr":"yssy","range":"2000", "rwy": "7000"}'
print(rangeResponse(data))
#print(findNrst(52.3124008, -48.1922503, 3000))