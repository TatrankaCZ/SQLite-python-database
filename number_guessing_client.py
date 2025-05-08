
# client-test 4 (nejnovejsi)

from ctypes import alignment
import sys
from PySide6.QtCore import QRect, Qt, Slot, QCoreApplication, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QFont, QPen, QIntValidator
from PySide6.QtWidgets import QStackedWidget, QApplication, QGridLayout, QLabel, QLayout, QTableWidget, QWidget, QListWidget, QListWidgetItem, \
    QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QGraphicsScene, QMainWindow, QTableWidgetItem, QSizePolicy, QHeaderView

import time
import json

import requests
from bs4 import BeautifulSoup

darkStyleSheet = """
    QWidget {
        background-color: #121f26;
        color: #ffffff;
    }
    QPushButton {
        background-color: #192638;
        color: #ffffff;
        border: 1px solid #0c141f;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #22334a;
    }
    QListWidget {
        background-color: #192638;
        color: #ffffff;
        border: 1px solid #0c141f;
    }
    QLineEdit {
        background-color: #192638;
        color: #ffffff;
        border: 1px solid #0c141f;
    }
    QTableWidget {
        background-color: #192638;
        color: #ffffff;
        border: 1px solid #0c141f;

    }
    QTableWidget QHeaderView::section {
        background-color: #192638; 
        color: #ffffff;       
        border: 1px solid #0c141f;
    }
    QTableWidget::item {

    }
"""


def get_html(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup


class WelcomeScreen(QHBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        start_layout = QVBoxLayout()
        spacer = QWidget()
        start_layout.addWidget(spacer)

        welcome_font = QFont("calibri", 100)

        welcome = QLabel("Vitej!", alignment=Qt.AlignCenter)
        welcome.setFont(welcome_font)
        self.welcome_button = QPushButton("zacit", font=QFont("calibri", 15))
        self.welcome_button.setMinimumSize(150, 50)
        self.welcome_button.clicked.connect(app.RoomMove1)#(app.WSWidget, app.MMWidget))

        start_layout.addWidget(welcome)
        start_layout.addWidget(self.welcome_button)
        start_layout.addWidget(spacer)

        text_widget = QLabel("vysledek", alignment=Qt.AlignCenter)

        content_layout = QVBoxLayout()
        content_layout.addWidget(text_widget)

        main_widget = QWidget()
        main_widget.setLayout(content_layout)
        main_widget.setVisible(False)

        start_menu = QWidget()
        start_menu.setLayout(start_layout)

        self.addWidget(start_menu, 1)
        self.addWidget(main_widget, 4)

    def set_on_click(self, on_click):
        self.welcome_button.clicked.connect(on_click)

class RoomSelection(QHBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO automaticky nacti mistnosti
        self.app = app
        self.RoomSelectionLabel = QLabel("Seznam mistnosti", alignment=Qt.AlignCenter, font=QFont("calibri", 20))

        self.menu_widget = QListWidget()
        self.menu_widget.itemClicked.connect(app.on_selected)

        self.gentext = QWidget()
        
        self.generate = QPushButton("generovat mistnost", font=QFont("calibri", 15))
        self.generate.setMinimumSize(150, 30)
        self.generate.clicked.connect(app.RoomMove7)
        self.generated_rooms = QVBoxLayout()

        self.Back = QPushButton("zpet", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 30)
        self.Back.clicked.connect(app.RoomMove4)
        
        self.generated_rooms.addWidget(self.RoomSelectionLabel)
        self.generated_rooms.addWidget(self.menu_widget)
        self.generated_rooms.addWidget(self.generate)
        self.generated_rooms.addWidget(self.Back)
        
        self.gentext.setLayout(self.generated_rooms)

        self.addWidget(self.gentext)

        self.loadRooms()

    def loadRooms(self):
        try:
            response = requests.get("http://localhost:8081/rooms")
            if response.status_code == 200:
                rooms = response.json()
                self.menu_widget.clear()
                for room in rooms:
                    if not room["completed"]:
                        roomName = f"Místnost {room['id']}"
                        item = QListWidgetItem(roomName)
                        item.setTextAlignment(Qt.AlignCenter)
                        item.setFont(QFont("calibri", 15))
                        self.menu_widget.addItem(item)
                        self.app.rooms[roomName] = {
                            "ID": room['id'],
                            "score": room['score'],
                            "guess_number": room['guess_number']
                        }
                        self.app.rooms[roomName]["OUTPUT"] = roomName + "\nvysledek"
            else:
                print("Nepodařilo se načíst místnoti.")
        except Exception as e:
            print(f"Chyba při načítání místností: {e}")

class NumberRangeSelect(QVBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app
        
        self.NumberRangeSelectLabel = QLabel("Vytvorit mistnost", alignment=Qt.AlignCenter, font=QFont("calibri", 30))
        
        self.minNumberText = QLabel("Minimalni cislo", alignment=Qt.AlignCenter, font=QFont("calibri", 25))
        self.minNumber = QLineEdit(font=QFont("calibri", 20))
        self.minNumber.setValidator(QIntValidator(1, 100))
        self.minNumber.setPlaceholderText(str(Widget.DEFAULT_MIN))

        # TODO - add validator [HOTOVO? Pat a Mat řešení]
        self.maxNumberText = QLabel("Maximalni cislo", alignment=Qt.AlignCenter, font=QFont("calibri", 25))
        self.maxNumber = QLineEdit(font=QFont("calibri", 20))
        #self.maxNumber.setValidator(QIntValidator(self.minNumber + 1, 101))
        self.maxNumber.setPlaceholderText(str(Widget.DEFAULT_MAX))

        self.maxNumberError = QLabel("")
        self.maxNumberError.setStyleSheet("color: red;")
        self.maxNumberError.setFont(QFont("calibri", 14))
        self.maxNumberError.setAlignment(Qt.AlignCenter)

        self.horizontalSplit = QHBoxLayout()
        self.verticalSplit1 = QVBoxLayout()
        self.verticalSplit2 = QVBoxLayout()

        self.verticalSplit1.addWidget(self.minNumberText)
        self.verticalSplit1.addWidget(self.minNumber)

        self.verticalSplit2.addWidget(self.maxNumberText)
        self.verticalSplit2.addWidget(self.maxNumber)

        self.verticalSplit_ = QWidget()
        self.verticalSplit_.setLayout(self.verticalSplit1)
        self.verticalSplit2_ = QWidget()
        self.verticalSplit2_.setLayout(self.verticalSplit2)

        self.horizontalSplit.addWidget(self.verticalSplit_)
        self.horizontalSplit.addWidget(self.verticalSplit2_)

        self.horizontalSplitWidget = QWidget()

        self.horizontalSplitWidget.setLayout(self.horizontalSplit)

        self.generate = QPushButton("generovat mistnost", font=QFont("calibri", 15))
        self.generate.setMinimumSize(150, 30)

        self.Back = QPushButton("zpet", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 30)
        self.Back.clicked.connect(app.RoomMove8)
        
        self.generate.clicked.connect(self.validateMaxNumber)

        self.addWidget(self.NumberRangeSelectLabel)
        self.addWidget(self.horizontalSplitWidget)
        self.addWidget(self.generate)
        self.addWidget(self.Back)
        self.addWidget(self.maxNumberError)

        

    def validateMaxNumber(self):
        min_number = int(self.minNumber.text()) if self.minNumber.text().isnumeric() else self.app.DEFAULT_MIN
        max_number = int(self.maxNumber.text()) if self.maxNumber.text().isnumeric() else self.app.DEFAULT_MAX
        if max_number <= min_number:
            self.maxNumberError.setText("Maximalni cislo musi byt vetsi nez minimalni")
        else:
            self.maxNumberError.setText("")
            self.app.roomgen()

class GameField(QVBoxLayout):
     def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.GameFieldLabel = QLabel("Herni pole", alignment=Qt.AlignCenter, font=QFont("calibri", 25))

        self.text_widget = QLabel("vysledek", alignment=Qt.AlignCenter, font=QFont("calibri", 15))
        self.line_edit = QLineEdit(font=QFont("calibri", 15))
        self.line_edit.setPlaceholderText("Zadejte hadane cislo")
        self.line_edit.setMinimumSize(150, 30)
        self.line_edit.returnPressed.connect(app.guess)

        self.submit_button = QPushButton("potvrdit", font=QFont("calibri", 15))
        self.submit_button.setMinimumSize(150, 40)
        self.submit_button.clicked.connect(app.guess)

        # self.content_layout = QVBoxLayout()
        # self.content_layout.addWidget(self.text_widget)

        self.text = QVBoxLayout()
        self.text.addWidget(self.line_edit)
        self.text.addWidget(self.submit_button)

        self.input_text = QWidget()
        self.input_text.setLayout(self.text)

        self.Back = QPushButton("zpet", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 40)
        self.Back.clicked.connect(app.RoomMove5)

        self.addWidget(self.GameFieldLabel)
        self.addWidget(self.text_widget)
        self.addWidget(self.input_text)
        self.addWidget(self.Back)

class MainMenu(QVBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.MainMenuLabel = QLabel("Hlavni menu", alignment=Qt.AlignCenter, font=QFont("calibri", 48))

        self.RoomList = QPushButton("Seznam mistnosti", font=QFont("calibri", 15))
        self.RoomList.setMinimumSize(150, 50)
        self.RoomList.clicked.connect(app.RoomMove2)

        self.HighScore = QPushButton("Score", font=QFont("calibri", 15))
        self.HighScore.setMinimumSize(150, 50)
        self.HighScore.clicked.connect(app.RoomMove9)

        self.QuitButton = QPushButton("Ukoncit", font=QFont("calibri", 15))
        self.QuitButton.setMinimumSize(150, 50)
        self.QuitButton.clicked.connect(self.quitApp)
        
        self.addWidget(self.MainMenuLabel)
        self.addWidget(self.RoomList)
        self.addWidget(self.HighScore)
        self.addWidget(self.QuitButton)

    def quitApp(self):
        QCoreApplication.quit()
        sys.exit(0)



class FetchRoomsWorker(QThread):
    rooms_fetched = Signal(list)

    def run(self):
        try:
            response = requests.get("http://localhost:8081/rooms")
            data = response.json()
            self.rooms_fetched.emit(data)
        except Exception as e:
            print(f"Chyba při načítání dat: {e}")
            self.rooms_fetched.emit([])


class HighScore(QVBoxLayout):

    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.table = QTableWidget()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.addWidget(self.table, stretch=1) 

        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Room", "Score", "Hadane cislo", "Dokonceno"])
        self.table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)

        self.Back = QPushButton("zpet", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 50)
        self.Back.clicked.connect(app.RoomMove10)
        self.addWidget(self.Back)


        QTimer.singleShot(0, self.update_table)  # Automatický fetch po zobrazení

    def update_table(self):
        self.worker = FetchRoomsWorker()
        self.worker.rooms_fetched.connect(self.populate_table)
        self.worker.start()

    def populate_table(self, rooms):
        self.table.setRowCount(len(rooms))
        for i, room in enumerate(rooms):
            room_id = QTableWidgetItem(str(room["id"]))
            score = QTableWidgetItem(str(room["score"]))
            guess = QTableWidgetItem(str(room["guess_number"]))
            completed = QTableWidgetItem(str(room["completed"]))

            for item in (room_id, score, guess, completed):
                item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(i, 0, room_id)
            self.table.setItem(i, 1, score)
            self.table.setItem(i, 2, guess)
            self.table.setItem(i, 3, completed)


    def fetch_rooms(self):
        parseRooms = requests.get(f"http://localhost:8081/rooms")
        output = parseRooms.json()
        return output


class Widget(QWidget):

    DEFAULT_MIN = 1
    DEFAULT_MAX = 10

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rooms = {}
        self.selected_room = None
        self.selected_room_name = None

        self.text_widget = QLabel("vysledek", alignment=Qt.AlignCenter)
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.guess)

        self.submit_button = QPushButton("potvrdit")
        self.submit_button.clicked.connect(self.guess)

        # self.content_layout = QVBoxLayout()
        # self.content_layout.addWidget(self.text_widget)

        self.text = QVBoxLayout()
        self.text.addWidget(self.line_edit)

        self.input_text = QWidget()
        self.input_text.setLayout(self.text)

        self.welcome_screen = WelcomeScreen(self)

        self.WSWidget = QWidget()
        self.WSWidget.setLayout(self.welcome_screen)
        self.WSWidget.setAutoFillBackground(True)

        self.room_list_screen = RoomSelection(self)
        
        self.RLWidget = QWidget()
        self.RLWidget.setLayout(self.room_list_screen.generated_rooms)
        self.RLWidget.setAutoFillBackground(True)
        self.RLWidget.hide()

        self.number_range_screen = NumberRangeSelect(self)

        self.NRWidget = QWidget()
        self.NRWidget.setLayout(self.number_range_screen)
        self.NRWidget.setAutoFillBackground(True)
        self.NRWidget.hide()

        self.MainMenuLayout = MainMenu(self)
        
        self.MMWidget = QWidget()
        self.MMWidget.setLayout(self.MainMenuLayout)
        self.MMWidget.setAutoFillBackground(True)
        self.MMWidget.hide()

        self.GFLayout = GameField(self)

        self.GFWidget = QWidget()
        self.GFWidget.setLayout(self.GFLayout)
        self.GFWidget.setAutoFillBackground(True)
        self.GFWidget.hide()

        self.HSLayout = HighScore(self)

        self.HSWidget = QWidget()
        self.HSWidget.setLayout(self.HSLayout)
        self.HSWidget.setAutoFillBackground(True)
        self.HSWidget.hide()

        self.MainLayout = QHBoxLayout()
        self.MainLayout.addWidget(self.WSWidget)
        self.MainLayout.addWidget(self.MMWidget)
        self.MainLayout.addWidget(self.RLWidget)
        self.MainLayout.addWidget(self.NRWidget)
        self.MainLayout.addWidget(self.GFWidget)
        self.MainLayout.addWidget(self.HSWidget)

        self.setLayout(self.MainLayout)

    def switch_screen(self, before, to):
        before.hide()
        to.show()

    def roomgen(self):
        min_number = int(self.number_range_screen.minNumber.text()) if self.number_range_screen.minNumber.text().isnumeric() else self.DEFAULT_MIN
        max_number = int(self.number_range_screen.maxNumber.text()) if self.number_range_screen.maxNumber.text().isnumeric() else self.DEFAULT_MAX

        parse = requests.post("http://localhost:8081/create", json = {"min": min_number, "max": max_number})
        room_number = parse.text
        room_name = f"mistnost {room_number}"
        self.rooms[room_name] = {}
        self.rooms[room_name]["GUESSLOG"] = []
        self.rooms[room_name]["ID"] = parse.text
        self.rooms[room_name]["OUTPUT"] = room_name + "\nvysledek"
        item = QListWidgetItem(room_name)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("calibri", 15))
        self.room_list_screen.menu_widget.addItem(item)
        self.RoomMove8()

    def guess(self):
        guessed_number = self.GFLayout.line_edit.text()
        current_text = self.GFLayout.text_widget.text()
        print("pressed")
        if guessed_number in self.rooms[self.selected_room_name]["GUESSLOG"]:
            msg = f"Cislo {guessed_number} jsi uz hadal"
            self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
            self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
            self.GFLayout.line_edit.setText("")
            return
        self.rooms[self.selected_room_name]["GUESSLOG"].append(guessed_number)

        parse = requests.get(f"http://localhost:8081/guess?room_id={self.selected_room}&number={guessed_number}")

        answer = parse.json()
        match answer["status"]:
            case "bigger":
                msg = f"{guessed_number} je vetsi, nez hadane cislo"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
            case "lesser":
                msg = f"{guessed_number} je mensi, nez hadane cislo"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
            case "found":
                msg = "Uhodl jsi cislo. Budes nasledne navracen do menu"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
                QCoreApplication.processEvents()
                self.room_list_screen.menu_widget.takeItem(self.room_list_screen.menu_widget.currentRow())
                time.sleep(5)
                self.RoomMove5()
            case "lost":
                msg = "Nedokazal jsi uhodnout cislo. Budes nasledne navracen do menu"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
                QCoreApplication.processEvents()
                self.room_list_screen.menu_widget.takeItem(self.room_list_screen.menu_widget.currentRow())
                time.sleep(5)
                self.RoomMove5()
            case "NaN":
                msg = f"{guessed_number} neni cislo"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"

        # self.text_widget.setText(f"{current_text}\n{msg}")
        self.GFLayout.line_edit.setText("")
        print(parse.text)

    def on_selected(self, item):
        room_name = item.text()
        room_id = self.rooms[room_name]["ID"]
        self.GFLayout.text_widget.setText(self.rooms[room_name]["OUTPUT"])
        self.selected_room = room_id
        self.selected_room_name = room_name
        #self.main_widget.setVisible(True)
        self.RoomMove6()

    def start(self):
        self.StartMenu.setVisible(False)
        self.gentext.setVisible(True)
        
    def RoomMove1(self):
        self.switch_screen(self.WSWidget, self.MMWidget)
    def RoomMove2(self):
        self.switch_screen(self.MMWidget, self.RLWidget)
    def RoomMove3(self):
        self.switch_screen(self.MMWidget, self.GFWidget)
    def RoomMove4(self):
        self.switch_screen(self.RLWidget, self.MMWidget)
    def RoomMove5(self):
        self.switch_screen(self.GFWidget, self.MMWidget)
    def RoomMove6(self):
        self.switch_screen(self.RLWidget, self.GFWidget)
    def RoomMove7(self):
        self.switch_screen(self.RLWidget, self.NRWidget)
    def RoomMove8(self):
        self.switch_screen(self.NRWidget, self.RLWidget)
    def RoomMove9(self):
        self.HSLayout.update_table()
        self.switch_screen(self.MMWidget, self.HSWidget)
    def RoomMove10(self):
        self.switch_screen(self.HSWidget, self.MMWidget)

if __name__ == "__main__":
    app = QApplication()
    app.setStyleSheet(darkStyleSheet)

    widget = Widget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
