import mysql.connector

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()




"""with open("data/airports.dat", "r", encoding="utf8") as file:
    #add_order = [5, 4, 1, 2, 3, ]
    for line in file:
        k = 0
        print(line)
        #Some airports have a "," within data fields. This if statement erases stray commas so those lines can be used like the others.
        if len(line.split(",")) == 15:
            temp = line.split("\"")
            #print(temp)
            for i in range(len(temp)):
                #Data fiends with commas, if there is no comma in the last spot, are incorrect. Tromso is the exception. 
                if (("," in temp[i]) and (temp[i][-1] != ",")) or temp[i] == "Tromsø Airport,":
                    new = ""
                    for char in temp[i]:
                        if char != ",":
                            new += char
                    temp[i] = new
            line = "\"".join(temp)
        airport = line.split(",")
        query = "INSERT INTO AIRPORT VALUES("
"""
            #Query Structure:
             #   	a_name varchar(128),
             #       a_city varchar(64),
             #       a_country varchar(64),
             #       a_iata char(3),
             #       a_icao char(4) primary key,
             #       a_lat double,
             #       a_long double,
             #       a_alt smallint,
             #       a_timezone float,
             #       a_dst char(1)
"""
        #One airport in the database has both a null ICAO and IATA code, so it is omitted
        if airport[5] == '\\N':
            continue
        for i in range(1,10):
            if airport[i] == '\\N':
                airport[i] = 'NULL'
            query += '{}, '.format(airport[i])
        if airport[10] == '\\N':
            airport[10] = 'NULL'
        query += '{});'.format(airport[10])
        
        try:
            print(line)
            print(query)
            cursor.execute(query)
        except mysql.connector.DataError:
            db.close()
            print("FAILED: ", query)
            break
db.commit()



with open("data/airlines.dat", "r", encoding="utf8") as file:
    for line in file: 
        print(line)
        airline = line.split(',')
        query = "INSERT INTO airline VALUES("
        print(airline[4])
        if airline[4] == "\"N/A\"":
            print ("fail", line)
            continue
        if airline[6] == airline[6].upper():
            airline[5], airline[6] = airline[6], airline[5]
        for i in range(1,7):
            if airline[i] == '""' or airline[i] == '\\N' or airline[i] == '"N/A"':
                airline[i] = 'NULL'
            query += '{}, '.format(airline[i])
        if 'Y' in airline[7]:
            airline[7] = "true"
        else:
            continue
            airline[7] = "false"
        if airline[4] == 'NULL':
            continue
        query += '{});'.format(airline[7])
        try:
            print(query)
            cursor.execute(query)
        except mysql.connector.IntegrityError:
            print("Failed:", query)
            continue
db.commit()    
"""
"""
with open("data/planes.dat", "r", encoding='utf8') as file:
    #j = 0
    for line in file:
        print(line)
        airplane = line.split(',')
        print (airplane)
        for i in range(len(airplane)):
            if  '\\N' in airplane[i]:
                if i == 1:
                    airplane[i] = 'NULL'
                else:
                    airplane[i] = 'NULL'
        if airplane[2] == 'NULL':
            airplane[2] = airplane[1] + '"'
        query = "INSERT INTO airplane VALUES({},{},{});".format(airplane[0], airplane[1], airplane[2][:-1])
        try:
            print(query)
            cursor.execute(query)
        except mysql.connector.IntegrityError:
            print("Failed:", query)
            continue
        #j+=1
db.commit()
"""
with open("data/planes.html", "r", encoding='utf8') as file:
    every = file.read().split('<tr>')
    airplane = ['','','']
    for line in every[2:]: 
        #print(line)
        line = line.split('>')
        #print(line)
        #print(line[6])
        airplane[0] = line[1][:line[1].find('<')]
        airplane[1] = line[3][:line[3].find('<')]
        if airplane[0] == 'A337' and airplane[1] == '':#Airpalne[1] is to future proof this slightly
            airplane[2] = line[14][:line[14].find('<')]
        elif airplane[0] == 'E75S/L': #Exception: Embraer 175
            airplane[0] = 'E170'
        else:
            airplane[2] = line[6][:line[6].find('<')]
        
        if airplane[1] == '"N/A"' or airplane[1] == '':
            airplane[1] = 'NUL'
        if '"' in airplane[2]:
            temp = ''
            for char in airplane[2]:
                if char != '"':
                    temp += char
            airplane[2] = temp
        print(airplane)
        query = 'INSERT INTO plane VALUES("{}", "{}", "{}");'.format(airplane[0], airplane[1], airplane[2])
        try:
            print(query)
            cursor.execute(query)
        except mysql.connector.IntegrityError:
            print("Failed:", query)
            continue

print("FUUUUUUUCK")
db.commit()
db.close()