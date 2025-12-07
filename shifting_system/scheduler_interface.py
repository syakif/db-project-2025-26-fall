from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QComboBox, QDialog, QDialogButtonBox, QMessageBox,
                             QHeaderView, QListWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta

class SchedulerInterface(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.current_schedule_id = None
        self.schedule_info = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # header
        self.header = QLabel('Scheduler Interface')
        self.header.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(self.header)
        
        # controls
        controls = QHBoxLayout()
        
        # department filter
        controls.addWidget(QLabel('Filter by Department:'))
        self.dept_filter = QComboBox()
        self.dept_filter.addItem('All Departments', None)
        self.load_departments()
        self.dept_filter.currentIndexChanged.connect(self.filter_employees)
        controls.addWidget(self.dept_filter)
        
        # skill filter
        controls.addWidget(QLabel('Filter by Skill:'))
        self.skill_filter = QComboBox()
        self.skill_filter.addItem('All Skills', None)
        self.load_skills()
        self.skill_filter.currentIndexChanged.connect(self.filter_employees)
        controls.addWidget(self.skill_filter)
        
        controls.addStretch()
        
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_assignments)
        controls.addWidget(refresh_btn)
        
        layout.addLayout(controls)
        
        # main content area
        content = QHBoxLayout()
        
        # employee list
        employee_section = QVBoxLayout()
        employee_section.addWidget(QLabel('Employees:'))
        self.employee_list = QListWidget()
        self.employee_list.itemDoubleClicked.connect(self.assign_employee)
        employee_section.addWidget(self.employee_list)
        
        employee_widget = QWidget()
        employee_widget.setLayout(employee_section)
        employee_widget.setFixedWidth(250)
        content.addWidget(employee_widget)
        
        # assignments table in grid view
        self.assignments_table = QTableWidget()
        self.assignments_table.setColumnCount(8)
        self.assignments_table.setHorizontalHeaderLabels([
            'Date', 'Employee', 'Shift Type', 'Start Time', 'End Time', 'Actions', '', ''
        ])
        self.assignments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        content.addWidget(self.assignments_table)
        
        layout.addLayout(content)
        self.setLayout(layout)
        
        self.load_employees()
    
    def load_departments(self):
        departments = self.db_manager.get_departments()
        for dept in departments:
            self.dept_filter.addItem(dept[1], dept[0])
    
    def load_skills(self):
        skills = self.db_manager.get_skills()
        for skill in skills:
            self.skill_filter.addItem(skill[1], skill[0])
    
    def load_employees(self):
        employees = self.db_manager.get_all_employees()
        self.all_employees = employees
        self.filter_employees()
    
    def filter_employees(self):
        # reload employees from database to get latest data
        self.all_employees = self.db_manager.get_all_employees()
        
        dept_id = self.dept_filter.currentData()
        skill_id = self.skill_filter.currentData()
        
        self.employee_list.clear()
        for emp in self.all_employees:
            # emp: (employee_id, first_name, last_name, dept_name, job_title, emp_type, skill_name)
            if dept_id and emp[3]:  # Filter by department
                if emp[3] != self.dept_filter.currentText():
                    continue
            
            if skill_id and emp[6]:  # Filter by skill
                if emp[6] != self.skill_filter.currentText():
                    continue
            
            display_text = f"{emp[1]} {emp[2]} - {emp[6] or 'No Skill'}"
            item = self.employee_list.addItem(display_text)
            # Store employee_id in item data
            self.employee_list.item(self.employee_list.count() - 1).setData(Qt.UserRole, emp[0])
    
    def load_schedule(self, schedule_id):
        self.current_schedule_id = schedule_id
        
        # get schedule infos
        schedules = self.db_manager.get_weekly_schedules()
        for schedule in schedules:
            if schedule[0] == schedule_id:
                self.schedule_info = schedule
                break
        
        self.header.setText(f'Scheduler - Week {self.schedule_info[1]} to {self.schedule_info[2]}')
        self.load_assignments()
    
    def load_assignments(self):
        if not self.current_schedule_id:
            return
        
        assignments = self.db_manager.get_shift_assignments(self.current_schedule_id)
        self.assignments_table.setRowCount(len(assignments))
        
        for row, assignment in enumerate(assignments):
            # assignment: (assignment_id, assigned_date, first_name, last_name, shift_name, start_time, end_time)
            self.assignments_table.setItem(row, 0, QTableWidgetItem(str(assignment[1])))
            self.assignments_table.setItem(row, 1, QTableWidgetItem(f"{assignment[2]} {assignment[3]}"))
            self.assignments_table.setItem(row, 2, QTableWidgetItem(assignment[4]))
            self.assignments_table.setItem(row, 3, QTableWidgetItem(str(assignment[5])))
            self.assignments_table.setItem(row, 4, QTableWidgetItem(str(assignment[6])))
            
            # delete button
            delete_btn = QPushButton('Delete')
            delete_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 5px;')
            delete_btn.clicked.connect(lambda checked, aid=assignment[0]: self.delete_assignment(aid))
            self.assignments_table.setCellWidget(row, 5, delete_btn)
    
    def assign_employee(self, item):
        if not self.current_schedule_id:
            QMessageBox.warning(self, 'Error', 'No schedule selected')
            return
        
        employee_id = item.data(Qt.UserRole)
        
        # show dialog to select date and shift
        dialog = AssignmentDialog(self.db_manager, self.schedule_info)
        if dialog.exec_() == QDialog.Accepted:
            date = dialog.selected_date
            shift_type_id = dialog.selected_shift_id
            
            if self.db_manager.add_shift_assignment(self.current_schedule_id, employee_id, 
                                                    shift_type_id, date):
                QMessageBox.information(self, 'Success', 'Shift assigned successfully!')
                self.load_assignments()
            else:
                QMessageBox.warning(self, 'Error', 'Failed to assign shift')
    
    def delete_assignment(self, assignment_id):
        reply = QMessageBox.question(self, 'Delete Assignment',
                                     'Are you sure you want to delete this assignment?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_shift_assignment(assignment_id):
                QMessageBox.information(self, 'Success', 'Assignment deleted!')
                self.load_assignments()
            else:
                QMessageBox.warning(self, 'Error', 'Failed to delete assignment')

class AssignmentDialog(QDialog):
    def __init__(self, db_manager, schedule_info):
        super().__init__()
        self.db_manager = db_manager
        self.schedule_info = schedule_info
        self.selected_date = None
        self.selected_shift_id = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('Assign Shift')
        layout = QVBoxLayout()
        
        # date selection
        layout.addWidget(QLabel('Select Date:'))
        self.date_combo = QComboBox()
        
        # Add dates from schedule
        start = self.schedule_info[1]
        end = self.schedule_info[2]
        current = start
        while current <= end:
            self.date_combo.addItem(str(current), current)
            current += timedelta(days=1)
        
        layout.addWidget(self.date_combo)
        
        # shift type selection
        layout.addWidget(QLabel('Select Shift:'))
        self.shift_combo = QComboBox()
        
        shifts = self.db_manager.get_shift_types()
        for shift in shifts:
            self.shift_combo.addItem(f"{shift[1]} ({shift[2]} - {shift[3]})", shift[0])
        
        layout.addWidget(self.shift_combo)
        
        #buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def accept(self):
        self.selected_date = self.date_combo.currentData()
        self.selected_shift_id = self.shift_combo.currentData()
        super().accept()