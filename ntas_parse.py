import os
from DataBaseReader import CreateDatabase
from StationOrder import StationOrder
from ntas_obj import Ntas_Plist
import math
from zipfile import ZipFile


class ParseNtasLogs(CreateDatabase):
    test_station = "OML2"
    
    def __init__(self):
        self.predict = dict()         ##2D dictionary, key1 --> station_name; key2 --> prediction object
        self.predict_temp = dict()    ##2D dictionary, key1 --> station_name; key2 --> prediction object
        super().__init__()

    def read_zipfolder(self, dir1):
        zipped_files, filenames = ParseNtasLogs.read_zip_folder(dir1)
        for name in filenames:
            file = zipped_files.open(name, 'r')
            self.__read_file(file)
            file.close()

    def read_folder(self, dir1):
        filenames = os.listdir(dir1) #4 zip files
        for name in filenames:
            file = open(name)
            self.__read_file(file)
            file.close()

    def __read_file(self, file):
        next_station = dict()
        for line in file:
            travel_info = ParseNtasLogs.string_to_dict(str(line))
            self.__remove_duplicate_predictions(next_station, travel_info)
        for key in next_station.keys():
            self. __read_line(next_station[key])

    def __remove_duplicate_predictions(self, dictstation, travel_info):
        station_id = travel_info["stationId"]
        time_string = travel_info['timeString']
        if station_id not in dictstation.keys():
            dictstation[station_id] = travel_info
        elif float(dictstation[station_id]['timeString']) > float(time_string):
            dictstation[station_id]['timeString'] = time_string

    def __read_line(self, travel_info):
        station_id = travel_info["stationId"]
        arriving_in = math.ceil(float(travel_info['timeString']))
        last_index, last_predict = self.___find_last_temp_predict(travel_info, station_id, arriving_in)
        if last_predict is None or last_index == -1:
            return

        NTAS_obj = Ntas_Plist(travel_info, arriving_in)

        if last_predict.train_num != NTAS_obj.train_num:
            self.predict_temp[station_id] = [NTAS_obj]
        elif abs((NTAS_obj.date_obj - last_predict.date_obj).total_seconds()) > 1800:
            self.predict_temp[station_id] = [NTAS_obj]
        elif arriving_in == 0:
            self.__set_prediction_on_arrival(NTAS_obj, station_id)
            self.predict_temp[station_id] = []
        else:
            self.predict_temp[station_id].append(NTAS_obj)

    def ___find_last_temp_predict(self, travel_info, station_id, arriving_in):
        try:
            last_index = len(self.predict_temp[station_id]) - 1
        except KeyError:
            NTAS_obj = Ntas_Plist(travel_info, arriving_in)
            self.predict[station_id] = dict()
            self.predict_temp[station_id] = [NTAS_obj]

            return -1, None
        try:
            last_predict = self.predict_temp[station_id][last_index]
        except IndexError:
            if arriving_in > 0:
                NTAS_obj = Ntas_Plist(travel_info, arriving_in)
                self.predict_temp[station_id] = [NTAS_obj]
            return -1, None

        if arriving_in == last_predict.arriving_in:
            return -1, None
        else:
            return last_index, last_predict

        
    def __set_prediction_on_arrival(self, NTAS_arrival, station_id):
        arrival_datetime = NTAS_arrival.date_obj
        for NTAS_prediction in self.predict_temp[station_id]:
            NTAS_prediction.set_travel(arrival_datetime)
            time_predicted = round(NTAS_prediction.prediction)
            self.__set_predict(station_id, time_predicted, NTAS_prediction)
            if ParseNtasLogs.test_station in station_id:
                print(NTAS_prediction.__str__())

    def __set_predict(self, station, time_predicted, NTAS_prediction):
        try:
            self.predict[station][time_predicted].append(NTAS_prediction)
        except KeyError:
            self.predict[station][time_predicted] = [NTAS_prediction]


    @staticmethod
    def read_zip_folder(dir1='NTAS_LOGS_TEST'):
        zipfile = ZipFile(dir1, 'r')
        folder = zipfile.namelist()
        folder.sort()
        return zipfile, folder




    @staticmethod
    def string_to_dict(line: str):
        line = line.strip("b'").strip("\\r\\n").strip("NTASData").strip() \
            .replace("[", "{\'").replace("]", "\'}") \
            .replace("=", "\':\'") \
            .replace(", ", "', '")
        travel_info = eval(line)
        return travel_info

    def create_NTASlogP_table(self):
        query = """CREATE TABLE NTAS_logsP
                            (
                            stationId char(4) , 
                            trainId   int, 
                            datetime VARCHAR(255),
                            timestring     float(4,2),
                            status          char(1),
                            prediction_error  float(4,2)
                            );          
                        """
        # super().create(query, "NTAS_logsP")  #  .__create(query, "NTAS_logsP")

        # tuples = self.cur.execute("SELECT * from NTAS_logsP").fetchall()
        # print(tuples)

    # NOT IN USE
    # Method is used to check if a prediction is being generated for a station after the destination
    # This would limit the number of trains that go out of service
    @staticmethod
    def is_destination_upcoming(current_station, end_station):
        next_station = StationOrder.get_next(current_station)
        while ("TERM" not in next_station):
            if next_station == end_station:
                return True
            next_station = StationOrder.get_next(next_station)
        return False

    def __populate_table(self):
        for station in self.predict.keys():
            for train in self.predict[station]:
                self.cur.execute("""INSERT INTO NTAS_logsP
                               (stationId, trainId, datetime, timestring, status, prediction_error)
                                VALUES (?,?,?,?,?,?)""",(station, int(train.train_num), train.date_str, train.f_prediction,
                                                       train.arriving_in, train.prediction_error))

        self.conn.commit()