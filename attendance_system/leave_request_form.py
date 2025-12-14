from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDateEdit, QComboBox, QMessageBox,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import date

class LeaveRequestForm(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel('Leave Request Form')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(header)
        
        # Form section
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Leave type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('Leave Type:'))
        self.leave_type_combo = QComboBox()
        self.load_leave_types()
        type_layout.addWidget(self.leave_type_combo)
        type_layout.addStretch()
        form_layout.addLayout(type_layout)
        
        # Start date
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel('Start Date:'))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        start_layout.addWidget(self.start_date)
        start_layout.addStretch()
        form_layout.addLayout(start_layout)
        
        # End date
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel('End Date:'))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())
        end_layout.addWidget(self.end_date)
        end_layout.addStretch()
        form_layout.addLayout(end_layout)
        
        # Submit button
        btn_layout = QHBoxLayout()
        submit_btn = QPushButton('Submit Request')
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        submit_btn.clicked.connect(self.submit_request)
        btn_layout.addWidget(submit_btn)
        
        refresh_btn = QPushButton('Refresh')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_requests)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        form_layout.addLayout(btn_layout)
        
        layout.addLayout(form_layout)
        
        # My requests section
        layout.addWidget(QLabel('My Leave Requests:'))
        
        self.requests_table = QTableWidget()
        self.requests_table.setColumnCount(5)
        self.requests_table.setHorizontalHeaderLabels([
            'Request ID', 'Type', 'Start Date', 'End Date', 'Status'
        ])
        self.requests_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.requests_table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.requests_table)
        
        self.setLayout(layout)
        self.load_requests()
    
    def load_leave_types(self):
        leave_types = self.db_manager.get_leave_types()
        for lt in leave_types:
            self.leave_type_combo.addItem(lt[1], lt[0])
    
    def submit_request(self):
        leave_type_id = self.leave_type_combo.currentData()
        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()
        
        if start > end:
            QMessageBox.warning(self, 'Error', 'Start date must be before end date')
            return
        
        if self.db_manager.submit_leave_request(self.user_data['employee_id'], 
                                               leave_type_id, start, end):
            QMessageBox.information(self, 'Success', 
                                  'Leave request submitted! Waiting for approval.')
            self.load_requests()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to submit leave request')
    
    def load_requests(self):
        requests = self.db_manager.get_leave_requests(self.user_data['employee_id'])
        self.requests_table.setRowCount(len(requests))
        
        for row, req in enumerate(requests):
            # req: (request_id, first_name, last_name, type_name, start_date, end_date, is_approved)
            self.requests_table.setItem(row, 0, QTableWidgetItem(str(req[0])))
            self.requests_table.setItem(row, 1, QTableWidgetItem(req[3]))
            self.requests_table.setItem(row, 2, QTableWidgetItem(str(req[4])))
            self.requests_table.setItem(row, 3, QTableWidgetItem(str(req[5])))
            
            status = 'Approved' if req[6] else 'Pending'
            status_item = QTableWidgetItem(status)
            if req[6]:
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.yellow)
            self.requests_table.setItem(row, 4, status_item)