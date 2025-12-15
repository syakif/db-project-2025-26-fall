from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class EmployeeRosterView(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel('My Roster - Scheduled Shifts')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(header)
        
        # Refresh button
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton('Refresh')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_shifts)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Date', 'Shift Type', 'Start Time', 'End Time', 'Status'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_shifts()
    
    def load_shifts(self):
        shifts = self.db_manager.get_employee_shifts(self.user_data['employee_id'])
        self.table.setRowCount(len(shifts))
        
        for row, shift in enumerate(shifts):
            # shift: (assigned_date, shift_name, start_time, end_time, is_published)
            self.table.setItem(row, 0, QTableWidgetItem(str(shift[0])))
            self.table.setItem(row, 1, QTableWidgetItem(shift[1]))
            self.table.setItem(row, 2, QTableWidgetItem(str(shift[2])))
            self.table.setItem(row, 3, QTableWidgetItem(str(shift[3])))
            
            status = 'Published' if shift[4] else 'Draft'
            status_item = QTableWidgetItem(status)
            if shift[4]:
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.yellow)
            self.table.setItem(row, 4, status_item)
