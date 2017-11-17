from collections import OrderedDict


class Nmath:
    def __init__(self):
        self.avg = OrderedDict()
        self.sd = OrderedDict()

    def set_mean__sdeviation(self, errors):
        for key in errors.keys():
            if len(errors[key]) > 0:
                err_list = Nmath.field_list(errors[key], "prediction")
                mean = self.__calc_avg(err_list, key)
                self.__calc_standard_deviation(err_list, mean, key)

    def __calc_avg(self, nlist, index):
        num_of_terms = len(nlist)
        sum_of_terms = sum(nlist)
        self.avg[index] = sum_of_terms /num_of_terms
        return self.avg[index]

    def __calc_standard_deviation(self, nlist, mean, index):
        squared_sums = 0.0
        num_of_terms = len(nlist)
        for x in nlist:
            squared_sums += (x - mean) ** 2
        self.sd[index] = (squared_sums / num_of_terms) ** (1 / 2)
        return self.sd[index]

    @staticmethod
    def field_list(obj_list, field):
        li = list()
        for obj in obj_list:
            li.append(obj.prediction_error)
        return li