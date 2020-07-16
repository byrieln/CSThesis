import mysql.connector

db = mysql.connector.connect(database='routegen', user='routegen', password='easyPw123', host='127.0.0.1')
cursor = db.cursor()


mini = 99
maxi = 0


with open("data/airports.dat", "r", encoding="utf8") as file:
    for line in file:
        if length == 15:
            print(line)
print(mini, maxi)
    
"""for line in file:
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
            break"""
        #cursor.execute("INSERT INTO airport VALUES({},{},{},{},{},{},{},{},{},{},{})".format())
db.commit()


print("FUUUUUUUCK")
db.commit()
db.close()