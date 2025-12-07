from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QInputDialog, QDateEdit, QHeaderView)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta

class ManagerDashboard(QWidget):
    edit_schedule_signal = pyqtSignal(int)  # emits schedule_id
    
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel('Manager Dashboard - Weekly Schedules')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(header)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        create_btn = QPushButton('Create New Schedule')
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        create_btn.clicked.connect(self.create_schedule)
        btn_layout.addWidget(create_btn)
        
        refresh_btn = QPushButton('Refresh')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.load_schedules)
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Schedule ID', 'Start Date', 'End Date', 'Status', 'Actions'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_schedules()
    
    def load_schedules(self):
        schedules = self.db_manager.get_weekly_schedules()
        self.table.setRowCount(len(schedules))
        
        for row, schedule in enumerate(schedules):
            self.table.setItem(row, 0, QTableWidgetItem(str(schedule[0])))
            self.table.setItem(row, 1, QTableWidgetItem(str(schedule[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(schedule[2])))
            
            status = 'Published' if schedule[3] else 'Draft'
            status_item = QTableWidgetItem(status)
            if schedule[3]:
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.yellow)
            self.table.setItem(row, 3, status_item)
            
            # action Buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(5, 2, 5, 2)
            
            edit_btn = QPushButton('Edit')
            edit_btn.setStyleSheet('background-color: #3498db; color: white; padding: 5px;')
            edit_btn.clicked.connect(lambda checked, sid=schedule[0]: self.edit_schedule(sid))
            action_layout.addWidget(edit_btn)
            
            if not schedule[3]:  # If not published
                publish_btn = QPushButton('Publish')
                publish_btn.setStyleSheet('background-color: #27ae60; color: white; padding: 5px;')
                publish_btn.clicked.connect(lambda checked, sid=schedule[0]: self.publish_schedule(sid))
                action_layout.addWidget(publish_btn)
            
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 4, action_widget)
    
    def create_schedule(self):
        # get start date
        start_date, ok = QInputDialog.getText(self, 'Create Schedule', 
                                              'Enter start date (YYYY-MM-DD):')
        if not ok or not start_date:
            return
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = start + timedelta(days=6)  # One week
            
            if self.db_manager.create_weekly_schedule(start, end):
                QMessageBox.information(self, 'Success', 'Schedule created successfully!')
                self.load_schedules()
            else:
                QMessageBox.warning(self, 'Error', 'Failed to create schedule')
        except ValueError:
            QMessageBox.warning(self, 'Error', 'Invalid date format. Use YYYY-MM-DD')
    
    def edit_schedule(self, schedule_id):
        self.edit_schedule_signal.emit(schedule_id)
    
    def publish_schedule(self, schedule_id):
        reply = QMessageBox.question(self, 'Publish Schedule',
                                     'Are you sure you want to publish this schedule?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db_manager.publish_schedule(schedule_id):
                QMessageBox.information(self, 'Success', 'Schedule published!')
                self.load_schedules()
            else:
                QMessageBox.warning(self, 'Error', 'Failed to publish schedule')