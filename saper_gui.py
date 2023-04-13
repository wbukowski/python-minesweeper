from PyQt5.QtWidgets import QAbstractButton, QLabel, QDialog, QSizePolicy, QVBoxLayout, QDialogButtonBox, QHBoxLayout
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt, QTimer, QSize
from highscore_handler import HighscoreHandler
import saper_logic as saper

highscore_handler = HighscoreHandler()


class FieldButton(QAbstractButton):
    """ Przycisk reprezentujący pole planszy. """
    def __init__(self, x, y, board, default, hover, parent=None):
        """ Jako argumenty dostaje kolejno: pozycję X-ową; pozycję Y-ową;
        planszę, na której się znajduje; domyślną ikonkę;
         ikonkę wyświetlaną przy najechaniu myszką na przycisk.

        Ustawia również parametry oznaczające najechanie myszką oraz
        odznaczenie na planszy."""
        super().__init__(parent)
        self.posX = x
        self.posY = y
        self.board = board
        self.current = default
        self.default = default
        self.on_hover = hover
        self.covered = True
        self.marked = False
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def paintEvent(self, event):
        """ Przeładowanie funkcji, które rysuje na przycisku PixMap trzymany
        pod zmienną 'current'"""
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.current)

    def mousePressEvent(self, e):
        """ Zdarzenie obsługujące kliknięcie przycisku.

        W przypadku kliknięcia lewym przyciskiem myszy oznacza sąsiadów
        przycisku.
        W przypadku kliknięcia prawym przyciskiem oznacza pole flagą.
        Dodatkowo, gdy przycisk kliknięty został jako pierwszy, odpala stoper
        mierzący czas wykonania planszy. """
        if e.button() == Qt.LeftButton:
            if not self.covered:
                self.board.mark_neighbours(self.posX, self.posY)
        else:
            if self.board.board.flag(self.posX, self.posY):
                self.board.mines_counter.update_label(self.board.board.flags)
                self.board.render()
        if not self.board.timer.running:
            self.board.timer.start()

    def mouseReleaseEvent(self, e):
        """ Zdarzenie obsługujące puszczenie przycisku.

        Jeśli przycisk kliknięty został lewym przyciskiem myszy, odznacza go.
        Jeśli możliwe jest szybkie odkrycie sąsiadów pola, jest ono
        wykonywane. """
        if e.button() == Qt.LeftButton:
            if not self.covered:
                self.board.unmark_neighbours(self.posX, self.posY)
            if self.board.board.quick_uncover(self.posX, self.posY):
                self.board.render()
            if self.board.board.uncover(self.posX, self.posY):
                self.covered = False
                self.board.render()

    def enterEvent(self, a0):
        """ Funkcja zmieniająca ikonkę przycisku, gdy najedziemy na niego
        myszką. """
        if self.covered:
            self.current = self.on_hover

    def leaveEvent(self, a0):
        """ Funkcja przywracająca przycisk po opuszczeniu myszki. """
        if self.covered:
            self.current = self.default

    def sizeHint(self):
        """ Funkcja ustalająca rozmiar przycisku. """
        return QSize(40, 40)


class BoardManager:
    """ Obiekt odpowiadający za komunikację GUI z logiką gry. """
    def __init__(self, width, height, mines):
        """ Przy inicjacji obiekt dostaje parametry początkowe planszy: długość,
        wysokość oraz liczbę min.
        Tworzona jest warstwa logiczna planszy, przyciski odpowiadające polom,
        stoper, licznik min pozostałych do oflagowania oraz ładowane są
        tekstury przycisków. """
        self.board = saper.Board(width, height, mines)
        self.width = width
        self.height = height
        self.load_tiles()
        self.buttons = [[FieldButton(i, j, self, self.default_tile, self.hover_tile) for i in range(width)] for j in range(height)]
        self.timer = TimerWidget()
        self.mines_counter = MinesCounter(self.board.mines)

    def load_tiles(self):
        """ Funkcja ładująca tekstury przycisków z plików. """
        self.default_tile = QPixmap("./icons/blue_tile.png")
        self.hover_tile = QPixmap("./icons/purple_tile.png")
        self.mine_tile = QPixmap("./icons/naval-mine.png")
        self.flag_tile = QPixmap("./icons/flag.png")
        self.number_tiles = [QPixmap(f"./icons/{i}.png") for i in range(0, 9)]

    def to_layout(self):
        """ Funkcja zwracająca layout wypełniony przyciskami obsługiwanymi
        przez klasę. """
        layout = QVBoxLayout()
        layout.setSpacing(0)
        for list in self.buttons:
            row = QHBoxLayout()
            for b in list:
                row.addWidget(b)
            layout.addLayout(row)
        return layout

    def render(self):
        """ Funkcja renderująca aktualny wygląd przycisków, a także
        sprawdzająca, czy rozgrywka nie została zakończona."""
        for list in self.buttons:
            for b in list:
                if b.marked:
                    b.current = self.hover_tile
                else:
                    b.current = self.field_to_tile(b.posX, b.posY)
                if self.board.fields[b.posY][b.posX][1] != 'c':
                    b.covered = False
                else:
                    b.covered = True
                b.update()
        if self.board.lost and self.timer.running:
            self.timer.end()
            self.game_lost()
        if self.board.check_for_win():
            self.timer.end()
            self.game_won()

    def field_to_tile(self, x, y):
        """ Funkcja przyporządkowująca polu o podanych indeksach teksturę,
        która odpowiada jego liczbie sąsiednich min. """
        if self.board.fields[y][x][1] == 'c':
            return self.default_tile
        if self.board.fields[y][x][1] == 'f':
            return self.flag_tile
        if self.board.fields[y][x][0] == -1:
            return self.mine_tile
        return self.number_tiles[self.board.fields[y][x][0]]

    def mark_neighbours(self, x, y):
        """ Funkcja podświetlająca zakrytych sąsiadów przycisku o zadanych
        współrzędnych. """
        for i in range(max(-1, -y), min(2, self.height - y)):
            for j in range(max(-1, -x), min(2, self.width - x)):
                if self.buttons[y + i][x + j].covered:
                    self.buttons[y + i][x + j].marked = True
        self.render()

    def unmark_neighbours(self, x, y):
        """ Funkcja przywracająca zakrytych sąsiadów przycisku o podanych
        współrzędnych do stanu pierwotnego."""
        for i in range(max(-1, -y), min(2, self.height - y)):
            for j in range(max(-1, -x), min(2, self.width - x)):
                if self.buttons[y + i][x + j].covered:
                    self.buttons[y + i][x + j].marked = False
        self.render()

    def disable_buttons(self):
        """ Funkcja wyłączająca przyciski odpowiadające za plansze, używana po
        zakończeniu rozgrywki. """
        for row in self.buttons:
            for b in row:
                b.setDisabled(True)

    def game_lost(self):
        """ Funkcja wywoływana w przypadku przegrania rozgrywki.
        Wyłącza przyciski reprezentujące pola, odkrywa wszystkie miny oraz
        wyświetla stosowne okno dialogowe."""
        self.disable_buttons()
        self.board.uncover_mines()
        self.render()
        result = ResultWindow(False)
        result.exec()

    def game_won(self):
        """ Funkcja wywoływana w przypadku wygrania rozgrywki.
        Wyłącza przyciski odpowiadające za pola planszy, zapisuje wynik oraz
        wywołuje stosowne okno. """
        self.disable_buttons()
        highscore_handler.handle(self.timer.current, self.board.bbbv)
        result = ResultWindow(True, self.timer, self.board.bbbv)
        result.exec()


class TimerWidget(QLabel):
    """ Kontrolka pełniąca funkcję miernika czasu wykonania planszy. """
    def __init__(self, parent=None):
        """ Podczas inicjacji obiektu tworzony jest zegar, który będzie
        odmierzał czas, ustawiany jest czas początkowy oraz ustawiana jest
        etykieta kontrolki. """
        super(TimerWidget, self).__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.count)
        self.current = 0
        self.running = False
        self.update_label()

    def update_label(self):
        """ Funkcja uaktualniająca etykietę kontrolki. """
        self.setText(self.get_time())

    def count(self):
        """ Funkcja zwiększająca licznik zegara o sekundę. """
        self.current += 1
        self.update_label()

    def start(self):
        """ Funkcja, która daje sygnał do startu zegarowi. """
        self.current = 0
        self.running = True
        self.timer.start(1000)

    def end(self):
        """ Funkcja zatrzymująca zegar. """
        self.running = False
        self.timer.stop()

    def get_time(self):
        """ Funkcja zwracająca aktualny czas zegarka w postaci MM:SS gdzie MM
        to minuty, a SS to sekundy. """
        (minutes, seconds) = divmod(self.current, 60)
        return "{:02d}:{:02d}".format(minutes, seconds)


class MinesCounter(QLabel):
    """ Kontrolka odpowiadająca za informację o liczbie już oznakowanych
    min. """
    def __init__(self, mines, parent=None):
        super(MinesCounter, self).__init__(parent)
        self.mines_to_mark = mines
        self.update_label(0)

    def update_label(self, flags):
        """ Funkcja uaktualniająca etykietę kontrolki. """
        self.setText(f"Mines left to be marked: {self.mines_to_mark - flags}")


class ResultWindow(QDialog):
    """ Okno dialogowe informujące o rezultacie rozgrywki. """
    def __init__(self, won, timer=None, bbbv=0, parent=None):
        """ Funkcja inicjująca dostaje jako parametry wartość boolowską,
        która informuje o rezultacie, kontrolkę zegara oraz współczynnik
        bbbv planszy.

        W przypadku porażki wyświetla komunikat o porażce.
        W przypadku zwycięstwa informuje o czasie oraz współczynniku 3BV/s. """
        super(ResultWindow, self).__init__(parent)
        layout = QVBoxLayout()

        self.label = QLabel()
        if won:
            self.label.setText(f"You won with time: {timer.get_time()}\n Your 3BV/s is: {bbbv/timer.current}")
        else:
            self.label.setText("You lost!")
        layout.addWidget(self.label)

        ok_button = QDialogButtonBox(QDialogButtonBox.Ok, self)
        ok_button.accepted.connect(self.accept)
        layout.addWidget(ok_button)
        self.setLayout(layout)
