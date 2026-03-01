from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtGui import QPalette, QBrush


class HeaderWidget(QWidget):
    """Единый компонент верхней панели для всех форм приложения"""
    logout_clicked = pyqtSignal()
    back_clicked = pyqtSignal()
    
    def __init__(self, title, main_app, show_logo=True, show_back_btn=False):
        super().__init__()
        self.title_text = title
        self.main_app = main_app
        self.show_logo = show_logo
        self.show_back_btn = show_back_btn
        self.initUI()
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)
        
        # ============ ПЕРВАЯ СТРОКА - ЗАГОЛОВОК И ВЫХОД ============
        top_layout = QHBoxLayout()
        top_layout.setSpacing(20)
        
        title_label = QLabel(self.title_text)
        title_label.setFont(QFont('Times New Roman', 24, QFont.Bold))
        title_label.setStyleSheet("color: #2E8B57;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_layout.addWidget(title_label)
        
        top_layout.addStretch()
        
        # Кнопка "Выход"
        logout_btn = QPushButton("Выход")
        logout_btn.setMaximumHeight(32)
        logout_btn.setMaximumWidth(100)
        logout_btn.setFont(QFont('Times New Roman', 11))
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: black;
                padding: 6px;
                border: 2px solid #333333;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
            QPushButton:pressed {
                background-color: #e8e8e8;
            }
        """)
        logout_btn.clicked.connect(self.logout_clicked.emit)
        top_layout.addWidget(logout_btn)
        
        main_layout.addLayout(top_layout)
        
        # ============ ВТОРАЯ СТРОКА - ИНФОРМАЦИЯ О ПОЛЬЗОВАТЕЛЕ И ДРУГИЕ КНОПКИ ============
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        # Информация о пользователе слева
        user_name = self.main_app.current_user.get('name', 'Пользователь')
        user_role = self.main_app.current_user.get('role', 'Клиент')
        
        user_info_label = QLabel(f"Пользователь: {user_name} ({user_role})")
        user_info_label.setFont(QFont('Times New Roman', 10))
        user_info_label.setAlignment(Qt.AlignLeft)
        bottom_layout.addWidget(user_info_label)
        
        bottom_layout.addStretch()
        
        # Кнопка "Назад"
        if self.show_back_btn:
            back_btn = QPushButton("← Назад")
            back_btn.setMaximumHeight(28)
            back_btn.setMaximumWidth(100)
            back_btn.setFont(QFont('Times New Roman', 10))
            back_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7FFF00;
                    color: black;
                    padding: 5px;
                    border: none;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #00FA9A;
                }
                QPushButton:pressed {
                    background-color: #6FEE90;
                }
            """)
            back_btn.clicked.connect(self.back_clicked.emit)
            bottom_layout.addWidget(back_btn)
        
        main_layout.addLayout(bottom_layout)
        
        # Установить зеленый акцент в виде нижней границы без белого фона
        self.setStyleSheet("""
            HeaderWidget {
                background-color: transparent;
                border-bottom: 3px solid #7FFF00;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        self.setLayout(main_layout)
        self.setMinimumHeight(85)
