import sqlite3
import pandas as pd
from readcsv import Readcsv


# create a database connection
class CreateDatabase(Readcsv):
    
    def __init__(self):
        self.conn = sqlite3.connect("TTC_test.db")
        self.cur = self.conn.cursor()

    def create(self, query, table):
        try:
            drop_query = "DROP TABLE "+ table + ";"
            self.cur.execute(drop_query)
            self.cur.execute(query)
        except:
            self.cur.execute(query)
   
    def create_station_table(self):
        query= """CREATE TABLE stations(
                    station_id varchar(255) NOT NULL,
                    next_station varchar(255) NOT NULL ,
                    distance  float(6,2) NOT NULL,
                    line      int(1)   NOT NULL,
                    PRIMARY KEY(station_id)
                    ); """

        self.create(query, "stations")

        stationSpecs = self.read_station_table("NTAS CSS\\StationMap.csv")
        for line in stationSpecs:
            self.cur.execute("""INSERT INTO stations (station_id, next_station, distance, line)  
                        Values(?, ?, ?, ?);""", (line[0], line[3], float(line[4]), int(line[6])))
        self.conn.commit()

    def create_destionation_table(self):
        query = """CREATE TABLE destinations(
                    station_id  CHAR(4) NOT NULL,
                    dest1 CHAR(4) NOT NULL, 
                    dest2 CHAR(4), 
                    dest3 CHAR(4), 
                    FOREIGN KEY(station_id) REFERENCES stations(station_id)
                    ); """

        self.create(query, "destinations")

        stationSpecs = self.read_station_table("NTAS CSS//StationMap.csv")

        for data in stationSpecs:
            station_id = data[0].strip()
            dest1 = data[9].strip()
            dest2 = data[10].strip()
            dest3 = data[11].strip()
            self.cur.execute("INSERT INTO destinations VALUES(?,?,?,?);", (station_id, dest1, dest2, dest3))
        self.conn.commit()

    def create_avgpredict_table(self):
        query = """CREATE TABLE predictions(
                    id CHAR(11) NOT NULL,
                    station_id  CHAR(4) NOT NULL,
                    dest CHAR(4) NOT NULL,
                    hour  int(1),
                    avg_time VARCHAR(255),
                    PRIMARY KEY(id),
                    FOREIGN KEY(station_id) REFERENCES stations(station_id)
                    ); """

        self.create(query, "predictions")

    def update_avgpredict(self, hour: int, predict: dict) -> None:
        "NOT PROTECTED AGAINST SQL INJECTION"
        for station_id in predict:
            for dest in station_id:
                _id = station_id + '|' + dest + '|' + hour
                time = predict[station_id][dest].avg
                query = "REPLACE INTO predictions VALUES {}, {}, {}, {}, {}".format(_id, station_id, dest, hour, time)
                query = query.strip(';') + ";"
                self.cur.execute(query)

    
    def set_avgpredict(self, hour: int, predict: dict) -> None:
        query = """SELECT station_id, dest, avg_time 
                FROM predictions 
                WHERE hour = {} ;
                """.format(hour)
        tuples = self.cur.execute(query)

        if tuples.arraysize < len(predict.keys()):
            #reset pedict
            pass
        else:
            for _tuple in tuples:
                predict[_tuple[0]][_tuple[1]] = _tuple[2] #turn this into a datetime object

    
    def create_track_table(self):
        query = """CREATE TABLE track_data(
                    track_id VARCHAR(255) NOT NULL, 
                    station_id  VARCHAR(255),  
                    FOREIGN KEY(station_id) REFERENCES stations(station_id)
                    ); """
        self.create(query, "track_data")

        stationSpecs = self.read_station_table("NTAS CSS//TrackCircuitMap.csv")
        for data in stationSpecs:
            track_id = data[0]
            station_id = data[5]
            isRevenue = True if data[11] == "1" else False
            isStation = True if data[6] == "0" else False
            if isRevenue and isStation:
                self.cur.execute("INSERT INTO track_data VALUES(?,?);", (track_id, station_id))

        self.conn.commit()

    def print_table(self, table_name):
        print(pd.read_sql_query("SELECT * FROM {};".format(table_name), self.conn))

    def select(self, query_string):
        return self.cur.execute(query_string)

    def close(self):
        self.conn.close()


if __name__ == "__main__" :
    mydb = CreateDatabase()
    mydb.create_station_table()
    #CreateDatabase.create_track_table()
    mydb.create_destionation_table()
    mydb.create_avgpredict_table()

    mydb.print_table("stations")
    mydb.print_table("destinations")
    mydb.print_table("predictions")

    mydb.close()






