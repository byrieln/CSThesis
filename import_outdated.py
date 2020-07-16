import mysql.connector

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()


with open("data/airports.dat", "r", encoding="utf8") as file:
    for line in file:
        print (line)
        airport = line.split(',')
        query = "INSERT INTO airport VALUES("
        for i in range(10):
            if airport[i] == '\\N':
                airport[i] = 'NULL'
            query += '{}, '.format(airport[i])
        if airport[10] == '\\N':
            airport[10] = 'NULL'
        query += '{});'.format(airport[10])
        print (query)
        try:
            cursor.execute(query)
        except mysql.connector.DataError:
            db.close()
            break
        #cursor.execute("INSERT INTO airport VALUES({},{},{},{},{},{},{},{},{},{},{})".format())
db.commit()


with open("data/airlines.dat", "r", encoding="utf8") as file:
    for line in file: 
        print (line)
        airline = line.split(',')
        query = "INSERT INTO airline VALUES("
        if airline[6] == airline[6].upper():
            airline[5], airline[6] = airline[6], airline[5]
        for i in range(7):
            if airline[i] == '""' or airline[i] == '\\N':
                airline[i] = 'NULL'
            query += '{}, '.format(airline[i])
        if 'Y' in airline[7]:
            airline[7] = "true"
        else:
            airline[7] = "false"
        query += '{});'.format(airline[7])
        print(query)
        cursor.execute(query)
db.commit()


with open("data/planes.dat", "r", encoding='utf8') as file:
    j = 0
    for line in file:
        print(line)
        airplane = line.split(',')
        print (airplane)
        for i in range(len(airplane)):
            if  '\\N' in airplane[i]:
                if i == 1:
                    airplane[i] = '"NUL"'
                else:
                    airplane[i] = 'NULL'
        query = "INSERT INTO airplane VALUES({} ,{},{},{});".format(j, airplane[0], airplane[1], airplane[2])
        print(query)
        cursor.execute(query)
        j+=1


with open("data/routes.dat", 'r', encoding='utf8') as file:
    j = 0
    for line in file:
        route = line[:-1].split(',')
        if route[1] == '\\N' or route[3] == '\\N' or route[5] == '\\N':
            print('AH')
            continue
        if 'Y' in route[6]:
            route[6] = 'true'
        else:
            route[6] = 'false'
        for i in route[8].split(' '):
            cursor.execute("SELECT * FROM airport WHERE a_id = {} OR a_id = {};".format(route[3], route[5]))
            if len(cursor.fetchall()) < 2:
                continue
            query = "INSERT INTO route VALUES({}, {}, {}, {}, {}, '{}');".format(j, route[1], route[3], route[5], route[6], i)
            print(query)
            cursor.execute(query)
            j+=1
        
        
          


print("FUUUUUUUCK")
db.commit()
db.close()