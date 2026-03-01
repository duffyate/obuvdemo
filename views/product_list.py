from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QColor
from views.header import HeaderWidget
import sqlite3
import os

class ProductListWindow(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.initUI()
        self.load_products()
        
    def initUI(self):
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
        """)
        
        main_layout = QVBoxLayout()
        
        # Создаем верхнюю панель
        header = HeaderWidget("Каталог товаров", self.main_app, show_logo=True)
        header.logout_clicked.connect(self.logout)
        main_layout.addWidget(header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Фото", "Артикул", "Наименование", "Категория", "Описание", 
            "Производитель", "Поставщик", "Цена", "Ед. изм.",
            "Количество", "Скидка", "Итоговая цена"
        ])
        
        # Настройки таблицы
        self.table.setRowHeight(0, 40)  # Высота заголовка
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.SolidLine)
        
        # Горизонтальный скролл начинает после определённой ширины
        self.table.horizontalHeader().setStretchLastSection(False)
        
        table_header = self.table.horizontalHeader()
        for i in range(12):
            table_header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
    
    def load_products(self):
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.product_id, p.article, p.product_name, c.category_name, p.description,
                       m.manufacturer_name, s.supplier_name, p.price, u.unit_name,
                       p.quantity, p.discount, 
                       ROUND(p.price * (100 - p.discount) / 100, 2) as final_price,
                       p.image_path
                FROM Products p
                JOIN Categories c ON p.category_id = c.category_id
                JOIN Manufacturers m ON p.manufacturer_id = m.manufacturer_id
                JOIN Suppliers s ON p.supplier_id = s.supplier_id
                JOIN Units u ON p.unit_id = u.unit_id
                ORDER BY p.product_id
            """)
            products = cursor.fetchall()
            conn.close()
            
            self.table.setRowCount(len(products))
            
            for row, product in enumerate(products):
                product_id, article, name, category, desc, manufacturer, supplier, price, unit, quantity, discount, final_price, image_path = product
                
                image_label = QLabel()
                if image_path and os.path.exists(os.path.join('product_images', image_path)):
                    pixmap = QPixmap(os.path.join('product_images', image_path))
                elif image_path and os.path.exists(image_path):
                    pixmap = QPixmap(image_path)
                else:
                    pixmap = QPixmap('assets/picture.png')
                
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                self.table.setCellWidget(row, 0, image_label)
                
                self.table.setItem(row, 1, QTableWidgetItem(article))
                self.table.setItem(row, 2, QTableWidgetItem(name))
                self.table.setItem(row, 3, QTableWidgetItem(category))
                self.table.setItem(row, 4, QTableWidgetItem(desc[:50] + "..." if desc and len(desc) > 50 else desc))
                self.table.setItem(row, 5, QTableWidgetItem(manufacturer))
                self.table.setItem(row, 6, QTableWidgetItem(supplier))
                self.table.setItem(row, 7, QTableWidgetItem(f"{price:.2f}"))
                self.table.setItem(row, 8, QTableWidgetItem(unit))
                self.table.setItem(row, 9, QTableWidgetItem(str(quantity)))
                self.table.setItem(row, 10, QTableWidgetItem(f"{discount}%"))
                
                if discount > 0:
                    price_item = QTableWidgetItem(f"{price:.2f}")
                    price_item.setForeground(QColor(255, 0, 0))
                    font = price_item.font()
                    font.setStrikeOut(True)
                    price_item.setFont(font)
                    
                    final_price_item = QTableWidgetItem(f"{final_price:.2f}")
                    final_price_item.setForeground(QColor(0, 0, 0))
                    
                    self.table.setItem(row, 11, final_price_item)
                else:
                    self.table.setItem(row, 11, QTableWidgetItem(f"{price:.2f}"))
                
                # Установка высоты строки
                self.table.setRowHeight(row, 55)
                
                # Применяем фоновые цвета в зависимости от состояния товара
                if discount > 15:
                    # Товар со скидкой > 15%
                    for col in range(12):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(46, 139, 87))
                elif quantity == 0:
                    # Товар отсутствует на складе
                    for col in range(12):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor(173, 216, 230))
                else:
                    # Чередование фонов для обычных товаров
                    if row % 2 == 0:
                        row_color = QColor(245, 248, 250)  # Светло-голубой
                    else:
                        row_color = QColor(255, 255, 255)  # Белый
                    
                    for col in range(12):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(row_color)
        except Exception as e:
            print(f"Ошибка загрузки товаров: {e}")
            import traceback
            traceback.print_exc()
    
    def logout(self):
        self.main_app.logout()