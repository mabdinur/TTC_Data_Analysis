import os, errno
from DataBaseReader import CreateDatabase
from StationOrder import StationOrder
import matplotlib.pyplot as plt
import numpy as np
from queue import Queue
from ntas_obj import Ntas_Plist
from collections import OrderedDict
import csv
import zipfile

class NtasLogs(CreateDatabase):

    predict = dict()
    test_station = "OML2"
    
    def __init__(self):
        super().__init__()

    def create_NTASlogP_table(self):
        query = """CREATE TABLE NTAS_logsP
                            (
                            stationId char(4) , 
                            trainId   int, 
                            datetime VARCHAR(255),
                            timestring     float(4,2),
                            status          char(1),
                            percent_error  float(4,2)
                            );          
                        """
        #super().create(query, "NTAS_logsP")  #  .__create(query, "NTAS_logsP")

        #tuples = self.cur.execute("SELECT * from NTAS_logsP").fetchall()
        #print(tuples)

        self.__read_folder("D:\\NTAS_Log-Sun-0917-1\\NTAS_Log")
        self.__read_folder("NTAS_Log") #"D:\\NTAS_Log-Sun_0917-2
        self.__read_folder("D:\\NTAS_Log-Sun-1105-1\\NTAS_Log")
        self.__read_folder("D:\\NTAS_Log-Sun-1105-2\\NTAS_Log")
        #   self.__populate_table()
        #self.__test_print()
        self.test_all_stations()


    def __test_print(self, outputfile="graph-data-2.csv", day="SUN-"):
        myfile = open(day + outputfile, 'w', newline="" )
        wr = csv.writer(myfile)
        wr.writerow(["Station", "Prediction(minutes)", "Avg Error(Actual - Prediction)", "Standard Deviation", "List of Error values"])

        #for obj in NtasLogs.predict[self.test_station]:
        index = 0
        for key in NtasLogs.predict.keys():
            print(key)
            errors = OrderedDict([(i, list()) for i in range(30)])
            avg = OrderedDict()
            standard_deviation = list()
            for obj in NtasLogs.predict[key]:
                if round(obj.f_prediction) != 0 :
                    key_p = round(obj.f_prediction)
                    value = obj.percent_error
                    if key_p not in errors.keys():
                        errors[key_p] = [value]
                    else:
                        errors[key_p].append(value)

            avg, standard_deviation = self.__mean__sdeviation(errors)
            k = 0
            for all_keys in avg.keys():
                wr.writerow([key, all_keys, avg[all_keys], standard_deviation[k], errors[all_keys]])
                print(all_keys, avg[all_keys], errors[all_keys] )
                k += 1

            self.create_graph(avg, standard_deviation, index, key, day)
            index += 1


    def test_all_stations(self, outputfile="graph-data-2.csv", day="SUN-"):
        myfile = open(day + outputfile, 'a', newline="" )
        wr = csv.writer(myfile)

        errors = OrderedDict([(i, list()) for i in range(30)])
        avg = OrderedDict()
        standard_deviation = list()

        for key in NtasLogs.predict.keys():
            print(key)
            for obj in NtasLogs.predict[key]:
                if round(obj.f_prediction) != 0 :
                    key_p = round(obj.f_prediction)
                    value = obj.percent_error
                    if key_p not in errors.keys():
                        errors[key_p] = [value]
                    else:
                        errors[key_p].append(value)

        avg, standard_deviation = self.__mean__sdeviation(errors)
        k = 0
        for all_keys in avg.keys():
            wr.writerow("ALL Stations", all_keys, avg[all_keys], standard_deviation[k], errors[all_keys])
            print(all_keys, avg[all_keys], errors[all_keys] )
            k += 1

        self.create_graph(avg, standard_deviation, 0, "ALL", day)


    def create_graph(self, avg, standard_deviation, index, key, day ):
        if len(avg) > 0:
            x, y = zip(*avg.items())
            fig = plt.figure(index)
            plt.errorbar(x, y, yerr=standard_deviation, fmt='none', ecolor='r')
            plt.scatter(x, y)
            plt.xlabel("Arrival Time Prediction(rounded to nearest Minute)")
            plt.ylabel("Prediction Error (Actual - Expected)")
            plt.title(key)
            fig.canvas.set_window_title("Sunday Morning Arrival Predictions (10AM to 1PM)")

            fig.savefig(day + "Station_figures//" + "Station__" + key)
            print(index)
    def __read_folder(self, dir):

        list_files = os.listdir(dir) #4 zip files
        for file in list_files:
            self.__read_file((dir + "\\" + file))
    
    def __mean__sdeviation(self, errors):
        avg = OrderedDict()
        sd = list()
        for key in errors.keys():
            if (len(errors[key]) > 0):
                mean = (sum(errors[key]))/len(errors[key])
                avg[key] = mean
                squared_sums = 0.0
                for x in errors[key]:
                    squared_sums += (x - mean) ** 2
                sd.append((squared_sums / len(errors[key])) ** (1 / 2))
        return avg,sd


    def __read_file(self, file):
        file_temp = open(file)
        next_train = dict()
        for line in file_temp:
            traval_info = NtasLogs.string_to_dict(line)
            self.__find_predictions(next_train, traval_info )
        for key in next_train.keys():
            self.__set_predict(next_train[key])
        #if 'OML2' in next_train.keys():
            #self.__set_predict(next_train[self.test_station])

    def __find_predictions(self, dicttrain, traval_info):
        station_id = traval_info["stationId"]
        time_string = traval_info['timeString']
        if station_id not in dicttrain.keys():
            dicttrain[station_id] = traval_info
        elif float(dicttrain[station_id]['timeString']) > float(time_string):
            dicttrain[station_id]['timeString'] = time_string

    def is_destination_upcoming(self, current_station, end_station):
        next_station = StationOrder.get_next(current_station)
        while("TERM" not in next_station):
            if(next_station == end_station):
                return True
            next_station = StationOrder.get_next(next_station)
        return False

    def __set_predict(self, traval_info):
        station_id = traval_info["stationId"]
        #station_id = self.set_terminal(station_id)

        if traval_info['timeString'][-2:] == '00':
            trainMessage = int(traval_info['timeString'].strp[0])
        else:
            return

        NTAS_obj = Ntas_Plist(traval_info['createDate'], traval_info['timeString'], trainMessage,
                              traval_info["trainDestination"], traval_info["trainId"])

       # if not self.is_destination_upcoming(station_id, NTAS_obj.train_dest):  ###May no longer need this
        #    return
        if station_id not in NtasLogs.predict.keys():
            if trainMessage == 'A':
                NtasLogs.predict[station_id] =  dict()
                NtasLogs.predict[station_id][trainMessage] = [NTAS_obj]
            return

        last_index = len(NtasLogs.predict[station_id]) - 1
        last_predict = NtasLogs.predict[station_id][last_index]
        #time_between_predictions = (NTAS_obj.date_obj - last_predict.date_obj).total_seconds()

        if float(last_predict.prediction) == float(NTAS_obj.prediction):
           pass
        elif last_predict.is_arrival == 'H':
            NtasLogs.predict[station_id].append(NTAS_obj)
        elif (last_predict.train_num != NTAS_obj.train_num or abs((NTAS_obj.date_obj - last_predict.date_obj).total_seconds()) > 1800 ) and last_predict.is_arrival == 'A':  #or time_between_predictions > 1800
            NtasLogs.predict[station_id].pop()
            NtasLogs.predict[station_id].append(NTAS_obj)
            print(station_id, NTAS_obj.prediction, NTAS_obj.train_num, NTAS_obj.date_str)
        elif trainMessage == 'H' and float(NTAS_obj.prediction) < 0.01:
            prediction1 = last_predict.prediction
            NTAS_obj.set_prediction(prediction1)
            NTAS_obj.set_travel(last_predict.date_obj)
            NtasLogs.predict[station_id].pop()
            NtasLogs.predict[station_id].append(NTAS_obj)

    def set_terminal(self, station):
        if ("FIN" in station) or ("SHW" in station) or ("KIP" in station) or ("KEN" in station) or ("YIE" in station) \
                or ("DML" in station):
            return station[0:3]
        else:
            return station
    def __populate_table(self):
        for station in NtasLogs.predict.keys():
            for train in NtasLogs.predict[station]:
                self.cur.execute("""INSERT INTO NTAS_logsP
                               (stationId, trainId, datetime, timestring, status, percent_error)
                                VALUES (?,?,?,?,?,?)""",(station, int(train.train_num), train.date_str, train.f_prediction,
                                                       train.is_arrival, train.percent_error))

        self.conn.commit()

    @staticmethod
    def string_to_dict(line):
        line1 = line[9:].replace("[", "{\'").replace("]", "\'}") \
            .replace("=", "\':\'") \
            .replace(", ", "', '") \
            .strip()
        traval_info = eval(line1)
        return traval_info

if __name__ == "__main__":
    Ntas = NtasLogs()
    Ntas.create_NTASlogP_table()
