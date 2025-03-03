
# client-test 4 (nejnovejsi)

from ctypes import alignment
import sys
from PySide6.QtCore import QRect, Qt, Slot, QCoreApplication
from PySide6.QtGui import QFont, QPen
from PySide6.QtWidgets import QStackedWidget, QApplication, QGridLayout, QLabel, QLayout, QWidget, QListWidget, QListWidgetItem, \
    QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QGraphicsScene, QMainWindow
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

        # gentext = QWidget()
        # # gentext.setLayout(self.generated_rooms)
        # gentext.setVisible(False)

        self.addWidget(start_menu, 1)
        # self.addWidget(gentext, 1)
        self.addWidget(main_widget, 4)

    def set_on_click(self, on_click):
        self.welcome_button.clicked.connect(on_click)

class RoomSelection(QHBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #self.rooms = {}
        #self.selected_room = None

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
        self.Back.clicked.connect(app.RoomMove4)#(app.MMWidget, app.RLWidget))
        
        self.generated_rooms.addWidget(self.RoomSelectionLabel)
        self.generated_rooms.addWidget(self.menu_widget)
        self.generated_rooms.addWidget(self.generate)
        self.generated_rooms.addWidget(self.Back)
        
        self.gentext.setLayout(self.generated_rooms)

class NumberRangeSelect(QVBoxLayout):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.NumberRangeSelectLabel = QLabel("Vytvorit mistnost", alignment=Qt.AlignCenter, font=QFont("calibri", 30))
        
        self.minNumberText = QLabel("Minimalni cislo", alignment=Qt.AlignCenter, font=QFont("calibri", 25))
        self.minNumber = QLineEdit(font=QFont("calibri", 20))
        self.minNumber.setPlaceholderText("1")
        
        self.maxNumberText = QLabel("Maximalni cislo", alignment=Qt.AlignCenter, font=QFont("calibri", 25))
        self.maxNumber = QLineEdit(font=QFont("calibri", 20))
        self.maxNumber.setPlaceholderText("11")

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
        self.generate.clicked.connect(app.roomgen)

        self.addWidget(self.NumberRangeSelectLabel)
        self.addWidget(self.horizontalSplitWidget)
        self.addWidget(self.generate)

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
        self.Back.clicked.connect(app.RoomMove5)#(app.MMWidget, app.RLWidget))

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
        self.RoomList.clicked.connect(app.RoomMove2)#(app.MMWidget, app.RLWidget))

        #self.GameField = QPushButton("Hraci pole")
        #self.GameField.clicked.connect(app.RoomMove3)#(app.MMWidget, app.RLWidget))
        
        self.addWidget(self.MainMenuLabel)
        self.addWidget(self.RoomList)
        #self.addWidget(self.GameField)

class Widget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rooms = {}
        self.selected_room = None
        self.selected_room_name = None

        #self.menu_widget = QListWidget()
        #self.menu_widget.itemClicked.connect(self.on_selected)

        # self.welcome_font = QFont("calibri", 100)
        #
        # self.welcome = QLabel("Vitej!", alignment=Qt.AlignCenter)
        # self.welcome.setFont(self.welcome_font)
        # self.welcome_button = QPushButton("zacit")
        # self.welcome_button.clicked.connect(self.start)

        #self.generate = QPushButton("generovat")
        #self.generate.clicked.connect(self.roomgen)
        #self.generated_rooms = QVBoxLayout()
        #self.generated_rooms.addWidget(self.menu_widget)
        #self.generated_rooms.addWidget(self.generate)

        ##
        #self.gentext = QWidget()
        #self.gentext.setLayout(self.generated_rooms)
        #self.gentext.setVisible(False)

        self.text_widget = QLabel("vysledek", alignment=Qt.AlignCenter)
        self.line_edit = QLineEdit()
        self.line_edit.returnPressed.connect(self.guess)

        self.submit_button = QPushButton("potvrdit")
        self.submit_button.clicked.connect(self.guess)

        # self.content_layout = QVBoxLayout()
        # self.content_layout.addWidget(self.text_widget)

        self.text = QVBoxLayout()
        self.text.addWidget(self.line_edit)
        # self.text.addWidget(self.button)

        self.input_text = QWidget()
        self.input_text.setLayout(self.text)
        # self.content_layout.addWidget(self.input_text)
        ###
        # self.main_widget = QWidget()
        # self.main_widget.setLayout(self.content_layout)
        # self.main_widget.setVisible(False)

        ##
        # self.start_layout = QVBoxLayout()
        # self.spacer = QWidget()
        # self.start_layout.addWidget(self.spacer)
        # self.start_layout.addWidget(self.welcome)
        # self.start_layout.addWidget(self.welcome_button)
        # self.start_layout.addWidget(self.spacer)

        ##
        # self.StartMenu = QWidget()
        # self.StartMenu.setLayout(self.start_layout)
        #
        # ####
        # self.menu_layout = QHBoxLayout()
        # self.menu_layout.addWidget(self.StartMenu, 1)
        # self.menu_layout.addWidget(self.gentext, 1)
        # self.menu_layout.addWidget(self.main_widget, 4)

        #self.empty = QListWidget()
        #
        #self.EmptyLayout = QVBoxLayout()
        #self.EmptyLayout.addWidget(self.empty)
        #
        #self.EmptyWidget = QWidget()
        #self.EmptyWidget.setLayout(self.EmptyLayout)
        #self.EmptyWidget.setAutoFillBackground(True)

        self.welcome_screen = WelcomeScreen(self)
        #self.welcome_screen.set_on_click(self.RoomMove)
        
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
        
        self.MainLayout = QHBoxLayout()
        self.MainLayout.addWidget(self.WSWidget)
        self.MainLayout.addWidget(self.MMWidget)
        self.MainLayout.addWidget(self.RLWidget)
        self.MainLayout.addWidget(self.NRWidget)
        self.MainLayout.addWidget(self.GFWidget)

        self.setLayout(self.MainLayout)

    #def show_rooms(self):
    #    #QLayout.removeWidget(self.welcome_screen)
    #    #self.welcome_screen.deleteLater()
    #    #self.MainLayout.removeWidget(self.WSWidget)
    #    self.room_list_screen = RoomSelection(self)
    #    self.RLWidget = QWidget()
    #    self.RLWidget.setLayout(self.room_list_screen.generated_rooms)
    #    #self.MainLayout.addWidget(self.RLWidget)
    #    self.MainLayout.replaceWidget(self.WSWidget, self.RLWidget)
    #    #self.setLayout(room_list_screen.generated_rooms)
    #    #self.update(0, 0, 1920, 1080)
    #    #self.show()
    #    print("funguje")

    def switch_screen(self, before, to):
        before.hide()
        to.show()
        #self.MainLayout.replaceWidget(before, to)
        #self.MainLayout.replaceWidget(self.EmptyWidget, to)
        #self.MainLayout = QWidget()
        #self.MainLayout.setLayout(self.WSWidget, self.MMWidget)
        
    def roomgen(self):
        min_number = self.number_range_screen.minNumber.text()
        max_number = self.number_range_screen.maxNumber.text()
        parse = requests.post("http://localhost:8080/create", json = {"min": min_number, "max": max_number})
        room_number = len(self.rooms) + 1
        room_name = f"mistnost {room_number}"
        self.rooms[room_name] = {}
        self.rooms[room_name]["ID"] = parse.text
        self.rooms[room_name]["OUTPUT"] = room_name + "\nvysledek"
        item = QListWidgetItem(room_name)
        item.setTextAlignment(Qt.AlignCenter)
        item.setFont(QFont("calibri", 15))
        self.room_list_screen.menu_widget.addItem(item)
        self.RoomMove8()

    def guess(self):
        guessed_number = self.GFLayout.line_edit.text()
        parse = requests.get(f"http://localhost:8080/guess?room_id={self.selected_room}&number={guessed_number}")
        print("pressed")
        current_text = self.GFLayout.text_widget.text()
        # if parse.text == "MENSI":
        #    msg = "Hledane cislo je mensi"
        # elif parse.text == "VETSI":
        #    msg = "Hledane cislo je vetsi"
        # else:
        #    ...
        answer = parse.json()
        match answer["status"]:
            case "bigger":
                msg = "Zadane cislo je vetsi"
                self.GFLayout.text_widget.setText(f"{current_text}\n{msg}")
                self.rooms[self.room_list_screen.menu_widget.currentItem().text()]["OUTPUT"] = f"{current_text}\n{msg}"
            case "lesser":
                msg = "Zadane cislo je mensi"
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
                #self.main_widget.setVisible(False)
                # self.text_widget.setText("output")
            case "NaN":
                msg = f"\"{guessed_number}\" neni cislo"
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

if __name__ == "__main__":
    app = QApplication()
    app.setStyleSheet(darkStyleSheet)

    widget = Widget()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
