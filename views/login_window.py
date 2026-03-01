from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame, QScrollArea
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
import sqlite3
import os
from views.product_list import ProductListWindow
from views.client_view import ClientView
from views.manager_view import ManagerView
from views.admin_view import AdminView
from database.import_from_excel import import_all_data
from database.init_db import create_database

class LoginWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.initUI()
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #7FFF00;
                border-radius: 6px;
                font-size: 13px;
                background-color: #FFFFFF;
            }
            QLineEdit:focus {
                border: 2px solid #00FA9A;
            }
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 12px;
                border: none;
                border-radius: 6px;
                font-size: 13px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
            QPushButton.guest-btn {
                background-color: #00FA9A;
            }
            QPushButton.guest-btn:hover {
                background-color: #7FFF00;
            }
            QPushButton.danger {
                background-color: #ff6b6b;
            }
            QPushButton.danger:hover {
                background-color: #ff5252;
            }
            QPushButton.accent {
                background-color: #00FA9A;
            }
            QPushButton.accent:hover {
                background-color: #7FFF00;
            }
            QFrame {
                background-color: transparent;
                border: none;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # Главный горизонтальный layout
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ЛЕВАЯ ПАНЕЛЬ - логотип и название
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #7FFF00;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(30, 40, 30, 40)
        left_layout.setSpacing(20)
        left_layout.setAlignment(Qt.AlignCenter)
        
        # Логотип
        logo_label = QLabel()
        pixmap = QPixmap('assets/logo.png')
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        
        # Название компании
        title = QLabel("ООО Обувь")
        title.setFont(QFont('Times New Roman', 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #000000; line-height: 1.2;")
        left_layout.addWidget(title, alignment=Qt.AlignCenter)
        
        left_layout.addStretch()
        main_layout.addWidget(left_panel, 1)
        
        # ПРАВАЯ ПАНЕЛЬ - форма входа
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(50, 40, 50, 40)
        right_layout.setSpacing(20)
        right_layout.setAlignment(Qt.AlignCenter)
        
        # Используем скролл для правой панели
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("border: none; background-color: white;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # Заголовок "Вход в систему"
        login_header = QLabel("Вход в систему")
        login_header.setFont(QFont('Times New Roman', 22, QFont.Bold))
        login_header.setAlignment(Qt.AlignCenter)
        login_header.setStyleSheet("color: #2E8B57;")
        scroll_layout.addWidget(login_header)
        
        # Поля ввода
        login_label_text = QLabel("Логин:")
        login_label_text.setFont(QFont('Times New Roman', 12, QFont.Bold))
        scroll_layout.addWidget(login_label_text)
        
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите ваш логин")
        self.login_input.setMinimumHeight(40)
        scroll_layout.addWidget(self.login_input)
        
        password_label_text = QLabel("Пароль:")
        password_label_text.setFont(QFont('Times New Roman', 12, QFont.Bold))
        scroll_layout.addWidget(password_label_text)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите ваш пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(40)
        scroll_layout.addWidget(self.password_input)
        
        # Кнопки входа
        login_button = QPushButton("Войти")
        login_button.setMinimumHeight(45)
        login_button.setStyleSheet("background-color: #7FFF00;")
        login_button.clicked.connect(self.login)
        scroll_layout.addWidget(login_button)
        
        guest_button = QPushButton("Войти как гость")
        guest_button.setMinimumHeight(45)
        guest_button.setProperty("class", "guest-btn")
        guest_button.clicked.connect(self.login_as_guest)
        scroll_layout.addWidget(guest_button)
        
        # Разделитель
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("background-color: #7FFF00; max-height: 2px; margin: 10px 0px;")
        scroll_layout.addWidget(separator1)
        
        # Управление БД
        db_header = QLabel("Управление базой данных")
        db_header.setFont(QFont('Times New Roman', 22, QFont.Bold))
        db_header.setAlignment(Qt.AlignCenter)
        db_header.setStyleSheet("color: #2E8B57; margin-top: 15px;")
        scroll_layout.addWidget(db_header)
        
        # Кнопки управления БД
        db_button_layout = QHBoxLayout()
        db_button_layout.setSpacing(10)
        
        import_btn = QPushButton("Импорт")
        import_btn.setProperty("class", "accent")
        import_btn.clicked.connect(self.import_data)
        db_button_layout.addWidget(import_btn)
        
        clear_btn = QPushButton("Очистить")
        clear_btn.setProperty("class", "danger")
        clear_btn.clicked.connect(self.clear_database)
        db_button_layout.addWidget(clear_btn)
        
        scroll_layout.addLayout(db_button_layout)
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        right_layout.addWidget(scroll)
        
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
    
    def login(self):
        login = self.login_input.text()
        password = self.password_input.text()
        
        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, full_name, role FROM Users WHERE login=? AND password=?", (login, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_data = {'id': user[0], 'name': user[1], 'role': user[2]}
                self.main_app.set_user(user_data)
                
                if user[2] == 'admin':
                    self.main_app.stacked_widget.addWidget(AdminView(self.main_app))
                    self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
                elif user[2] == 'manager':
                    self.main_app.stacked_widget.addWidget(ManagerView(self.main_app))
                    self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
                else:
                    self.main_app.stacked_widget.addWidget(ClientView(self.main_app))
                    self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
            else:
                QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка базы данных", str(e))
    
    def login_as_guest(self):
        user_data = {'id': None, 'name': 'Гость', 'role': 'guest'}
        self.main_app.set_user(user_data)
        self.main_app.stacked_widget.addWidget(ProductListWindow(self.main_app))
        self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)
    
    def import_data(self):
        if not os.path.exists('db_init'):
            QMessageBox.warning(self, "Ошибка", "Папка 'db_init' не найдена")
            return
        
        required_files = ['pick_points.xlsx', 'products.xlsx', 'users.xlsx', 'orders.xlsx']
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join('db_init', file)):
                missing_files.append(file)
        
        if missing_files:
            QMessageBox.warning(self, "Ошибка", 
                               f"Отсутствуют файлы:\n{', '.join(missing_files)}\n\n"
                               "Поместите все файлы в папку 'db_init'")
            return
        
        reply = QMessageBox.question(
            self, 
            "Подтверждение",
            "Импорт данных из Excel файлов.\n\n"
            "ВНИМАНИЕ: Все существующие данные будут заменены!\n\n"
            "Продолжить?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        try:
            create_database()
            success = import_all_data()
            
            if success:
                QMessageBox.information(self, "Успех", 
                                      "Данные успешно импортированы из Excel файлов!")
                if os.path.exists('db_initialized.flag'):
                    os.remove('db_initialized.flag')
            else:
                QMessageBox.critical(self, "Ошибка", 
                                   "Произошла ошибка при импорте данных.\n"
                                   "Проверьте консоль для подробностей.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при импорте: {str(e)}")
    
    def clear_database(self):
        reply = QMessageBox.question(
            self, 
            "Подтверждение",
            "ОЧИСТКА БАЗЫ ДАННЫХ\n\n"
            "ВНИМАНИЕ: Все данные будут безвозвратно удалены!\n\n"
            "Вы уверены?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.No:
            return
        
        reply2 = QMessageBox.question(
            self, 
            "Последнее подтверждение",
            "Это последнее предупреждение!\n"
            "Все товары, заказы и пользователи будут удалены.\n\n"
            "Точно продолжить?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply2 == QMessageBox.No:
            return
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            cursor.execute("PRAGMA foreign_keys = OFF")
            
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':
                    try:
                        cursor.execute(f"DELETE FROM {table_name}")
                    except Exception as e:
                        print(f"Ошибка при очистке {table_name}: {e}")
            
            cursor.execute("DELETE FROM sqlite_sequence")
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            conn.close()
            
            if os.path.exists('db_initialized.flag'):
                os.remove('db_initialized.flag')
            
            QMessageBox.information(self, "Успех", "База данных успешно очищена!")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при очистке БД: {str(e)}")