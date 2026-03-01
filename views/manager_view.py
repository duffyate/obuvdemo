from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QTableWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sqlite3
import os
from views.product_list import ProductListWindow
from views.header import HeaderWidget
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtGui import QPixmap, QColor

class ManagerView(ProductListWindow):
    def __init__(self, main_app):
        self.original_products = []
        self.current_sort = None
        self.current_filter = None
        self.current_search = ""
        super().__init__(main_app)
        self.setWindowTitle("ООО Обувь - Менеджер")
        
    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                font-family: 'Times New Roman';
            }
            QLineEdit, QComboBox {
                padding: 8px;
                border: 1px solid #7FFF00;
                border-radius: 4px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 8px 15px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
            QPushButton.orders {
                background-color: #00FA9A;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Создаем верхнюю панель
        header = HeaderWidget("Панель менеджера", self.main_app, show_logo=True)
        header.logout_clicked.connect(self.logout)
        main_layout.addWidget(header)
        
        # ===== ПЕРВАЯ СТРОКА - КНОПКИ ДЕЙСТВИЙ =====
        self.actions_layout = QHBoxLayout()
        self.actions_layout.setSpacing(8)
        
        orders_btn = QPushButton("Заказы")
        orders_btn.setMinimumHeight(32)
        orders_btn.setMaximumWidth(150)
        orders_btn.setProperty("class", "orders")
        orders_btn.setStyleSheet("""
            QPushButton {
                background-color: #7FFF00;
                color: black;
                padding: 6px 12px;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00FA9A;
            }
        """)
        orders_btn.clicked.connect(self.open_orders)
        self.actions_layout.addWidget(orders_btn)
        
        # Дополнительные кнопки будут добавлены в admin_view.py
        self.actions_layout.addStretch()
        
        main_layout.addLayout(self.actions_layout)
        
        # ===== ВТОРАЯ СТРОКА - ФИЛЬТРЫ =====
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(8)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск товаров...")
        self.search_input.setMaximumWidth(200)
        self.search_input.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.search_input)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Без сортировки", "По количеству (возрастание)", "По количеству (убывание)"])
        self.sort_combo.setMaximumWidth(200)
        self.sort_combo.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.sort_combo)
        
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItem("Все поставщики")
        self.supplier_combo.setMaximumWidth(200)
        
        try:
            conn = sqlite3.connect('shoe_store.db')
            cursor = conn.cursor()
            cursor.execute("SELECT supplier_name FROM Suppliers ORDER BY supplier_name")
            suppliers = cursor.fetchall()
            for supplier in suppliers:
                self.supplier_combo.addItem(supplier[0])
            conn.close()
        except:
            pass
        
        self.supplier_combo.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.supplier_combo)
        
        filters_layout.addStretch()
        main_layout.addLayout(filters_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "Фото", "Артикул", "Наименование", "Категория", "Описание", 
            "Производитель", "Поставщик", "Цена", "Ед. изм.",
            "Количество", "Скидка", "Итоговая цена"
        ])
        
        table_header = self.table.horizontalHeader()
        for i in range(12):
            table_header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        main_layout.addWidget(self.table)
        self.setLayout(main_layout)
        
        self.load_original_products()
    
    def load_original_products(self):
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
            self.original_products = cursor.fetchall()
            conn.close()
            print(f"Загружено товаров: {len(self.original_products)}")
            self.display_products(self.original_products)
        except Exception as e:
            print(f"Ошибка загрузки товаров: {e}")
            import traceback
            traceback.print_exc()
    
    def apply_filters(self):
        filtered_products = self.original_products.copy()
        
        search_text = self.search_input.text().lower()
        if search_text:
            filtered_products = [p for p in filtered_products if 
                               search_text in str(p[1]).lower() or  # article
                               search_text in str(p[2]).lower() or  # name
                               search_text in str(p[3]).lower() or  # category
                               search_text in str(p[4] or "").lower() or  # description
                               search_text in str(p[5]).lower() or  # manufacturer
                               search_text in str(p[6]).lower()]    # supplier
        
        selected_supplier = self.supplier_combo.currentText()
        if selected_supplier != "Все поставщики":
            filtered_products = [p for p in filtered_products if p[6] == selected_supplier]
        
        sort_option = self.sort_combo.currentText()
        if sort_option == "По количеству (возрастание)":
            filtered_products.sort(key=lambda x: x[9])
        elif sort_option == "По количеству (убывание)":
            filtered_products.sort(key=lambda x: x[9], reverse=True)
        
        self.display_products(filtered_products)
    
    def display_products(self, products):
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
            
            if discount > 15:
                for col in range(12):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(46, 139, 87))
            
            if quantity == 0:
                for col in range(12):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(173, 216, 230))
    
    def open_orders(self):
        from views.orders_view import OrdersView
        self.main_app.stacked_widget.addWidget(OrdersView(self.main_app))
        self.main_app.stacked_widget.setCurrentIndex(self.main_app.stacked_widget.count() - 1)