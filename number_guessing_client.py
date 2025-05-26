
# client-test 4 (nejnovejsi)

import code
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

        welcome = QLabel("Vítej!", alignment=Qt.AlignCenter)
        welcome.setFont(welcome_font)
        self.welcome_button = QPushButton("Začít", font=QFont("calibri", 15))
        self.welcome_button.setMinimumSize(150, 50)
        self.welcome_button.clicked.connect(app.RoomMove_WelcomeScreenToMainMenu)

        self.login_button = QPushButton("Přihlásit se", font=QFont("calibri", 15))
        self.login_button.setMinimumSize(150, 50)
        self.login_button.clicked.connect(app.RoomMove_WelcomeScreenToLogin)

        start_layout.addWidget(welcome)
        start_layout.addWidget(self.welcome_button)
        start_layout.addWidget(self.login_button)
        start_layout.addWidget(spacer)

        text_widget = QLabel("výsledek", alignment=Qt.AlignCenter)

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

class LoginScreen(QVBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        spacer = QWidget()

        self.LoginLabel = QLabel("Přihlášení", alignment=Qt.AlignCenter, font=QFont("calibri", 50))

        self.Email = QLineEdit(alignment=Qt.AlignCenter, font=QFont("calibri", 20))
        self.Email.setPlaceholderText("Zadejte e-mail")

        self.EmailCode = QLineEdit(alignment=Qt.AlignCenter, font=QFont("calibri", 20))
        self.EmailCode.setPlaceholderText("Zadejte kód z e-mailu")
        self.EmailCode.hide()

        self.Confirm = QPushButton("Potvrdit", font=QFont("calibri", 15))
        self.Confirm.setMinimumSize(150, 30)
        self.Confirm.clicked.connect(self.OnEmailConfirm)

        self.Back = QPushButton("zpět", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 30)
        self.Back.clicked.connect(app.RoomMove_LoginToWelcomeScreen)

        self.addWidget(self.LoginLabel)
        self.addWidget(self.Email)
        self.addWidget(self.EmailCode)
        self.addWidget(self.Confirm)
        self.addWidget(self.Back)
        self.addWidget(spacer)

    def OnEmailConfirm(self):
        email = self.Email.text()
        code = self.EmailCode.text()
        if not email:
            print("Zadejte e-mail.")
            return
        try:
            response = requests.post("http://localhost:8081/login", json={"email": email, "code": code})
            if response.status_code == 200:
                print("E-mail odeslán.")
                self.EmailCode.show()
            else:
                print("Chyba při odesílání e-mailu:", response.text)
        except Exception as e:
            print(f"Chyba při komunikaci se serverem: {e}")


class RoomSelection(QHBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app = app
        self.RoomSelectionLabel = QLabel("Seznam místností", alignment=Qt.AlignCenter, font=QFont("calibri", 20))

        self.menu_widget = QListWidget()
        self.menu_widget.itemClicked.connect(app.on_selected)

        self.gentext = QWidget()
        
        self.generate = QPushButton("generovat místnost", font=QFont("calibri", 15))
        self.generate.setMinimumSize(150, 30)
        self.generate.clicked.connect(app.RoomMove_RoomListToNumberRange)
        self.generated_rooms = QVBoxLayout()

        self.Back = QPushButton("zpět", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 30)
        self.Back.clicked.connect(app.RoomMove_RoomListToMainMenu)
        
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
                            "guess_number": room['guess_number'],
                            "GUESSLOG": []
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
        
        self.NumberRangeSelectLabel = QLabel("Vytvořit místnost", alignment=Qt.AlignCenter, font=QFont("calibri", 30))
        
        self.minNumberText = QLabel("Minimální číslo", alignment=Qt.AlignCenter, font=QFont("calibri", 25))
        self.minNumber = QLineEdit(font=QFont("calibri", 20))
        self.minNumber.setValidator(QIntValidator(1, 100))
        self.minNumber.setPlaceholderText(str(Widget.DEFAULT_MIN))

        # TODO - add validator [HOTOVO? Pat a Mat řešení]
        self.maxNumberText = QLabel("Maximální číslo", alignment=Qt.AlignCenter, font=QFont("calibri", 25))
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

        self.generate = QPushButton("generovat místnost", font=QFont("calibri", 15))
        self.generate.setMinimumSize(150, 30)

        self.Back = QPushButton("zpět", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 30)
        self.Back.clicked.connect(app.RoomMove_NumberRangeToRoomList)
        
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
            self.maxNumberError.setText("Maximální číslo musí být větší než minimální")
        else:
            self.maxNumberError.setText("")
            self.app.roomgen()

class GameField(QVBoxLayout):
     def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.GameFieldLabel = QLabel("Herní pole", alignment=Qt.AlignCenter, font=QFont("calibri", 25))

        self.text_widget = QLabel("výsledek", alignment=Qt.AlignCenter, font=QFont("calibri", 15))
        self.line_edit = QLineEdit(font=QFont("calibri", 15))
        self.line_edit.setPlaceholderText("Zadejte hádané číslo")
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

        self.Back = QPushButton("zpět", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 40)
        self.Back.clicked.connect(app.RoomMove_GameFieldToMainMenu)

        self.addWidget(self.GameFieldLabel)
        self.addWidget(self.text_widget)
        self.addWidget(self.input_text)
        self.addWidget(self.Back)

class MainMenu(QVBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.MainMenuLabel = QLabel("Hlavní menu", alignment=Qt.AlignCenter, font=QFont("calibri", 48))

        self.RoomList = QPushButton("Seznam místností", font=QFont("calibri", 15))
        self.RoomList.setMinimumSize(150, 50)
        self.RoomList.clicked.connect(app.RoomMove_MainMenuToRoomList)

        self.HighScore = QPushButton("Score", font=QFont("calibri", 15))
        self.HighScore.setMinimumSize(150, 50)
        self.HighScore.clicked.connect(app.RoomMove_MainMenuToHighscore)

        self.QuitButton = QPushButton("Ukončit", font=QFont("calibri", 15))
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

        self.Back = QPushButton("zpět", font=QFont("calibri", 15))
        self.Back.setMinimumSize(150, 50)
        self.Back.clicked.connect(app.RoomMove_HighscoreToMainMenu)
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

        self.text_widget = QLabel("výsledek", alignment=Qt.AlignCenter)
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

        self.LSLayout = LoginScreen(self)

        self.LSWidget = QWidget()
        self.LSWidget.setLayout(self.LSLayout)
        self.LSWidget.setAutoFillBackground(True)
        self.LSWidget.hide()

        self.MainLayout = QHBoxLayout()
        self.MainLayout.addWidget(self.WSWidget)
        self.MainLayout.addWidget(self.MMWidget)
        self.MainLayout.addWidget(self.RLWidget)
        self.MainLayout.addWidget(self.NRWidget)
        self.MainLayout.addWidget(self.GFWidget)
        self.MainLayout.addWidget(self.HSWidget)
        self.MainLayout.addWidget(self.LSWidget)

        self.setLayout(self.MainLayout)

    def switch_screen(self, before, to):
        before.hide()
        to.show()

    def roomgen(self):
        min_number = int(self.number_range_screen.minNumber.text()) if self.number_range_screen.minNumber.text().isnumeric() else self.DEFAULT_MIN
        max_number = int(self.number_range_screen.maxNumber.text()) if self.number_range_screen.maxNumber.text().isnumeric() else self.DEFAULT_MAX

        parse = requests.post("http://localhost:8081/create", json = {"min": min_number, "max": max_number})
        room_number = parse.text
        room_name = f"místnost {room_number}"
        self.rooms[room_name] = {}
        self.rooms[room_name]["GUESSLOG"] = []
        self.rooms[room_name]["ID"] = parse.text
        self.rooms[room_name]["OUTPUT"] = room_name + "\nvysledek"
        item = QListWidgetItem(room_name)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("calibri", 15))
        self.room_list_screen.menu_widget.addItem(item)
        self.RoomMove_NumberRangeToRoomList()

    def guess(self):
        guessed_number = self.GFLayout.line_edit.text()
        current_text = self.GFLayout.text_widget.text()
        print("pressed")

        if guessed_number in self.rooms[self.selected_room_name]["GUESSLOG"]:
            msg = f"Číslo {guessed_number} jsi už hádal"
            self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
            self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
            self.GFLayout.line_edit.setText("")
            return
        
        parse = requests.get(f"http://localhost:8081/guess?room_id={self.selected_room}&number={guessed_number}")
        self.rooms[self.selected_room_name]["GUESSLOG"].append(guessed_number)
        
        try:
            answer = parse.json()
        except Exception as e:
            print("Server nevrátil validní JSON. Odpověď:\n", parse.text)
            return
        match answer["status"]:
            case "bigger":
                msg = f"{guessed_number} je větší, než hádané číslo"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
            case "lesser":
                msg = f"{guessed_number} je menší, než hádané číslo"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
            case "found":
                msg = "Uhodl jsi číslo. Budeš následně navrácen do menu"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
                QCoreApplication.processEvents()
                self.room_list_screen.menu_widget.takeItem(self.room_list_screen.menu_widget.currentRow())
                time.sleep(5)
                self.RoomMove_GameFieldToMainMenu()
            case "lost":
                msg = "Nedokázal jsi uhodnout číslo. Budeš následně navrácen do menu"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
                QCoreApplication.processEvents()
                self.room_list_screen.menu_widget.takeItem(self.room_list_screen.menu_widget.currentRow())
                time.sleep(5)
                self.RoomMove_GameFieldToMainMenu()
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
        response = requests.get(f"http://localhost:8081/logs?room_id={room_id}")
        if response.status_code == 200:
            print("Záznamy úspěšně načteny.")
            data = response.json()
            self.rooms[room_name]["GUESSLOG"] = []
            for i in data:
                self.rooms[room_name]["GUESSLOG"].append(str(i["guess"]))
        else:
            print(f"Chyba při načítání záznamů:", response.text)
            self.rooms[room_name]["GUESSLOG"] = []

        self.GFLayout.text_widget.setText(self.rooms[room_name]["OUTPUT"])
        self.selected_room = room_id
        self.selected_room_name = room_name
        self.RoomMove_RoomListToGameField()

    def start(self):
        self.StartMenu.setVisible(False)
        self.gentext.setVisible(True)
        
    def RoomMove_WelcomeScreenToMainMenu(self):
        self.switch_screen(self.WSWidget, self.MMWidget)
    def RoomMove_MainMenuToRoomList(self):
        self.switch_screen(self.MMWidget, self.RLWidget)
    #def RoomMove3(self):
    #    self.switch_screen(self.MMWidget, self.GFWidget)
    def RoomMove_RoomListToMainMenu(self):
        self.switch_screen(self.RLWidget, self.MMWidget)
    def RoomMove_GameFieldToMainMenu(self):
        self.switch_screen(self.GFWidget, self.MMWidget)
    def RoomMove_RoomListToGameField(self):
        self.switch_screen(self.RLWidget, self.GFWidget)
    def RoomMove_RoomListToNumberRange(self):
        self.switch_screen(self.RLWidget, self.NRWidget)
    def RoomMove_NumberRangeToRoomList(self):
        self.switch_screen(self.NRWidget, self.RLWidget)
    def RoomMove_MainMenuToHighscore(self):
        self.HSLayout.update_table()
        self.switch_screen(self.MMWidget, self.HSWidget)
    def RoomMove_HighscoreToMainMenu(self):
        self.switch_screen(self.HSWidget, self.MMWidget)
    def RoomMove_LoginToWelcomeScreen(self):
        self.switch_screen(self.LSWidget, self.WSWidget)
    def RoomMove_WelcomeScreenToLogin(self):
        self.LSLayout.EmailCode.hide()
        self.LSLayout.Email.setText("")
        self.LSLayout.EmailCode.setText("")
        self.switch_screen(self.WSWidget, self.LSWidget)

if __name__ == "__main__":
    app = QApplication()
    app.setStyleSheet(darkStyleSheet)

    widget = Widget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
