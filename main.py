import sys
import sqlite3
import os
import io
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PyQt5.QtGui import QIcon
from views.login_window import LoginWindow
from database.import_from_excel import import_all_data

# Исправляем кодировку для Windows консоли
if sys.stdout and sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr and sys.stderr.encoding and sys.stderr.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class MainApplication:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon('assets/icon.ico'))
        
        self.init_database()
        
        self.stacked_widget = QStackedWidget()
        self.current_user = None
        
        self.login_window = LoginWindow(self)
        self.stacked_widget.addWidget(self.login_window)
        
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.stacked_widget.setWindowTitle("ООО Обувь")
        self.stacked_widget.setFixedSize(1024, 768)
        self.stacked_widget.show()
    
    def init_database(self):
        """Проверяет наличие базы данных и инициализирует при необходимости"""
        db_path = 'shoe_store.db'
        db_init_dir = 'db_init'
        
        try:
            db_exists = os.path.exists(db_path)
            
            init_flag_path = 'db_initialized.flag'
            
            if not db_exists:
                # При запуске в режиме exe подавляем вывод в консоль
                is_exe = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
                
                if not is_exe:
                    print("=" * 50)
                    print("БАЗА ДАННЫХ НЕ НАЙДЕНА")
                    print("=" * 50)
                
                from database.init_db import create_database
                create_database()
                
                if os.path.exists(db_init_dir):
                    excel_files = ['pick_points.xlsx', 'products.xlsx', 'users.xlsx', 'orders.xlsx']
                    has_all_files = all(os.path.exists(os.path.join(db_init_dir, f)) for f in excel_files)
                    
                    if has_all_files:
                        if not is_exe:
                            print("\nНайдены Excel файлы, импортируем данные...")
                        import_all_data()
                        with open(init_flag_path, 'w') as f:
                            f.write('initialized')
                    else:
                        if not is_exe:
                            print("\nExcel файлы не найдены, используется пустая база данных")
                else:
                    if not is_exe:
                        print("\nПапка db_init не найдена, используется пустая база данных")
            
            elif db_exists and not os.path.exists(init_flag_path) and os.path.exists(db_init_dir):
                is_exe = getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
                
                if not is_exe:
                    print("=" * 50)
                    print("ПЕРВОНАЧАЛЬНЫЙ ИМПОРТ ДАННЫХ")
                    print("=" * 50)
                
                excel_files = ['pick_points.xlsx', 'products.xlsx', 'users.xlsx', 'orders.xlsx']
                has_all_files = all(os.path.exists(os.path.join(db_init_dir, f)) for f in excel_files)
                
                if has_all_files:
                    reply = QMessageBox.question(
                        None, 
                        "Импорт данных",
                        "Обнаружены Excel файлы. Импортировать данные в базу?\n"
                        "Внимание: существующие данные будут заменены!",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    
                    if reply == QMessageBox.Yes:
                        from database.init_db import create_database
                        create_database()
                        import_all_data()
                        with open(init_flag_path, 'w') as f:
                            f.write('initialized')
                    else:
                        if not is_exe:
                            print("Импорт пропущен, используется существующая база")
                        with open(init_flag_path, 'w') as f:
                            f.write('skipped')
                else:
                    if not is_exe:
                        print("Не все Excel файлы найдены, используется существующая база")
                    with open(init_flag_path, 'w') as f:
                        f.write('skipped')
            
            else:
                if not getattr(sys, 'frozen', False):
                    print("Используется существующая база данных")
                
        except Exception as e:
            if not getattr(sys, 'frozen', False):
                print(f"Ошибка при инициализации базы данных: {e}")
                import traceback
                traceback.print_exc()
            QMessageBox.critical(None, "Ошибка", 
                               f"Не удалось инициализировать базу данных:\n{str(e)}")
    
    def run(self):
        sys.exit(self.app.exec_())
    
    def set_user(self, user_data):
        self.current_user = user_data
        
    def logout(self):
        self.current_user = None
        self.stacked_widget.setCurrentWidget(self.login_window)

if __name__ == "__main__":
    app = MainApplication()
    app.run()