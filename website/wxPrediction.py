#import findspark
#findspark.init('/opt/spark')

#from pyspark.sql import SparkSession

import re
from requests import get

#"""
import findspark
findspark.init('/opt/spark')

from pyspark.sql import SparkSession, Row
spark = SparkSession.builder.appName('delay_predictions').getOrCreate()

data = spark.read.csv('final_2020_*.csv', header=True, inferSchema=True)

from pyspark.ml.feature import StringIndexer, OneHotEncoder

cloudIndex = StringIndexer(inputCol='cloudCoverage', outputCol='cloudIndex')
cloudOnehot = StringIndexer(inputCol='cloudIndex', outputCol='cloudOnehot')
weatherIndex = StringIndexer(inputCol='weather', outputCol='weatherIndex')
weatherOnehot = StringIndexer(inputCol='weatherIndex', outputCol='weatherOnehot')

cloudIDX = cloudIndex.fit(data)
data = cloudIDX.transform(data)

cloudOHE = cloudOnehot.fit(data)
data = cloudOHE.transform(data)

weatherIDX = weatherIndex.fit(data)
data = weatherIDX.transform(data)

weatherOHE = weatherOnehot.fit(data)
data = weatherOHE.transform(data)

weatherOptions = data.groupBy('weather').count().collect()

from pyspark.ml.feature import VectorAssembler

assembler = VectorAssembler(inputCols=[
    'temp',
    'dewpoint',
    'wind',
    'precip',
    'alti',
    'vis',
    'cloudOnehot',
    'cloudAlt',
    'weatherOnehot',
    'ice'
], outputCol='features')

data = assembler.transform(data)

ml = data.select(['ArrDelayMinutes',
     'Diverted',
     'Cancelled',
     'WeatherDelay',
     'features'])

from pyspark.sql.functions import udf
from pyspark.sql.types import DoubleType

dones = ml.filter(ml['Diverted'] == 1).count()
dzeros = ml.filter(ml['Diverted'] == 0).count()

divertWeights = udf(lambda x: dzeros/(dones+dzeros) if x == 1.0 else dones/(dones+dzeros), DoubleType())
ml = ml.withColumn('divertWeight', divertWeights(ml['Diverted']))

cones = ml.filter(ml['Cancelled'] == 1).count()
czeros = ml.filter(ml['Cancelled'] == 0).count()

cancelWeights = udf(lambda x: czeros/(cones+czeros) if x == 1.0 else cones/(cones+czeros), DoubleType())
ml = ml.withColumn('cancelWeight', divertWeights(ml['Cancelled']))

isWxDelay = udf(lambda x: 0.0 if x == 0.0 else 1.0, DoubleType())
ml = ml.withColumn('hasWXDelay', isWxDelay(ml['WeatherDelay']))

cancelWeights = udf(lambda x: wzeros/(wones+wzeros) if x == 1.0 else wones/(wones+wzeros), DoubleType())
ml = ml.withColumn('wxdWeight', divertWeights(ml['hasWXDelay']))

wones = ml.filter(ml['hasWXDelay'] == 1).count()
wzeros = ml.filter(ml['hasWXDelay'] == 0).count()

delayWeights = udf(lambda x: wzeros/(wones+wzeros) if x == 1.0 else wones/(wones+wzeros), DoubleType())
ml = ml.withColumn('wxdWeight', divertWeights(ml['hasWXDelay']))

train, test = ml.randomSplit([0.7, 0.3], seed=101)
from pyspark.ml.classification import LogisticRegression

divertLR = LogisticRegression(featuresCol='features', labelCol='Diverted', weightCol='divertWeight', predictionCol='divertPrediction',  rawPredictionCol='divertRaw', probabilityCol = 'divertProb')
divertModel = divertLR.fit(train)

from pyspark.ml.classification import RandomForestClassifier
delayForest = RandomForestClassifier(labelCol='hasWXDelay', weightCol='wxdWeight', maxBins = 100, predictionCol='delayPrediction', rawPredictionCol='delayRaw', probabilityCol = 'delayProb')
delayModel = delayForest.fit(train)

from pyspark.ml.classification import GBTClassifier
cancelGBT = GBTClassifier(labelCol='Cancelled', weightCol='cancelWeight', maxBins = 100, predictionCol='cancelPrediction')
cancelModel = cancelGBT.fit(train)
#"""
print('Training Complete')

#-SHSN DRSN
#BKN018CB 

def getPredictions(route):
    #print(route)
    results = getWeather(route)
    wx = []
    for i in results:
        wx.append(metarToDict(i))
    
    wx = [x for x in wx if x != None]
    for i in wx:
        print(i)
    
    out = {}
    
    out['delay'], out['cancel'], out['divert'] = predict(wx)
    return out
    
def predict(metar):
    df = spark.createDataFrame([Row(**i) for i in metar])
    
    #print(df.columns)
    

    
    df = cloudIDX.transform(df)
    #print(df.columns)
    df = cloudOHE.transform(df)
    df = weatherIDX.transform(df)
    df = weatherOHE.transform(df)
    
    df = assembler.transform(df)
    
    ml = df.select(['airport',
     'features'])
    
    ml = divertModel.transform(ml)
    ml = cancelModel.transform(ml)
    ml = delayModel.transform(ml)
    
    res = ml.collect()
    delays = [x['airport'] for x in res if x['delayPrediction'] == 1]
    cancels = [x['airport'] for x in res if x['cancelPrediction'] == 1]
    diversions = [x['airport'] for x in res if x['divertPrediction'] == 1]
    return delays, cancels, diversions

def metarToDict(wx):
    if wx == 'No METAR found':
        return None
    parsed = {}
    
    wx = wx.split(' ') #Ignore the airport identifier and time
    
    parsed['airport'] = wx[0]
    
    wx = cleanWX(wx)
    
    wx, parsed['wind'] = getWind(wx)
    
    wx, parsed['cloudCoverage'], parsed['cloudAlt'] = getCloud(wx)
    
    wx, parsed['vis'] = getVis(wx)
    
    wx, parsed['alti'] = getAltimeter(wx)
    
    wx, parsed['temp'], parsed['dewpoint'] = getTemp(wx)
    
    parsed['ice'] = 0
    parsed['precip'] = 0
    
    if len(wx) > 0:  
        parsed['weather'] = ' '.join(wx)
    else:
        parsed['weather'] = '0'
    
    weather = '0'
    for i in weatherOptions:
        if i['weather'] == parsed['weather']:
            weather = parsed['weather']
            break
    parsed['weather'] = weather
    
    return parsed

def getTemp(wx):
    for i in range(len(wx)):
        if re.match('^M?\d\d\/M?\d\d$', wx[i]):#matches (M?) 2 digits/(M?) 2 digits
            temp, dew = wx[i].split('/')
            if temp[0] == 'M':
                temp = int(temp[1:]) * -1
            if dew[0] == 'M':
                dew = int(dew[1:]) * -1    
            return wx[:i]+wx[i+1:], round(CtoF(temp), 2), round(CtoF(dew), 2) #training dataset is in fahrenheit even though it is never used in aviation...
            
def CtoF(temp):
    temp = int(temp) * 9 / 5 
    return float(temp + 32)

def getAltimeter(wx):
    for i in range(len(wx)):
        if re.match('^[A,Q]\d{4}$', wx[i]):
            if 'Q' in wx[i]:
                wx[i] = round(int(wx[i][1:]) / 33.8639,2)
            else:
                wx[i] = float(wx[i][1:])/100
            return wx[:i]+wx[i+1:], float(wx[i])

def getVis(wx):
    for i in range(len(wx)):
        if wx[i] == 'CAVOK':
            return wx[:i]+wx[i+1:], 10.0
        elif re.match('^\d{4}$', wx[i]):#four digits in a row
            if wx[i] == '9999':
                return wx[:i]+wx[i+1:], 10.0
            return wx[:i]+wx[i+1:], metersToSM(wx[i])
        elif 'SM' in wx[i]:
            if '/' in wx[i]:
                #print(wx[i])
                wx[i] = int(wx[i][0]) / int(wx[i][2])
                if i != 0:
                    wx[i] += int(wx[i-1])
                    return wx[:i-1]+wx[i+1:], float(wx[i])
            else:
                wx[i] = int(wx[i][:-2])
            return wx[:i]+wx[i+1:], float(wx[i])
    return wx, 10.0
            
            
def metersToSM(km):
    #meters to statute miles
    return int(km)/1609
    
    

def cleanWX(wx):
    wx = wx[2:]
    if wx[0] == 'AUTO':
        wx = wx[1:]
    
    for i in wx:
        if re.match('\d{3}V\d{3}', i):#3 digits 'V' 3 digits
            wx.remove(i)
    
    for i in range(len(wx)):
        if wx[i] == 'NOSIG' or wx[i] == 'RMK' or wx[i] == 'TEMPO' or wx[i] == 'BECMG':
            return wx[:i]
    return wx

def getCloud(wx):
    #print(wx)
    clouds = []
    cloudWords = ['CLR', 'FEW', 'SCT', 'BKN', 'OVC', 'VV']
    clearWords =  ['SKC', 'NCD', 'NSC']
    for i in wx:
        for j in cloudWords+clearWords:
            if j in i:
                clouds.append(i)
    
    
    for i in clouds:
        wx.remove(i)
    if len(clouds) == 0:
        return wx, '0', 0.0
    if clouds[0] =='CLR':
        return wx, 'CLR', 0.0
    for i in clearWords:
        if clouds[0] == i:
            return wx, 'CLR', 0.0
    if 'CB' in clouds[0]:
        clouds[0] = clouds[0][:-2]
    if 'VV' not in clouds[0]:
        clouds[0] = (clouds[0][:3], int(clouds[0][3:]))
    else:
        clouds[0] = (clouds[0][:2], int(clouds[0][2:]))
        
    return wx, clouds[0][0], clouds[0][1]*100.0
        
        
    

def getWind(wx):
    #Find which element is wind, if any
    for i in range(len(wx)):
        #Identify if unit is knots or meters per second
        #The letters at the end of the wind element identify unit, KT for knots, MPS for meters persecond
        if 'VRB' in wx[i]:
            return wx, 0
        if 'KT' in wx[i]:
            #Wind format: 00000KT
            #First 3 numbers: compass direction
            #Next 2 numbers: speed in knots
            #Final 2 are unit identifier
            return wx[:i] + wx[i+1:], int(wx[i][3:5])
        elif 'MPS' in wx[i]:
            #Wind format: 00000MPS
            #First 3 numbers: compass direction
            #Next 2 numbers: speed in knots
            #Final 3 are unit identifier
            return wx[:i] + wx[i+1:], int(mpsToKT(wx[i][3:5]))
    return wx, 0
    
def mpsToKT(mps):
    return round(int(mps) * 1.94384)

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

print(getPredictions(['BIKF', 'YSSY', 'PHNL', 'KMGW', 'ZBAA', 'UUSS', 'ZMUB', 'KJFK', 'KHZL']))

#print(metarToDict('PHNL 012153Z 16009KT 10SM FEW025 FEW035 27/18 A3001 RMK AO2 SLP160 T02670178'))
#print(metarToDict('ZBAA 012200Z 02003MPS 360V060 CAVOK M02/M11 Q1035 NOSIG'))
#print(metarToDict('KHZL 012235Z AUTO 23007KT 200V270 4SM -SN BKN012 BKN019 OVC031 00/M03 A2966 RMK AO2'))
#print(metarToDict('KMGW 020121Z 22006KT 1 1/4SM -SN BR BKN008 OVC011 M01/M03 A2991 RMK AO2 P0001 T10111028'))
#print(metarToDict(