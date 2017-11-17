from readcsv import Readcsv
from datetime import datetime
from collections import OrderedDict
from StationOrder import StationOrder
from DataBaseReader import CreateDatabase

class Predictions(Readcsv):
    predict = super().create_dest()
    this_hour = datetime.now().hour
    #odDict = OrderedDict()
    #odDict = {{"UNI1": datetime.now()}, {"KNG1": datetime.now()}}

    #train is an ordered dict
    def update_current(cls, train, trigger_station):
        "Train is a dictionary containing StationName -- Datetime associated with 1 train"
        end_time = train[trigger_station]
        num_stops = len(train.keys())

        for i in range(num_stops - 2, -1, -1 ):  #start at second index and iterate to 0
            curr_station = train.get(i)
            next_station_actual = train.get(i+1)
            next_station_path = StationOrder.nstation_dict[curr_station]
            if next_station_actual == next_station_path:
                station_time = train[i]
                travel_time = station_time - end_time
                cls.__set_dest_time(curr_station, next_station_actual, travel_time)

        cls.__new_avgtime(end_time)

    def __set_dest_time(cls, current_station, target_station, new_time):
        dest_list = cls.predict[current_station]
        for dest in dest_list.keys():
            if dest == target_station:
                cls.predict[current_station][dest].current = new_time
                cls.__set_avgtime(new_time, current_station, dest)

    def __set_avgtime(cls, new_time, current_station, dest):
        avg_time = cls.predict[current_station][dest].avg
        num = cls.predict[current_station][dest].num_updates
        if avg_time == None:
            avg_time = 0
        if avg_time == None:
            num = 0
        avg_time = (num/(num+1))*avg_time + new_time/(num+1)
        cls.predict[current_station][dest].avg = avg_time

    def __new_avgtime(cls, endtime: datetime):
        prev_hour = cls.this_hour
        if prev_hour != endtime.hour:
            CreateDatabase.update_avgpredict(prev_hour, cls.predict)
            CreateDatabase.set_avgpredict(prev_hour, cls.predict)
            cls.this_hour = endtime.hour

    def __reset_dict(cls, class_dict, value = None):
        for key in class_dict:
            for nested_key in key:
                class_dict[key][nested_key] = value