import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                             QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QProcess
from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout

from database.db_manager import DatabaseManager
from utils.auth import LoginDialog

from shifting_system.manager_dashboard import ManagerDashboard
from shifting_system.scheduler_interface import SchedulerInterface

from attendance_system.manager_attendance_report import ManagerAttendanceReport

from admin.employee_management import EmployeeManagement

class MainWindow(QMainWindow):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('HR Management System')
        self.setGeometry(100, 100, 1200, 800)
        
        # central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # navigation and content
        content_layout = QHBoxLayout()
        
        # sidebar navigation
        nav_widget = self.create_navigation()
        content_layout.addWidget(nav_widget)
        
        # stacked widget for different screens
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        content_layout.setStretch(0, 1)
        content_layout.setStretch(1, 4)
        
        main_layout.addLayout(content_layout)
        central_widget.setLayout(main_layout)
        
        # load initial screen
        self.load_screens()
    
    def create_header(self):
        header = QWidget()
        header.setStyleSheet('background-color: #2c3e50; padding: 10px;')
        header.setFixedHeight(60)
        
        layout = QHBoxLayout()
        
        title = QLabel('HR Management System')
        title.setStyleSheet('color: white; font-size: 20px; font-weight: bold;')
        
        user_label = QLabel(f"Welcome, {self.user_data['first_name']} {self.user_data['last_name']}")
        user_label.setStyleSheet('color: white; font-size: 14px;')
        user_label.setAlignment(Qt.AlignRight)
        
        logout_btn = QPushButton('Logout')
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(user_label)
        layout.addWidget(logout_btn)
        
        header.setLayout(layout)
        return header
    
    def create_navigation(self):
        nav = QWidget()
        nav.setStyleSheet('background-color: #34495e;')
        nav.setFixedWidth(250)
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # navigation buttons
        buttons = []
        
        # employee features
        if not self.user_data['is_admin']:
            buttons.extend([
                ('Time Clock', 0),
                ('My Roster', 1),
                ('Leave Request', 2)
            ])
        
        # manager features
        if self.user_data['is_admin']:
            buttons.extend([
                ('Manager Dashboard', 3),
                ('Scheduler', 4),
                ('Attendance Report', 5),
                ('Employee Management', 6),
            ])
        
        for btn_text, index in buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2c3e50;
                    color: white;
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #3498db;
                }
            """)
            btn.clicked.connect(lambda checked, i=index: self.stacked_widget.setCurrentIndex(i))
            layout.addWidget(btn)
        
        layout.addStretch()
        nav.setLayout(layout)
        return nav
    
    def load_screens(self):
        # employee screens (0-2)
        #to be develeoped
        
        
        for i in range(3): #placeholder for employee screens
            placeholder = self.create_placeholder_widget(i)
            self.stacked_widget.addWidget(placeholder)

        # manager screens (3-6)
        self.manager_dashboard = ManagerDashboard(self.db_manager, self.user_data)
        self.manager_dashboard.edit_schedule_signal.connect(self.open_scheduler)
        self.stacked_widget.addWidget(self.manager_dashboard)
        
        self.scheduler = SchedulerInterface(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.scheduler)
        
        self.attendance_report = ManagerAttendanceReport(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.attendance_report)
        
        self.employee_mgmt = EmployeeManagement(self.db_manager, self.user_data)
        self.stacked_widget.addWidget(self.employee_mgmt)
        
        # set initial screen
        if self.user_data['is_admin']:
            self.stacked_widget.setCurrentIndex(3)  #manager Dashboard
        else: #if employee
            print("Employee screens to be developed")
            self.stacked_widget.setCurrentIndex(0)  #employee initial screen (to be developed)
    
    def open_scheduler(self, schedule_id):
        self.scheduler.load_schedule(schedule_id)
        self.stacked_widget.setCurrentIndex(4) #scheduler screen
    
    def logout(self):
        self.db_manager.disconnect()
        self.close()
        QApplication.quit()  # close app
        QProcess.startDetached(sys.executable, sys.argv)

    def create_placeholder_widget(self, index):  #after development you can remove this function
        widget = QWidget()
        layout = QVBoxLayout()
        
        label = QLabel(f"Employee screen {index} is under development")
        label.setStyleSheet("font-size: 18px; color: gray;")
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        widget.setLayout(layout)
        
        return widget

def main():
    app = QApplication(sys.argv)
    
    # initialize database
    db_manager = DatabaseManager()
    
    if not db_manager.connect():
        QMessageBox.critical(None, 'Database Error', 
                           'Failed to connect to database. Please ensure SQL Server is running.')
        sys.exit(1)
    
    # show login dialog
    login = LoginDialog(db_manager)
    
    if login.exec_() == QDialog.Accepted:
        main_window = MainWindow(db_manager, login.user_data)
        main_window.show()
        sys.exit(app.exec_())
    else:
        db_manager.disconnect()
        sys.exit(0)

if __name__ == '__main__':
    main()