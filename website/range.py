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
    route = findNext([data['dep']], data['dep'], data['arr'], data['range'], data['rwy'])
    #print(route)
    return optimize(route, data['range'])

def findNext(route, stop, arr, maxRange, rwy):
    #print(route)
    if distance(stop, arr) < int(maxRange):
        return route + [arr]
    stopCoords = coords(stop)
    lat = stopCoords[0]
    long = stopCoords[1]
    calc = "(3443.9 * 2  * atan((sqrt(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2)))/(sqrt(1-(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2))))))".format(lat, lat, long, lat, lat, long)
    query = "select *, round({}) as 'Distance' from airport where a_rwy is not null AND a_rwy > {} HAVING Distance < {} ORDER BY Distance DESC LIMIT 50;".format(calc, rwy, maxRange)
    cursor.execute(query)
    airports = list(cursor.fetchall())
    best = [-1, stop, 999999]
    for i in range(len(airports)):
        airports[i] = list(airports[i])
        airports[i].append(distance(airports[i][4], arr))
    #print(airports)
    """for i in range(len(airports)):
        dist = distance(airports[i][4], arr)
        #dist = [distance(airports[i][4], arr), distance(dep, route[-1])]
        #print(best, i, airports[i][4], dist)
        if  dist < best[2] and best[1] not in route:# and dist[0]:
            
            best = [i, airports[i][4], dist]
    
    route.append(best[1])
    
    #print(route)
    
    if best[2] < int(maxRange):
        route.append(arr)
        return route
    """
    airports.sort(key=sortKey)
    routeLength = distance(route[-1], route[0])
    for i in airports:
        #if len(route) > 1:
        #    print(len(route), distance(i[4], route[-2]), distance(route[-1], route[-2]))
        if i[4] in route:
            continue
        if len(route) > 1 and distance(i[4], route[-2]) < distance(route[-1], route[-2]):
            continue
        #print("next:", i[4], distance(i[4], route[-1]))
        return findNext(route + [i[4]], i[4], arr, maxRange, rwy)
    
    return "No Route"
    
def sortKey(airport):
    #print(airport[-1])
    return airport[-1]
    
def optimize(route, maxRange):
    if len(route) < 3:
        return route
    
    for i in range(len(route)):
        for j in range(i+2, len(route)):
            #print(i,j)
            #print(i, j, distance(route[i], route[j]), maxRange)
            if j < len(route) and distance(route[i], route[j]) < int(maxRange):
                #print("old", route)
                return optimize(route[:i+1]+route[j:], maxRange)
                j = i + 2
                #print("new", route)
    return route
    
"""
def optimize(route, maxRange):
    if len(route) < 3:
        return route
    
    for i in range(len(route)):
        for j in range(i+2, len(route)):
            #print(i,j)
            if j < len(route) and distance(route[i], route[j]) < int(maxRange):
                #print("old", route)
                route = route[:i+1]+route[j:]
                j = i + 2
                #print("new", route)
    return route"""

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

data = b'{"dep":"klax","arr":"phnl","range":"1300", "rwy": "3000"}'
print(rangeResponse(data))
data = b'{"dep":"uuee","arr":"ksfo","range":"1250", "rwy": "3000"}'
print(rangeResponse(data))
data = b'{"dep":"wsss","arr":"eddf","range":"1300", "rwy": "3000"}'
print(rangeResponse(data))
data = b'{"dep":"bikf","arr":"egyp","range":"1300", "rwy": "3000"}'
print(rangeResponse(data))
data = b'{"dep":"bikf","arr":"fact","range":"1300", "rwy": "3000"}'
print(rangeResponse(data))
#print(findNrst(52.3124008, -48.1922503, 3000))