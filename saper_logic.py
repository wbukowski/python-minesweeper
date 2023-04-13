
import random


class Board:
    """ Klasa zajmująca się obsługą logiki gry. """
    def __init__(self, width, height, mines):
        self.width = width
        self.height = height
        self.fields = [[(0, 'c') for i in range(width)] for j in range(height)]
        self.islands = 0
        self.flags = 0
        self.lost = False
        self.place_mines(mines)
        self.fill_with_numbers()
        self.calc_bbbv()

    def place_mines(self, x):
        """ Funkcja losująca pozycję min na planszy i wstawiająca je w
        odpowiednie miejsca. """
        self.mines = x
        mines = random.sample(range(self.width * self.height), x)
        for m in mines:
            self.fields[m // self.width][m % self.width] = (-1, 'c')

    def fill_with_numbers(self):
        """ Funkcja wstawiająca cyfry w poszczególne pola planszy
        zależne od ilości sąsiednich min. """
        for y in range(self.height):
            for x in range(self.width):
                self.fields[y][x] = (self.get_number_of_mines(x, y), 'c')

    def get_number_of_mines(self, x, y):
        """ Funkcja obliczająca liczbę min sąsiednich do pola o zadanych jako
        parametry indeksach. """
        if self.fields[y][x][0] == -1:
            return -1
        res = 0
        for i in range(max(-1, -y), min(2, self.height - y)):
            for j in range(max(-1, -x), min(2, self.width - x)):
                if self.fields[y + i][x + j][0] == -1:
                    res += 1
        return res

    def get_number_of_flags(self, x, y):
        """ Funkcja obliczająca liczbę pól oznaczonych flagą sąsiednich
        do pola o indeksach zadanych jako parametry. """
        res = 0
        for i in range(max(-1, -y), min(2, self.height - y)):
            for j in range(max(-1, -x), min(2, self.width - x)):
                if self.fields[y + i][x + j][1] == 'f':
                    res += 1
        return res

    def uncover(self, x, y):
        """ Funkcja odsłaniająca wybrane pole lub, w przypadku 0, całą wyspę.
        W przypadku odkrycia miny ustawia zmienną 'lost' na prawdę.
        Zwraca prawdę, gdy pole udało się odkryć i fałsz w przeciwnym
        przypadku. """
        if self.fields[y][x][1] != 'c':
            return False

        to_uncover = self.fields[y][x][0]
        if to_uncover == 0:
            self.islands += 1
            self.uncover_island(x, y)
        self.fields[y][x] = (to_uncover, 'u')
        if to_uncover == -1:
            self.lost = True
        return True

    def uncover_mines(self):
        """ Funkcja odsłaniająca wszystkie miny na planszy. """
        for y in range(self.height):
            for x in range(self.width):
                if self.fields[y][x][0] == -1:
                    self.fields[y][x] = (self.fields[y][x][0], 'u')

    def uncover_island(self, x, y):
        """ Funkcja rekurencyjna, która odsłania wyspę. Odsłania pole o
        zadanych indeksach i, jeśli pole nie leży na granicy wyspy,
        wywołuje się rekurencyjnie na jego sąsiadach. """
        to_uncover = self.fields[y][x]
        if to_uncover[0] == 0 and to_uncover[1] == 'c':
            self.fields[y][x] = (to_uncover[0], 'u')
            for i in range(max(-1, -y), min(2, self.height - y)):
                for j in range(max(-1, -x), min(2, self.width - x)):
                    self.uncover_island(x + j, y + i)
        elif to_uncover[1] == 'c':
            self.uncover(x, y)

    def quick_uncover(self, x, y):
        """ Funkcja odkrywająca zakrytych sąsiadów pola o wskazanych indeksach,
        jeśli liczba flag na sąsiednich polach jest równa jego liczbie
        sąsiednich min. Zwraca prawdę, gdy odkrycie udało było możliwe i fałsz
        w przeciwnym wypadku. """
        if self.fields[y][x][1] != 'u':
            return False
        if self.fields[y][x][0] != self.get_number_of_flags(x, y):
            return False

        for i in range(max(-1, -y), min(2, self.height - y)):
            for j in range(max(-1, -x), min(2, self.width - x)):
                if self.fields[y + i][x + j][1] != 'f':
                    self.uncover(x + j, y + i)
        return True

    def calc_bbbv(self):
        """ Funkcja wyliczająca współczynnik 3BV planszy. Zasada obliczania
        współczynnika jest następująca:
        - oznacz każdą wyspę razem z jej brzegami, do rezultatu dodaj liczbę
        wysp
        - dodaj 1 do rezultatu dla każdego pola, które nie jest miną, ani nie
        jest już oznaczone"""
        marked = {}

        def mark_around_0(x, y):
            """ Funkcja zaznaczająca pola wokół 0. """
            for i in range(max(-1, -y), min(2, self.height - y)):
                for j in range(max(-1, -x), min(2, self.width - x)):
                    if (x + j, y + i) not in marked and self.fields[y + i][x + j][0] != -1:
                        marked[(x + j, y + i)] = True
                        if self.fields[y + i][x + j][0] == 0:
                            mark_around_0(x + j, y + i)

        self.bbbv = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.fields[y][x][0] == 0 and (x, y) not in marked:
                    marked[(x, y)] = True
                    self.bbbv += 1
                    mark_around_0(x, y)

        for y in range(self.height):
            for x in range(self.width):
                if self.fields[y][x][0] != -1 and (x, y) not in marked:
                    marked[(x, y)] = True
                    self.bbbv += 1

    def flag(self, x, y):
        """ Funkcja ustawiająca flagę na polu o zadanych indeksach.
        Zwraca prawdę, gdy operacja powiodła się oraz fałsz, gdy nie ma już
        więcej flag do wykorzystania. """
        if self.fields[y][x][1] == 'u':
            return False

        if self.fields[y][x][1] == 'f':
            self.unflag(x, y)
            return True

        if self.flags >= self.mines:
            return False

        self.flags += 1
        self.fields[y][x] = (self.fields[y][x][0], 'f')
        return True

    def unflag(self, x, y):
        """ Funkcja usuwająca flagę z pola o podanych indeksach. """
        self.flags -= 1
        self.fields[y][x] = (self.fields[y][x][0], 'c')

    def check_for_win(self):
        """ Funkcja sprawdzająca, czy plansza nie została już rozwiązana. """
        for i in range(self.height):
            for j in range(self.width):
                if self.fields[i][j][0] != -1 and self.fields[i][j][1] != 'u':
                    return False
        return True
