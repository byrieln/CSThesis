"""
Example script that scrapes data from the IEM ASOS download service
"""
from __future__ import print_function
import json
import time
import datetime

# Python 2 and 3: alternative 4
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

# Number of attempts to download data
MAX_ATTEMPTS = 6
# HTTPS here can be problematic for installs that don't have Lets Encrypt CA
SERVICE = "http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"


def download_data(uri):
    """Fetch the data from the IEM

    The IEM download service has some protections in place to keep the number
    of inbound requests in check.  This function implements an exponential
    backoff to keep individual downloads from erroring.

    Args:
      uri (string): URL to fetch

    Returns:
      string data
    """
    attempt = 0
    while attempt < MAX_ATTEMPTS:
        try:
            data = urlopen(uri, timeout=300).read().decode("utf-8")
            if data is not None and not data.startswith("ERROR"):
                return data
        except Exception as exp:
            print("download_data(%s) failed with %s" % (uri, exp))
            time.sleep(5)
        attempt += 1

    print("Exhausted attempts to download, returning empty data")
    return ""


def get_stations_from_filelist(filename):
    """Build a listing of stations from a simple file listing the stations.

    The file should simply have one station per line.
    """
    stations = []
    for line in open(filename):
        stations.append(line.strip())
    return stations


def get_stations_from_networks():
    """Build a station list by using a bunch of IEM networks."""
    stations = []
    states = """AK AL AR AZ CA CO CT DE FL GA HI IA ID IL IN KS KY LA MA MD ME
     MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT
     WA WI WV WY"""
    # IEM quirk to have Iowa AWOS sites in its own labeled network
    networks = ["AWOS"]
    for state in states.split():
        networks.append("%s_ASOS" % (state,))

    for network in networks:
        # Get metadata
        uri = (
            "https://mesonet.agron.iastate.edu/geojson/network/%s.geojson"
        ) % (network,)
        data = urlopen(uri)
        jdict = json.load(data)
        for site in jdict["features"]:
            stations.append(site["properties"]["sid"])
    return stations


def download_alldata():
    """An alternative method that fetches all available data.

    Service supports up to 24 hours worth of data at a time."""
    # timestamps in UTC to request data for
    startts = datetime.datetime(2012, 8, 1)
    endts = datetime.datetime(2012, 9, 1)
    interval = datetime.timedelta(hours=24)

    service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

    now = startts
    while now < endts:
        thisurl = service
        thisurl += now.strftime("year1=%Y&month1=%m&day1=%d&")
        thisurl += (now + interval).strftime("year2=%Y&month2=%m&day2=%d&")
        print("Downloading: %s" % (now,))
        data = download_data(thisurl)
        outfn = "%s.txt" % (now.strftime("%Y%m%d"),)
        with open(outfn, "w") as fh:
            fh.write(data)
        now += interval

def getWX(station, date):
    """Our main method"""
    # timestamps in UTC to request data for
    
    #ts = date.split('-')

    service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

    service += date.strftime("year1=%Y&month1=%m&day1=%d&")
    """
    adding 2 days to the date range also gets the following day
    This is required due to the UTC to local time conversion
    Don't need preceding day, because all locations are in the US, all behind UTC
    """
    service += (date + datetime.timedelta(days=2)).strftime("year2=%Y&month2=%m&day2=%d&")

    # Two examples of how to specify a list of stations
    #print(type(airports)
    # stations = get_stations_from_filelist("mystations.txt")

    uri = "%s&station=%s" % (service, station)
    #print(uri)
    print("Downloading: %s" % (station,), end = " ")
    data = download_data(uri)
    #print(" Got Data")
    print('')
    #print(data)
    return format(data)

def makeTimestamp(year, month, day, time):
    #Takes the time and date given by the dataset and converts it to UTC timestamp (denoted as 'Z' in aviation)
    #Copied here so I dont have to rewrite it
    div = time//100
    mod = time % 100
    if div > 23 or div < 0 or mod > 59 or mod < 0:
        return None
    return  datetime.datetime.strptime('{}-{}-{} {}:{}'.format(year, month, day, div, mod), '%Y-%m-%d %H:%M')

def getMonthlyWX(station, date):
    dayOfMonth = date.day
    
    fromdate = date - datetime.timedelta(days=dayOfMonth)
    todate = fromdate + datetime.timedelta(days=31)
        
    return getWXRange(fromdate, todate, station)

def getFullWX(station):
    #gets full weather between October 2008 and May 2020
    #More wiggle room than necessary added for timezone differences
    fromDate = makeTimestamp(2008, 9, 1, 0000)
    toDate = makeTimestamp(2020, 6, 2, 0000)
    
    return getWXRange(fromDate, toDate, station)

def getWXRange(startDate, endDate, airports):
    """Our main method"""
    # timestamps in UTC to request data for
    
    startts = startDate
    #y, m, d = tuple(endDate)
    endts = endDate

    service = SERVICE + "data=all&tz=Etc/UTC&format=comma&latlon=yes&"

    service += startts.strftime("year1=%Y&month1=%m&day1=%d&")
    service += endts.strftime("year2=%Y&month2=%m&day2=%d&")

    # Two examples of how to specify a list of stations
    #print(type(airports))
    if type(airports) != list:
        airports = [airports]
    stations = airports
    output = []
    # stations = get_stations_from_filelist("mystations.txt")
    for station in stations:
        uri = "%s&station=%s" % (service, station)
        print("Downloading: %s" % (station,), end = " ")
        data = download_data(uri)
        #print(" Got Data")
        output.append(data)
    
    return format(output)
    

def format(raw):
    """
    format the output to easily parallelize into spark
    """
    output = []
    if type(raw)== str:
        raw = [raw]
    for i in raw:
        output = output + i[i.find('station'):].split('\n')[:-1]
    for i in range(len(output)):
        output[i] = tuple(output[i].split(','))
    return output

if __name__ == "__main__":
    #    download_alldata()
    getWX( (2019, 9, 1), (2019, 9, 1), ['AVP'])
