
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QFormLayout, QSlider, QDialogButtonBox, QTableWidget, QTableWidgetItem, QWidget
from PyQt5.QtCore import Qt
from saper_gui import BoardManager, highscore_handler


def clear_board(layout):
    """ Czyści layout zawierający przyciski reprezentujące pola planszy """
    for row in layout.children():
        while row.count():
            child = row.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


def clear_stats_row(layout):
    """ Czyści layout zawierający elementy statystyczne planszy: współczynnik
    3BV, liczbę min pozostałych do oflagowania oraz dotychczasowy czas
    przeznaczony na rozwiązanie planszy """
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


def GameModeSelector():
    """ Wywołuje okno dialogowe służące do wyboru nowej gry. Zwraca
    3-elementową krotkę (długość, wysokość, liczba_min). """
    window = QDialog()
    layout = QHBoxLayout()
    window.setLayout(layout)

    column = QVBoxLayout()
    layout.addLayout(column)

    easy_row = QHBoxLayout()
    easy_button = QPushButton("Easy")
    easy_button.setCheckable(True)
    easy_button.clicked.connect(lambda: ontoggle(easy_button))
    easy_desc = QLabel("Easy mode")
    easy_row.addWidget(easy_button)
    easy_row.addWidget(easy_desc)
    column.addLayout(easy_row)

    advanced_row = QHBoxLayout()
    advanced_button = QPushButton("Advanced")
    advanced_button.setCheckable(True)
    advanced_button.clicked.connect(lambda: ontoggle(advanced_button))
    advanced_desc = QLabel("Advanced mode")
    advanced_row.addWidget(advanced_button)
    advanced_row.addWidget(advanced_desc)
    column.addLayout(advanced_row)

    expert_row = QHBoxLayout()
    expert_button = QPushButton("Expert")
    expert_button.setCheckable(True)
    expert_button.clicked.connect(lambda: ontoggle(expert_button))
    expert_desc = QLabel("Expert mode")
    expert_row.addWidget(expert_button)
    expert_row.addWidget(expert_desc)
    column.addLayout(expert_row)

    custom_column = QVBoxLayout()
    custom_button = QPushButton("Custom")
    custom_button.setCheckable(True)
    custom_button.clicked.connect(lambda: ontoggle(custom_button))
    custom_column.addWidget(custom_button)

    custom_sliders_and_values = QHBoxLayout()
    custom_form = QFormLayout()
    custom_width = QSlider(Qt.Horizontal)
    custom_width.setMinimum(9)
    custom_width.setMaximum(30)
    custom_width.valueChanged.connect(lambda: set_mines_maximum(custom_width))
    custom_width.setDisabled(True)
    custom_height = QSlider(Qt.Horizontal)
    custom_height.setMinimum(9)
    custom_height.setMaximum(24)
    custom_height.valueChanged.connect(
        lambda: set_mines_maximum(custom_height))
    custom_height.setDisabled(True)
    custom_mines = QSlider(Qt.Horizontal)
    custom_mines.setMinimum(9)
    custom_mines.setMaximum(9)
    custom_mines.valueChanged.connect(lambda: slider_changed(custom_mines))
    custom_mines.setDisabled(True)
    custom_form.addRow("Width: ", custom_width)
    custom_form.addRow("Height: ", custom_height)
    custom_form.addRow("Mines: ", custom_mines)
    custom_sliders_and_values.addLayout(custom_form)

    custom_values = QVBoxLayout()
    custom_width_label = QLabel()
    custom_width_label.setText(str(custom_width.value()))
    custom_values.addWidget(custom_width_label)
    custom_height_label = QLabel()
    custom_height_label.setText(str(custom_height.value()))
    custom_values.addWidget(custom_height_label)
    custom_mines_label = QLabel()
    custom_mines_label.setText(str(custom_mines.value()))
    custom_values.addWidget(custom_mines_label)
    custom_sliders_and_values.addLayout(custom_values)
    custom_column.addLayout(custom_sliders_and_values)
    layout.addLayout(custom_column)

    def disable_custom(bool):
        custom_height.setDisabled(bool)
        custom_width.setDisabled(bool)
        custom_mines.setDisabled(bool)

    def ontoggle(button):
        if button != easy_button:
            easy_button.setChecked(False)
        if button != advanced_button:
            advanced_button.setChecked(False)
        if button != expert_button:
            expert_button.setChecked(False)
        if button != custom_button:
            custom_button.setChecked(False)
            disable_custom(True)
        else:
            disable_custom(False)

    def set_mines_maximum(slider):
        custom_mines.setMaximum(
            int(0.35 * custom_height.value() * custom_width.value()))
        slider_changed(slider)

    def slider_changed(slider):
        if slider == custom_width:
            custom_width_label.setText(str(custom_width.value()))
        elif slider == custom_height:
            custom_height_label.setText(str(custom_height.value()))
        elif slider == custom_mines:
            custom_mines_label.setText(str(custom_mines.value()))

    confirm_button = QDialogButtonBox(QDialogButtonBox.Ok, window)
    confirm_button.accepted.connect(window.accept)
    column.addWidget(confirm_button)
    if window.exec():
        if easy_button.isChecked():
            return (8, 8, 10)
        elif advanced_button.isChecked():
            return (16, 16, 40)
        elif expert_button.isChecked():
            return (30, 16, 99)
        else:
            return (custom_width.value(), custom_height.value(), custom_mines.value())
    else:
        return None


class HighscoreDialog(QDialog):
    """ Okno dialogowe zawierające tabelę z najlepszymi wynikami. """
    def __init__(self, parent=None):
        super(HighscoreDialog, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.table = QTableWidget(10, 3)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(["Date", "Time", "3BV/s"])
        self.fill_table(self.table)
        layout.addWidget(self.table)

    def fill_table(self, table):
        """ Uzupełnienie tabeli wierszami z zaimportowanego obiektu klasy 
        HighscoreHandler. """
        for i in range(len(highscore_handler.records)):
            record = highscore_handler.records[i]
            (minutes, seconds) = divmod(record[1], 60)

            date_item = QTableWidgetItem(record[0])
            time_item = QTableWidgetItem(f"{minutes}:{seconds}")
            coef_item = QTableWidgetItem(str(record[2]))

            table.setItem(i, 0, date_item)
            table.setItem(i, 1, time_item)
            table.setItem(i, 2, coef_item)
        table.resizeColumnsToContents()


class MenuButtons(QHBoxLayout):
    """ Layout zawierający przyciski menu: nowej gry i najlepszych wyników. """
    def __init__(self, parent=None):
        super(MenuButtons, self).__init__(parent)
        self.new_game_button = QPushButton("New game")
        self.highscore_button = QPushButton("Highscores")
        self.addWidget(self.new_game_button)
        self.addWidget(self.highscore_button)


class GameWindow(QWidget):
    """ Główne okno gry """
    def __init__(self, parent=None):
        super(GameWindow, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.menu = MenuButtons()
        self.menu.new_game_button.clicked.connect(lambda: self.new_game(layout))
        self.menu.highscore_button.clicked.connect(self.highscores)
        layout.addLayout(self.menu)

        (width, height, mines) = GameModeSelector()
        self.board = BoardManager(width, height, mines)
        self.board_layout = self.board.to_layout()
        self.bbbv_label = QLabel()
        self.bbbv_label.setText(f"3BV of the board: {self.board.board.bbbv}")

        self.stats_row = QHBoxLayout()
        self.stats_row.addWidget(self.board.timer)
        self.stats_row.addWidget(self.board.mines_counter)
        self.stats_row.addWidget(self.bbbv_label)
        layout.addLayout(self.stats_row)
        layout.addLayout(self.board_layout)
        self.show()

    def new_game(self, layout):
        """ Sczytuje parametry nowej planszy i uzupełnia layout o odpowiednie
        widgety. """
        params = GameModeSelector()
        if params is None:
            return

        clear_board(self.board_layout)
        clear_stats_row(self.stats_row)

        (width, height, mines) = params
        self.board = BoardManager(width, height, mines)
        self.board_layout = self.board.to_layout()
        self.bbbv_label = QLabel()
        self.bbbv_label.setText(f"3BV of the board: {self.board.board.bbbv}")

        self.stats_row.addWidget(self.board.timer)
        self.stats_row.addWidget(self.board.mines_counter)
        self.stats_row.addWidget(self.bbbv_label)
        layout.addLayout(self.stats_row)
        layout.addLayout(self.board_layout)
        self.setFixedSize(width*40, height*40 + 50)

    def highscores(self):
        """ Wywołuje okno dialogowe z najlepszymi wynikami """
        window = HighscoreDialog()
        window.exec()
