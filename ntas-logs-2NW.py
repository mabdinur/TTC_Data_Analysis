import os
from DataBaseReader import CreateDatabase
from StationOrder import StationOrder
import matplotlib.pyplot as plt
import numpy as np
from queue import Queue
from ntas_obj import Ntas_Plist
from collections import OrderedDict
import csv

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

        self.__read_folder("NTAS_Log\\")
     #   self.__populate_table()
        self.__test_print(self.test_station)
    
    def __test_print(self, test_station):

        with open("graph-data.csv", 'w', newline="" ) as myfile:
            wr = csv.writer(myfile)
            wr.writerow(["Station", "Prediction(minutes)", "Avg Error(Actual - Prediction)", "Standard Deviation", "List of Error values"])

            #for obj in NtasLogs.predict[test_station]:
            index = 0
            for key in NtasLogs.predict.keys():
                print(key)
                errors = OrderedDict([(i,list()) for i in range(15)])
                avg = OrderedDict()
                standard_deviation = list()

                for obj in NtasLogs.predict[key]:
                    if round(obj.f_prediction) != 0 :
                        key_p = round(obj.f_prediction)
                        value = obj.percent_error
                        #if value < -100:
                        #    print(obj.train_num, "True", obj.true_travel, "Prediction", obj.f_prediction,
                        #          round(obj.percent_error),
                        #          " %", obj.date_str)
                        if key_p not in errors.keys():
                            errors[key_p] = [value]
                        else:
                            errors[key_p].append(value)

                avg = self.__avg(errors)
                standard_deviation = self.__deviation(errors, avg)

                k = 0
                for all_keys in avg.keys():
                    wr.writerow([key, all_keys, avg[all_keys], standard_deviation[k], errors[all_keys]])
                    print(all_keys, errors[all_keys] )
                    k += 1
                self.create_graph(avg, standard_deviation, index, key)

    def create_graph(self, avg, standard_deviation, i, key ):
        if len(avg) > 0:
            x, y = zip(*avg.items())
            fig = plt.figure(i)
            plt.errorbar(x, y, yerr=standard_deviation, fmt='none', ecolor='r')
            plt.scatter(x, y)
            plt.xlabel("Arrival Time Prediction(rounded to nearest Minute)")
            plt.ylabel("Prediction Error (Actual - Expected)")
            plt.title(key)
            fig.canvas.set_window_title("Sunday Morning Arrival Predictions (10AM to 1PM)")
            fig.savefig("Station_figures//" + key + "SUN9AM-1PM")
            i += 1

    def __read_folder(self, dir="NTAS_Log\\" ):
        list_files = os.listdir(dir)
        for file in list_files:
            self.__read_file((dir + "\\" + file))
    
    def __avg(self, errors):
        avg = OrderedDict()
        for key in errors.keys():
            if (len(errors[key]) > 0):
             avg[key] = (sum(errors[key]))/len(errors[key])
        return avg

    def __deviation(self, errors:dict, avg:dict):
        sd = list()
        for key in avg.keys():
            squared_sums = 0.0
            for item in errors[key]:
                squared_sums += (item - avg[key])**2
            sd.append((squared_sums/len(errors[key]))**(1/2))
        return sd




    def __read_file(self, file):
        file_temp = open(file)
        next_train = dict()
        for line in file_temp:
            traval_info = NtasLogs.string_to_dict(line)
            self.__find_predictions(next_train, traval_info )
        for key in next_train.keys():
            if("SPA1" in key):
                print(next_train[key])
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
        trainMessage = 'A' if traval_info['trainMessage'] == 'Arriving' else 'H'
        NTAS_obj = Ntas_Plist(traval_info['createDate'], traval_info['timeString'], trainMessage,
                              traval_info["trainDestination"], traval_info["trainId"])
        if not self.is_destination_upcoming(station_id, traval_info["trainDestination"]):  ###May no longer need this
            return
        elif traval_info["stationId"] not in NtasLogs.predict.keys():
            NtasLogs.predict[station_id] = [NTAS_obj]
        else:
            last_index = len(NtasLogs.predict[station_id]) - 1
            last_predict = NtasLogs.predict[station_id][last_index]
            current_predict = traval_info['timeString']
            if last_predict.prediction == NTAS_obj.prediction:
                return
            elif last_predict.train_num != NTAS_obj.train_num and last_predict.is_arrival == 'A':
                NtasLogs.predict[station_id].pop()
                NtasLogs.predict[station_id].append(NTAS_obj)
            elif last_predict.is_arrival == 'H':
                NtasLogs.predict[station_id].append(NTAS_obj)
                # print(trainMessage, traval_info['trainMessage'] )
            elif trainMessage == 'H' and float(current_predict) < 0.01:
                date1 = NtasLogs.predict[station_id][last_index].date_obj
                prediction1 = NtasLogs.predict[station_id][last_index].prediction
                NTAS_obj.set_prediction(prediction1)
                NTAS_obj.set_travel(date1)
                NtasLogs.predict[station_id].pop()
                NtasLogs.predict[station_id].append(NTAS_obj)

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
