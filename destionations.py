class Destination:

    def __init___(self, current_pdict = None, avg_pdict = None , n_updates = 0):
        self.current = current_pdict
        self.avg = avg_pdict
        self.num_updates = n_updates