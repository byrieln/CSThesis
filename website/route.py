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
    route = []
    data = loads(data)
    data['dep'] = data['dep'].upper()
    data['arr'] = data['arr'].upper()
    
    route = findRoute([data['dep']], data['dep'], data['arr'], data['fleet'], data['skipAirports'])
    route = optimize(route, data['fleet'])
    legs = getLegs(route, data['fleet'])
    
    if type(route) == list:
        #route = optimize(route, data['range'], data['rwy'], data['skipAirports'])
        response = {
            'route':legs,
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
    print(response)
    return dumps(response)
    
def optimize(route, types):
    for type in types:
        for i in range(len(route)-1):
            for j in range(i+2, len(route)):
                #print(type, i,j)
                query = "select * from route where r_dep = '{}' and r_arr = '{}' and (r_plane IN(SELECT p_iata FROM plane where p_icao = '{}'));".format(route[i], route[j], type)
                #print(query, end = " ")
                cursor.execute(query)
                query = cursor.fetchall()
                #print(query, end = "")
                if len(query) > 0:
                    #print("found")
                    route = route[:i+1]+route[j:]
    #print (route)
    return route
    
def getLegs(route, fleet):
    #print("Legs: ", route)
    legs = []
    for i in range(len(route)-1):
        dep = getAirportName(route[i])
        arr = getAirportName(route[i+1])
        currentLeg = {
            'depICAO':route[i],
            'dep': dep[0],
            'depIATA': dep[1],
            'arrICAO':route[i+1], 
            'arr': arr[0],
            'arrIATA': arr[1],
            'flight':[]
        }
        #query = "SELECT * FROM route WHERE r_dep = {} and r_arr
        for type in fleet:
            query = "select * from route where r_dep = '{}' and r_arr = '{}' and (r_plane IN(SELECT p_iata FROM plane where p_icao = '{}'));".format(route[i], route[i+1], type)
            cursor.execute(query)
            query = cursor.fetchall()
            for j in query:
                entry = [getAirlineName(j[1]), planeIataToIcao(j[4])]
                if entry not in currentLeg['flight']:
                    currentLeg['flight'].append(entry)
        legs.append(currentLeg)
    return legs
   
def planeIataToIcao(iata):
    query = "SELECT p_name FROM plane WHERE p_iata = '{}';".format(iata)
    cursor.execute(query)
    query = cursor.fetchall()
    return query[0][0]
    
def getAirlineName(icao):
    query = "SELECT l_name FROM airline WHERE l_icao = '{}'".format(icao)
    cursor.execute(query)
    query = cursor.fetchall()
    return query[0][0]

def getAirportName(icao):
    query = "SELECT a_name, a_iata FROM airport WHERE a_icao = '{}'".format(icao)
    cursor.execute(query)
    query = cursor.fetchall()
    return query[0]
   
class Airport():
    def __init__(self, code, dep, arr, route):
        self.icao = code
        self.dep = dep
        self.arr = arr
        self.distLeft = distance(code, arr)
        self.route = route
        self.routeLen = sum(routeLengths(route))
    def getIcao(self):
        return self.icao
    def getDistLeft(self):
        return self.distLeft
    def getRoute(self):
        return self.route
    def getRouteLen(self):
        return self.routeLen
    def setRoute(self, route, length):
        self.route = route
        self.routeLen = length
    def apPrint(self):
        print(self.icao, end = " ")

def findRoute(route, dep, arr, types, skip):
    
    #Create a list of airports that have been visited
    airports = [Airport(arr, dep, arr, [])]
    
    #Save the best route length found, so far. Default is much higher than flying around earth.
    optimal = 999999999999
    
    #Create a list, that is used roughly as a queue, based on available routes
    dests = [[dep, [dep]]]
    
    #Keep track of how many times the while look runs. The first few iterations sort the dests list.
    iteration = 0
    
    #Break out of the loop once no more nodes can be visited
    while (len(dests) > 0):
    
        #The length of the route so far
        length = sum(routeLengths(dests[0][1])) + distance(dests[0][0], arr)
        print(dests[0], getAP(airports, arr).getRoute())
        printList(airports)
        if dests[0][0] == 'OMDB':
            print(length, getAP(airports, arr).getRouteLen())
            print(routeLengths(dests[0][1]), routeLengths(getAP(airports, arr).getRoute()))
        #If the length of the new route is longer than the best length, ignore it
        if length > optimal:
            
            #remove the destination from the list and continue using it
            dests.remove(dests[0])
            continue
            
        #If the airport is already in the lest, edit it rather than add it
        elif getAP(airports, dests[0][0]) != None:
            
            #find the airport's index to mutate it from the airports list
            index = find(airports, dests[0][0])
            
            #The new route to the node is better if it is shorter
            if airports[index].getRouteLen() > length:
                airports[index].setRoute(dests[0][1], length)
            
            #Check if the current node is the destination
            if dests[0][0] == arr:
                #If the length is shorter than the optimal route, the current route becomes optimal
                if length < optimal:
                    optimal = length
                    #If there are only two items in the route, they are the departure and arrival, and a direct flight exists
                    if len(getAP(airports, arr).getRoute())==2:
                        return getAP(airports, arr).getRoute()
        #If the airport node hasn't been visited yet and the route to it is shorter than the optimal route
        else:
            #
            if length < optimal:
                
                
                airports = insert(airports, dests[0][0], dep, arr, dests[0][1], optimal)
                if dests[0][0] == arr:
                    optimal = length
                    
                    #If the only two items in the route are the departure and arrival airports, a direct flight exists, and no more searching is needed
                    if len(getAP(airports, arr).getRoute())==2:
                        return getAP(airports, arr).getRoute()
                #print(dests[0][0], getAP(airports, dests[0][0]).getRoute())
            
                for type in types:
                    query = "select * from route where r_dep = '{}' and (r_plane IN(SELECT p_iata FROM plane where p_icao = '{}'));".format(dests[0][0], type)
                    #print(query)
                    cursor.execute(query)
                    query = cursor.fetchall()
                    for i in query:
                        if i[3] in dests[0][1]:
                            continue
                        if i[3] in skip:
                            continue
                        if i[3] == arr:
                            dests.insert(1,[i[3], dests[0][1]+[i[3]]])
                        else:
                            dests.append([i[3], dests[0][1]+[i[3]]])
        dests.remove(dests[0])
        if optimal == 999999999999:
            iteration += 1
            #print("Still max", iteration)
            if iteration < 50: #If there is no route found in sorted iterations, the nearest stop is not the best
                dests.sort(key = lambda stop:distance(stop[0], arr))
    
    return getAP(airports, arr).getRoute()


def insert(apList, icao, dep, arr, route, optimal):
    index = find(apList, icao)
    #print(index, len(apList))
    if index < len(apList) and apList[index].getIcao() != icao:
        new = Airport(icao, dep, arr, route)
        if new.getRouteLen() + new.getDistLeft() > optimal:
            return apList
        apList.insert(index, Airport(icao, dep, arr, route))
        return apList
    routeLen = sum(routeLengths(route))
    if index == len(apList):
        apList.append(Airport(icao, dep, arr, route))
    if apList[index].getRouteLen() > routeLen:
        apList[index].setRoute(route, routeLen)
            
    
    return apList



def find(apList, icao):
    #Binary search to find icao in airport list
    high = len(apList) - 1
    mid = 0
    low = 0
    while low <= high:
        mid = (high+low)//2
        
        if apList[mid].getIcao() < icao:
            low = mid + 1
            
        elif apList[mid].getIcao() > icao:
            high = mid - 1
            
        else:
            return mid
    if low > high:
        return low
    else:
        return high
        
def getAP(apList, icao):
    #print("get",icao)
    index = find(apList, icao)
    if index < len(apList) and apList[index].getIcao() != icao:
        return None
    if index >= len(apList):
        return None
    #printList(apList)
    return apList[index]

def printList(hi):
    for i in hi:
        i.apPrint()
    print()

def lastDestKey(route):
    return route[-1][-1]

def getStops(route):
    return 

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

def routeLengths(route):
    if route == []:
        return [9999999999]
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
    if len(result) < 1:
        print(airport,"invalid")
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

""""
current = time()
data = b'{"dep":"bikf","arr":"omdb","fleet":["B752", "A320"], "skipAirports":[]}'
print(routeResponse(data), time()-current)
"""
"""
current = time()
data = b'{"dep":"ENSB","arr":"YMML","fleet":["B752", "A320", "B738", "B77W", "B77L", "A380", "A333", "A332"], "skipAirports":[]}'
resp = loads(routeResponse(data))
print(resp, time()-current)
"""
#print(getLegs(['KIAD', 'BIKF', 'EFHK', 'UUEE', 'USSS', 'ZBAA'], ["B752", "A320"]))

"""
current = time()
data = b'{"dep":"ksfo","arr":"yssy","fleet":["B752"], "skipAirports":[]}'
print(routeResponse(data), time()-current)
"""
"""
current = time()
data = b'{"dep":"klax","arr":"yssy","fleet":["B77W"], "skipAirports":[]}'
print(routeResponse(data), time()-current)
"""
"""
current = time()
data = b'{"dep":"klax","arr":"yssy","fleet":[ "A320", "B752"], "skipAirports":[]}'
print(routeResponse(data), time()-current)
"""

current = time()
data = b'{"dep":"bgBW","arr":"fact","fleet":[ "A320", "B752","DH8A","DH8B","DH8C","DH8D","DH8", "B77W", "B77L", "B738", "B737"], "skipAirports":[]}'
print(routeResponse(data), time()-current)