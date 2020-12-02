from json import loads, dumps
import mysql.connector
from math import sin, cos, sqrt, atan2, radians, ceil, degrees
from time import time
from requests import get


from wxPrediction import getPredictions

def passPredictions(route):
    return getPredictions

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()

def rangeResponse(data):
    """
    takes string request data as input
    outputs trip json
    """
    route = {}
    data = loads(data)
    data['dep'] = data['dep'].upper()
    data['arr'] = data['arr'].upper()
    
    dist = distance(data['dep'], data['arr'])
    
    if dist < int(data['range']):
        route = {
            'legs': 1,
            '0':{
                'dep':data['dep'],
                'arr':data['arr'],
                'dist':dist,
                'skip':data['skipAirports']
            }
        }
    route = findNext([data['dep']], data['dep'], data['arr'], data['range'], data['rwy'], data['skipAirports'])
    print(route)
    if type(route) == list:
        route = optimize(route, data['range'], data['rwy'], data['skipAirports'])
        response = {
            'route':route,
            'lengths':routeLengths(route),
            'weather': getWeather(route[1:]),
            'predict': getPredictions(route[1:]),
            'skip': data['skipAirports']
        }
    
    else:
        response = {
            'route':route,
            'lengths':[],
            'weather': [],
            'predict': [],
            'skip': data['skipAirports']
        }
    print(response)
    return dumps(response)
    
def getWeather(route):
    """
    Gets METAR reports of each destination in route
    """
    weather = []
    for i in route:
        url = 'https://aviationweather.gov/metar/data?ids={}&format=raw&date=&hours=0'.format(i)
        data = get(url).content.decode()
        data = data[data.find('<code>')+6: data.find('</code>')]
        if (len(data) > 500):
            weather.append("No METAR found")
        else:
            weather.append(data)
    return weather

def findNext(route, stop, arr, maxRange, rwy, skip):
    """
    Takes the route so far as input, the current leg departure airport, the desired destination, and airplane range and runway length
    Recursively generates a route from stop to arrival
    returns route with the next stop recursively added to the end
    """
    #print(route)
    #print('findNext before if', stop, codeType(stop))
    if distance(stop, arr) < int(maxRange):
        return route + [arr]
    stopCoords = coords(stop)
    lat = stopCoords[0]
    long = stopCoords[1]
    calc = "(3443.9 * 2  * atan((sqrt(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2)))/(sqrt(1-(pow(sin((radians(a_lat) - radians({}))/2),2) + cos(radians({})) * cos(radians(a_lat)) * pow(sin((radians(a_long) - radians({}))/2),2))))))".format(lat, lat, long, lat, lat, long)
    query = "select *, round({}) as 'Distance' from airport where a_rwy is not null AND a_rwy > {} HAVING Distance < {} and Distance > {} ORDER BY Distance ;".format(calc, rwy, maxRange, int(maxRange)/2)
    cursor.execute(query)
    airports = list(cursor.fetchall())
    #print(stop, len(airports), codeType(stop))
    best = [-1, stop, 999999]
    for i in range(len(airports)):
        airports[i] = list(airports[i])
        #print("findNext a", airports[i][4], arr)
        airports[i].append(distance(airports[i][4], arr))
    #print(airports)
    airports.sort(key=sortKey)
    routeLength = distance(route[-1], route[0])
    #print('findNext top', route[-0], route[-1])
    for i in airports:
        #if len(route) > 1:
        #    print(len(route), distance(i[4], route[-2]), distance(route[-1], route[-2]))
            #print('findNext', i[4], route[-2], route[-1])
        if i[4] in route or i[4] in skip:
            continue
        
        if len(route) > 1 and distance(i[4], route[-2]) < distance(route[-1], route[-2]):
            continue
        #print("next:", i[4], distance(i[4], route[-1]))
        return findNext(route + [i[4]], i[4], arr, maxRange, rwy,skip)
    
    return "No Route"
    
def sortKey(airport):
    """
    Used as the key in a list.sort()
    """
    return airport[-1]
    
def optimize(route, maxRange,rwy,skip):
    """
    Use optimization algorithms to return a more optimal route than generated
    Use cut first, because it is quicker and removes airports that go against progress.
    Gen works less efficiently when circles are in the route
    """
    print("Init:",route)
    route = optimizeCut(route,maxRange)
    print("Cut:", route)
    route = optimizeGen(route[::-1],maxRange,rwy,skip)[::-1]
    
    print("Gen:",route)
    return route

def optimizeCut(route, maxRange):
    """
    first optimization method: Find loops
    """
    if len(route) < 3:
        return route
    
    for i in range(len(route)):
        for j in range(i+2, len(route)):
            #print(i,j)
            #print(i, j, distance(route[i], route[j]), maxRange)
            #print(route)
            if j < len(route) and distance(route[i], route[j]) < int(maxRange):
                #print("old", route)
                return optimizeCut(route[:i+1]+route[j:], maxRange)
                j = i + 2
                #print("new", route)
    return route

def optimizeGen(route, maxRange, rwy, skip):
    """
    second optimization method: Generate routes between stops to see if theyre shorter
    """
    #print("optimizing:",route)
    route
    dists = routeLengths(route)
    
    for i in range(len(route)):
        for j in range(i+2, i+5):
            """
            It is pointless to generate a new route between two airports next to each other in the list
            +5 is given because generation takes a long time and it limits how many generation events happen
            """
            if j >= len(route):
                continue
            newRt = findNext([route[i]], route[i], route[j], maxRange, rwy, skip)
            #print(newRt, route[i:j], sum(routeLengths(newRt)), sum(dists[i:j]),routeLengths(newRt), dists[i:j])
            #print ("lengths:",sum(routeLengths(newRt)), sum(dists[i:j]))
            if newRt == "No Route":
                #print("F"+newRt+"F")
                continue
            if sum(routeLengths(newRt)) < sum(dists[i:j]):
                #print("Must Opzimize!",newRt, route[i:j],"to",route[:i+1]+newRt[1:]+route[j+1:],route[:i+1],newRt[1:],route[j+1:])
                return optimizeGen(route[:i+1]+newRt[1:]+route[j+1:], maxRange, rwy, skip)
    return route

def routeLengths(route):
    dists = []
    for i in range(len(route)-1):
        #print('routeLengths',route[i],route[i+1])
        dists.append(distance(route[i], route[i+1]))
    #print(dists)
    return dists
    
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
    #print('dist', dep, arr)
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
        print(code, "error")
        return "name"

"""
current = time()
data = b'{"dep":"uuee","arr":"ksfo","range":"1250", "rwy": "3000"}'
print(rangeResponse(data), time()-current)

current = time()
data = b'{"dep":"wsss","arr":"eddf","range":"1300", "rwy": "3000"}'
print(rangeResponse(data), time()-current)
current = time()
data = b'{"dep":"bikf","arr":"egyp","range":"1300", "rwy": "3000"}'
print(rangeResponse(data), time()-current)
current = time()
data = b'{"dep":"bikf","arr":"fact","range":"1300", "rwy": "3000"}'
print(rangeResponse(data), time()-current)

current = time()
data = b'{"dep":"kewr","arr":"wsss","range":"1300", "rwy": "3000"}'
print(rangeResponse(data), time()-current)

current = time()
data = b'{"dep":"klga","arr":"ypph","range":"1300", "rwy": "500"}'
print(rangeResponse(data), time()-current)

current = time()
data = b'{"dep":"kmia","arr":"lirf","range":"600", "rwy": "500"}'
print(rangeResponse(data), time()-current)
current = time()
data = b'{"dep":"klax","arr":"phnl","range":"1300", "rwy": "3000"}'
print(rangeResponse(data), time()-current)

"""