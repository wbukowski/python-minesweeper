
import datetime as dt
from os import mkdir

class HighscoreHandler:
    """ Klasa zajmująca się obsługą najlepszych wyników. """
    def __init__(self):
        """ Przy tworzenu obiektu sczytywane są poprzednie rekordy z pliku,
        w przeciwnym przypadku tworzona jest lista pusta. """
        try:
            file = open("./highscores/highscores.csv", "r")
            lines = map(lambda line: line.split(";"), file.readlines())
            self.records = [(line[0], int(line[1]), float(line[2])) for line in lines]
        except(FileNotFoundError):
            self.records = []

    def handle(self, time, bbbv):
        """ Funkcja odpowiadająca za obsługę konkretnego wyniku.
        Liczy współczynnik 3BV/s i wstawia go w odpowiednie miejse na liście
        wyników. """
        coef = bbbv/time
        for i in range(len(self.records)):
            if coef > self.records[i][2]:
                date = str(dt.datetime.now().date())
                self.records.insert(i, (date, time, coef))
                self.save()
                return
        if len(self.records) < 10:
            date = str(dt.datetime.now().date())
            self.records.append((date, time, coef))
            self.save()

    def save(self):
        """ Funkcja zapisująca aktualną listę wyników do pliku. """
        try:
            file = open("./highscores/highscores.csv", "w")
        except(FileNotFoundError):
            mkdir("./highscores")
            file = open("./highscores/highscores.csv", "w")
        for r in self.records[:10]:
            file.write(f"{r[0]};{r[1]};{r[2]}\n")
