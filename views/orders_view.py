from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPixmap
from views.header import HeaderWidget
import sqlite3
import os

class OrdersView(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.initUI()
        self.load_orders()
        
    def initUI(self):
        self.setWindowTitle("ООО Обувь - Управление заказами")
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
            }
            QTableWidget {
                border: 1px solid #CCCCCC;
                gridline-color: #EEEEEE;
                background-color: #FFFFFF;
            }
            QTableWidget::item {
                padding: 8px;
                border-right: 1px solid #EEEEEE;
            }
            QHeaderView::section {
                background-color: #2E8B57;
                color: #FFFFFF;
                padding: 10px;
                border: none;
                border-right: 1px solid #FFFFFF;
                font-weight: bold;
            }
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
            QPushButton.admin {
                background-color: #00FA9A;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Создаем верхнюю панель
        header = HeaderWidget("Управление заказами", self.main_app, show_logo=True, show_back_btn=True)
        header.logout_clicked.connect(self.logout)
        header.back_clicked.connect(self.go_back)
        main_layout.addWidget(header)
        
        if self.main_app.current_user['role'] == 'admin':
            admin_layout = QHBoxLayout()
            
            add_btn = QPushButton("Добавить заказ")
            add_btn.setProperty("class", "admin")
            add_btn.clicked.connect(self.add_order)
            admin_layout.addWidget(add_btn)
            
            admin_layout.addStretch()
            main_layout.addLayout(admin_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Артикул заказа", "Клиент", "Статус", "Адрес выдачи", 
            "Дата заказа", "Дата выдачи", "Состав заказа"
        ])
        
        # Настройки таблицы
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)
        
        table_header = self.table.horizontalHeader()
        table_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        for i in range(1, 8):
            table_header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        if self.main_app.current_user['role'] == 'admin':
            self.table.setSelectionBehavior(self.table.SelectRows)
            self.table.itemDoubleClicked.connect(self.edit_order)
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
    
    def load_orders(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT o.order_id, o.order_article, u.full_name, o.status, 
                       p.address, o.order_date, o.issue_date
                FROM Orders o
                JOIN Users u ON o.user_id = u.user_id
                JOIN PickupPoints p ON o.pickup_point_id = p.pickup_point_id
                ORDER BY o.order_date DESC
            """)
            orders = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(orders))
            
            for row, order in enumerate(orders):
                order_id, article, client, status, address, order_date, issue_date = order
                
                self.table.setItem(row, 0, QTableWidgetItem(str(order_id)))
                self.table.setItem(row, 1, QTableWidgetItem(article))
                self.table.setItem(row, 2, QTableWidgetItem(client))
                self.table.setItem(row, 3, QTableWidgetItem(self.get_status_text(status)))
                self.table.setItem(row, 4, QTableWidgetItem(address))
                self.table.setItem(row, 5, QTableWidgetItem(order_date))
                self.table.setItem(row, 6, QTableWidgetItem(issue_date or ""))
                
                items_text = self.parse_order_items(article)
                self.table.setItem(row, 7, QTableWidgetItem(items_text))
                
                # Установка высоты строки
                self.table.setRowHeight(row, 50)
                
                # Применяем фоновые цвета в зависимости от статуса заказа
                if status == 'completed':
                    # Завершённый заказ - зелёный
                    for col in range(8):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(46, 139, 87))
                elif status == 'cancelled':
                    # Отменённый заказ - светло-розовый
                    for col in range(8):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 182, 193))
                elif status == 'new':
                    # Новый заказ - светло-жёлтый
                    for col in range(8):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(255, 255, 200))
                else:
                    # Остальные статусы - чередование цветов
                    if row % 2 == 0:
                        row_color = QColor(245, 248, 250)  # Светло-голубой
                    else:
                        row_color = QColor(255, 255, 255)  # Белый
                    
                    for col in range(8):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(row_color)
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить заказы: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def parse_order_items(self, order_article):
        try:
            parts = order_article.split(', ')
            items = []
            for i in range(0, len(parts), 2):
                if i + 1 < len(parts):
                    article = parts[i]
                    quantity = parts[i + 1]
                    
                    conn = sqlite3.connect('shoe_store.db')
                    cursor = conn.cursor()
                    cursor.execute("SELECT product_name FROM Products WHERE article=?", (article,))
                    result = cursor.fetchone()
                    conn.close()
                    
                    if result:
                        items.append(f"{result[0]} x{quantity}")
                    else:
                        items.append(f"{article} x{quantity}")
            return '\n'.join(items)
        except:
            return order_article
    
    def get_status_text(self, status):
        statuses = {
            'new': 'Новый',
            'processing': 'В обработке',
            'completed': 'Выполнен',
            'cancelled': 'Отменен'
        }
        return statuses.get(status, status)
    
    def add_order(self):
        from views.order_edit import OrderEditWindow
        self.edit_window = OrderEditWindow(self.main_app, None, self)
        self.edit_window.show()
    
    def edit_order(self, item):
        row = item.row()
        order_id = int(self.table.item(row, 0).text())
        from views.order_edit import OrderEditWindow
        self.edit_window = OrderEditWindow(self.main_app, order_id, self)
        self.edit_window.show()
    
    def refresh_orders(self):
        self.load_orders()
    
    def go_back(self):
        self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.currentIndex() - 1)
    
    def logout(self):
        self.main_app.logout()