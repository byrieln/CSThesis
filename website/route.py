from json import loads, dumps
import mysql.connector
from math import sin, cos, sqrt, atan2, radians, ceil, degrees
from time import time
from requests import get

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()

def getFleet():
    query = "SELECT * FROM plane;"
    cursor.execute(query)
    query = cursor.fetchall()
    fleet = []
    for plane in query:
        (icao, iata, name) = plane
        plane = {
            'icao': icao,
            'iata': iata, 
            'name': name
        }
        if plane['iata']=='N/A' or plane['iata']=='NUL':
            plane ['iata'] = ""
        fleet.append(plane)
    
    return dumps(fleet)

def routeResponse(data):
    """
    takes string request data as input
    outputs trip json
    """
    route = {}
    data = loads(data)
    data['dep'] = data['dep'].upper()
    data['arr'] = data['arr'].upper()
    
    route = findRoute(data['dep'], data['arr'], data['fleet'])
    if type(route) == list:
        #route = optimize(route, data['range'], data['rwy'], data['skipAirports'])
        response = {
            'route':route,
            'lengths':routeLengths(route),
            'weather': getWeather(route[1:]),
            'skip': data['skipAirports']
        }
    
    else:
        response = {
            'route':route,
            'lengths':[],
            'weather': [],
            'skip': data['skipAirports']
        }
    return dumps(response)
    
def findRoute(dep, arr, types):
    route = []
    
    print(dep, arr)
    routes = []
    for type in types:
        
        query = "select * from route where r_dep = '{}' and (r_plane IN(SELECT p_iata FROM plane where p_icao = '{}'));".format(dep, type)
        print(query)
        cursor.execute(query)
        query = cursor.fetchall()
        for i in query:
            routes.append(list(i)+[distance(i[3], arr)])
    
    #print(routes)
    routes.sort(key=routeSortKey)
    print(routes)
    #return route

def routeSortKey(route):
    return route[-1]

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

def routeLengths(route):
    dists = []
    for i in range(len(route)-1):
        #print('routeLengths',route[i],route[i+1])
        dists.append(distance(route[i], route[i+1]))
    #print(dists)
    return dists
    
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


current = time()
data = b'{"dep":"bikf","arr":"uuee","fleet":["B752", "A320"], "skipAirports":[]}'
print(routeResponse(data), time()-current)


"""
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