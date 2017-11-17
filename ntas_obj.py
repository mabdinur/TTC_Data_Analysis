from collections import OrderedDict
from datetime import datetime

class Ntas_Plist:  #(Ntas_Predict):

    def __init__(self, travel_info, arriving_in):
        self.date_str = travel_info['createDate']
        self.date_obj = self.__setdate(self.date_str)
        self.prediction = float(travel_info['timeString'].strip())
        self.arriving_in = arriving_in
        self.train_num = travel_info["trainId"]
        self.true_travel = None
        self.prediction_error = None

    def __setdate(self, date1:str):
        date1 = date1.replace("EST ", "")
        date1 = date1.replace("EDT ", "")
        return datetime.strptime(date1, "%a %b %d %H:%M:%S %Y")

    def set_travel(self, date1: datetime):
        self.true_travel = (date1 - self.date_obj).total_seconds()/60   #arrival - departure
        self.prediction_error = round(self.true_travel - self.prediction, 2) #100*(self.true_travel - self.f_prediction)/(self.true_travel)

    def adjust_prediction(self, other_prediction):
        self.prediction = self.prediction - other_prediction

    def __str__(self):
        return str(self.train_num) + " " + str(self.date_str) + " " + str(self.prediction) + " " + str(self.arriving_in) + " " + str(self.true_travel) + " " + str(self.prediction_error)
