from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QHeaderView, QMessageBox, QDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from datetime import date

class ManagerAttendanceReport(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        #header
        header = QLabel('Manager Attendance Report')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(header)
        
        # controls
        controls = QHBoxLayout()
        
        controls.addWidget(QLabel('Report Date:'))
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.dateChanged.connect(self.load_report)  # Auto-load on date change
        controls.addWidget(self.date_picker)
        
        load_btn = QPushButton('Refresh Report')
        load_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_btn.clicked.connect(self.load_report)
        controls.addWidget(load_btn)
        
        # button to see leave requests
        leave_btn = QPushButton('View Leave Requests')
        leave_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        leave_btn.clicked.connect(self.view_leave_requests)
        controls.addWidget(leave_btn)
        
        controls.addStretch()
        layout.addLayout(controls)
        
        # current date display
        self.current_date_label = QLabel()
        self.current_date_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.current_date_label.setStyleSheet('color: #2c3e50; padding: 5px;')
        layout.addWidget(self.current_date_label)
        
        # legend
        legend = QHBoxLayout()
        legend.addWidget(QLabel('Legend:'))
        
        on_time = QLabel(' On Time ')
        on_time.setStyleSheet('background-color: lightgreen; padding: 5px;')
        legend.addWidget(on_time)
        
        late = QLabel(' Late ')
        late.setStyleSheet('background-color: lightcoral; padding: 5px;')
        legend.addWidget(late)
        
        absent = QLabel(' Absent ')
        absent.setStyleSheet('background-color: lightgray; padding: 5px;')
        legend.addWidget(absent)
        
        on_leave = QLabel(' On Leave ')
        on_leave.setStyleSheet('background-color: lightyellow; padding: 5px;')
        legend.addWidget(on_leave)
        
        legend.addStretch()
        layout.addLayout(legend)
        
        # table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Employee', 'Scheduled Start', 'Scheduled End', 
            'Clock In', 'Clock Out', 'Status', 'Notes'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.load_report()
    
    def load_report(self):
        report_date = self.date_picker.date().toPyDate()
        self.current_date_label.setText(f"Showing report for: {report_date.strftime('%A, %B %d, %Y')}")
        
        report = self.db_manager.get_attendance_report(report_date)
        
        self.table.setRowCount(len(report))
        
        for row, record in enumerate(report):
            # record: (employee_id, first_name, last_name, scheduled_start, scheduled_end,
            #          clock_in, clock_out, status, leave_type_id)
            
            name = f"{record[1]} {record[2]}"
            self.table.setItem(row, 0, QTableWidgetItem(name))
            
            if record[3]:  # Has scheduled shift
                self.table.setItem(row, 1, QTableWidgetItem(str(record[3])))
                self.table.setItem(row, 2, QTableWidgetItem(str(record[4])))
            else:
                self.table.setItem(row, 1, QTableWidgetItem('N/A'))
                self.table.setItem(row, 2, QTableWidgetItem('N/A'))
            
            if record[5]:  # Clock in
                self.table.setItem(row, 3, QTableWidgetItem(str(record[5])))
            else:
                self.table.setItem(row, 3, QTableWidgetItem('-'))
            
            if record[6]:  # Clock out
                self.table.setItem(row, 4, QTableWidgetItem(str(record[6])))
            else:
                self.table.setItem(row, 4, QTableWidgetItem('-'))
            
            # Status with color coding
            status = record[7]
            status_item = QTableWidgetItem(status)
            
            if record[8]:  # On leave
                status_item.setBackground(QColor(255, 255, 200))  # Light yellow
                notes = 'On Approved Leave'
            elif status == 'On Time':
                status_item.setBackground(QColor(144, 238, 144))  # Light green
                notes = ''
            elif status == 'Late':
                status_item.setBackground(QColor(240, 128, 128))  # Light coral
                notes = 'Arrived Late'
            else:  # Absent
                status_item.setBackground(QColor(211, 211, 211))  # Light gray
                notes = 'Did Not Clock In'
            
            self.table.setItem(row, 5, status_item)
            self.table.setItem(row, 6, QTableWidgetItem(notes))
    
    def view_leave_requests(self):
        # show all pending leave requests
        dialog = LeaveRequestDialog(self.db_manager)
        dialog.exec_()
        self.load_report()  # Refresh after approving requests

class LeaveRequestDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle('Leave Requests')
        self.setGeometry(200, 200, 800, 500)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        header = QLabel('All Leave Requests')
        header.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(header)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            'Request ID', 'Employee', 'Type', 'Start Date', 'End Date', 'Status', 'Actions'
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        self.load_requests()
    
    def load_requests(self):
        requests = self.db_manager.get_leave_requests()
        self.table.setRowCount(len(requests))
        
        for row, req in enumerate(requests):
            # req: (request_id, first_name, last_name, type_name, start_date, end_date, is_approved)
            self.table.setItem(row, 0, QTableWidgetItem(str(req[0])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{req[1]} {req[2]}"))
            self.table.setItem(row, 2, QTableWidgetItem(req[3]))
            self.table.setItem(row, 3, QTableWidgetItem(str(req[4])))
            self.table.setItem(row, 4, QTableWidgetItem(str(req[5])))
            
            status = 'Approved' if req[6] else 'Pending'
            status_item = QTableWidgetItem(status)
            if req[6]:
                status_item.setBackground(Qt.green)
            else:
                status_item.setBackground(Qt.yellow)
            self.table.setItem(row, 5, status_item)
            
            #approve button for pending requests
            if not req[6]:
                approve_btn = QPushButton('Approve')
                approve_btn.setStyleSheet('background-color: #27ae60; color: white; padding: 5px;')
                approve_btn.clicked.connect(lambda checked, rid=req[0]: self.approve_request(rid))
                self.table.setCellWidget(row, 6, approve_btn)
            else:
                approved_label = QLabel('✓ Approved')
                approved_label.setStyleSheet('color: green; font-weight: bold; padding: 5px;')
                approved_label.setAlignment(Qt.AlignCenter)
                self.table.setCellWidget(row, 6, approved_label)
    
    def approve_request(self, request_id):
        reply = QMessageBox.question(self, 'Approve Leave Request',
                                     'Are you sure you want to approve this leave request?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db_manager.approve_leave_request(request_id):
                QMessageBox.information(self, 'Success', 'Leave request approved!')
                self.load_requests()  # Refresh the table
            else:
                QMessageBox.warning(self, 'Error', 'Failed to approve request')