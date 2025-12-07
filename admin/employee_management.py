from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QDialog, QDialogButtonBox, QLineEdit, QComboBox,
                             QMessageBox, QHeaderView, QFormLayout, QCheckBox,
                             QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class EmployeeManagement(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        #header
        header = QLabel('Employee Management')
        header.setFont(QFont('Arial', 16, QFont.Bold))
        layout.addWidget(header)
        
        #tab widget for employees and accounts
        tabs = QTabWidget()
        
        #employee tab
        employee_tab = QWidget()
        employee_layout = QVBoxLayout()
        
        # buttons for employee tab
        emp_btn_layout = QHBoxLayout()
        
        add_emp_btn = QPushButton('Add New Employee')
        add_emp_btn.setStyleSheet("""
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
        add_emp_btn.clicked.connect(self.add_employee)
        emp_btn_layout.addWidget(add_emp_btn)
        
        refresh_emp_btn = QPushButton('Refresh')
        refresh_emp_btn.setStyleSheet("""
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
        refresh_emp_btn.clicked.connect(self.load_employees)
        emp_btn_layout.addWidget(refresh_emp_btn)
        
        emp_btn_layout.addStretch()
        employee_layout.addLayout(emp_btn_layout)
        
        # employee table
        self.employee_table = QTableWidget()
        self.employee_table.setColumnCount(7)
        self.employee_table.setHorizontalHeaderLabels([
            'ID', 'First Name', 'Last Name', 'Department', 
            'Job Title', 'Employment Type', 'Primary Skill'
        ])
        self.employee_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.employee_table.setEditTriggers(QTableWidget.NoEditTriggers)
        employee_layout.addWidget(self.employee_table)
        
        employee_tab.setLayout(employee_layout)
        tabs.addTab(employee_tab, 'Employees')
        
        # user accounts tab
        accounts_tab = QWidget()
        accounts_layout = QVBoxLayout()
        
        # buttons for accounts tab
        acc_btn_layout = QHBoxLayout()
        
        add_acc_btn = QPushButton('Create User Account')
        add_acc_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        add_acc_btn.clicked.connect(self.create_user_account)
        acc_btn_layout.addWidget(add_acc_btn)
        
        refresh_acc_btn = QPushButton('Refresh')
        refresh_acc_btn.setStyleSheet("""
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
        refresh_acc_btn.clicked.connect(self.load_user_accounts)
        acc_btn_layout.addWidget(refresh_acc_btn)
        
        acc_btn_layout.addStretch()
        accounts_layout.addLayout(acc_btn_layout)
        
        # user accounts table
        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(5)
        self.accounts_table.setHorizontalHeaderLabels([
            'User ID', 'Employee Name', 'Username', 'Is Admin', 'Actions'
        ])
        self.accounts_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.accounts_table.setEditTriggers(QTableWidget.NoEditTriggers)
        accounts_layout.addWidget(self.accounts_table)
        
        accounts_tab.setLayout(accounts_layout)
        tabs.addTab(accounts_tab, 'User Accounts')
        
        layout.addWidget(tabs)
        self.setLayout(layout)
        
        self.load_employees()
        self.load_user_accounts()
    
    def load_employees(self):
        employees = self.db_manager.get_all_employees()
        self.employee_table.setRowCount(len(employees))
        
        for row, emp in enumerate(employees):
            # emp: (employee_id, first_name, last_name, dept_name, job_title, emp_type, skill_name)
            self.employee_table.setItem(row, 0, QTableWidgetItem(str(emp[0])))
            self.employee_table.setItem(row, 1, QTableWidgetItem(emp[1]))
            self.employee_table.setItem(row, 2, QTableWidgetItem(emp[2]))
            self.employee_table.setItem(row, 3, QTableWidgetItem(emp[3] or 'N/A'))
            self.employee_table.setItem(row, 4, QTableWidgetItem(emp[4] or 'N/A'))
            self.employee_table.setItem(row, 5, QTableWidgetItem(emp[5] or 'N/A'))
            self.employee_table.setItem(row, 6, QTableWidgetItem(emp[6] or 'N/A'))
    
    def load_user_accounts(self):
        accounts = self.db_manager.get_all_user_accounts()
        self.accounts_table.setRowCount(len(accounts))
        
        for row, acc in enumerate(accounts):
            # acc: (user_id, employee_id, first_name, last_name, username, is_admin)
            self.accounts_table.setItem(row, 0, QTableWidgetItem(str(acc[0])))
            self.accounts_table.setItem(row, 1, QTableWidgetItem(f"{acc[2]} {acc[3]}"))
            self.accounts_table.setItem(row, 2, QTableWidgetItem(acc[4]))
            
            admin_status = 'Yes' if acc[5] else 'No'
            admin_item = QTableWidgetItem(admin_status)
            if acc[5]:
                admin_item.setBackground(Qt.yellow)
            self.accounts_table.setItem(row, 3, admin_item)
            
            # Delete button
            delete_btn = QPushButton('Delete')
            delete_btn.setStyleSheet('background-color: #e74c3c; color: white; padding: 5px;')
            delete_btn.clicked.connect(lambda checked, uid=acc[0]: self.delete_user_account(uid))
            self.accounts_table.setCellWidget(row, 4, delete_btn)
    
    def add_employee(self):
        dialog = AddEmployeeDialog(self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_employees()
            # Emit signal to refresh scheduler if needed
            QMessageBox.information(self, 'Success', 
                                  'Employee added successfully! The employee is now available in the scheduler.')
    
    def create_user_account(self):
        dialog = CreateUserAccountDialog(self.db_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.load_user_accounts()
    
    def delete_user_account(self, user_id):
        reply = QMessageBox.question(self, 'Delete User Account',
                                     'Are you sure you want to delete this user account?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.db_manager.delete_user_account(user_id):
                QMessageBox.information(self, 'Success', 'User account deleted!')
                self.load_user_accounts()
            else:
                QMessageBox.warning(self, 'Error', 'Failed to delete user account')

class AddEmployeeDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle('Add New Employee')
        self.setFixedSize(400, 350)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        # first name
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText('Enter first name')
        layout.addRow('First Name:', self.first_name)
        
        # lastname
        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText('Enter last name')
        layout.addRow('Last Name:', self.last_name)
        
        #department
        self.department = QComboBox()
        departments = self.db_manager.get_departments()
        for dept in departments:
            self.department.addItem(dept[1], dept[0])
        layout.addRow('Department:', self.department)
        
        # job title
        self.job_title = QComboBox()
        jobs = self.db_manager.get_job_titles()
        for job in jobs:
            self.job_title.addItem(job[1], job[0])
        layout.addRow('Job Title:', self.job_title)
        
        # employment type
        self.emp_type = QComboBox()
        types = self.db_manager.get_employment_types()
        for emp_type in types:
            self.emp_type.addItem(emp_type[1], emp_type[0])
        layout.addRow('Employment Type:', self.emp_type)
        
        #primary skill
        self.skill = QComboBox()
        skills = self.db_manager.get_skills()
        for skill in skills:
            self.skill.addItem(skill[1], skill[0])
        layout.addRow('Primary Skill:', self.skill)
        
        #buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_employee)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def save_employee(self):
        first_name = self.first_name.text().strip()
        last_name = self.last_name.text().strip()
        
        if not first_name or not last_name:
            QMessageBox.warning(self, 'Error', 'Please enter both first and last name')
            return
        
        dept_id = self.department.currentData()
        job_id = self.job_title.currentData()
        type_id = self.emp_type.currentData()
        skill_id = self.skill.currentData()
        
        if self.db_manager.add_employee(first_name, last_name, dept_id, 
                                       job_id, type_id, skill_id):
            QMessageBox.information(self, 'Success', 'Employee added successfully!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to add employee')

class CreateUserAccountDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle('Create User Account')
        self.setFixedSize(450, 300)
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()
        
        #employee selection
        self.employee_combo = QComboBox()
        self.load_employees_without_accounts()
        layout.addRow('Select Employee:', self.employee_combo)
        
        # username
        self.username = QLineEdit()
        self.username.setPlaceholderText('Enter username')
        layout.addRow('Username:', self.username)
        
        # password
        self.password = QLineEdit()
        self.password.setPlaceholderText('Enter password')
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow('Password:', self.password)
        
        # confirm password
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText('Confirm password')
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addRow('Confirm Password:', self.confirm_password)
        
        # is_admin checkbox
        self.is_admin = QCheckBox('Administrator Access')
        self.is_admin.setStyleSheet('padding: 5px;')
        layout.addRow('Access Level:', self.is_admin)
        
        # infos label
        info_label = QLabel('Note: Administrators have access to all management features.')
        info_label.setStyleSheet('color: gray; font-size: 10px; padding: 5px;')
        info_label.setWordWrap(True)
        layout.addRow(info_label)
        
        # buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.create_account)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)
    
    def load_employees_without_accounts(self):
        employees = self.db_manager.get_employees_without_accounts()
        
        if not employees:
            self.employee_combo.addItem('No employees without accounts', None)
        else:
            for emp in employees:
                # emp: (employee_id, first_name, last_name)
                self.employee_combo.addItem(f"{emp[1]} {emp[2]} (ID: {emp[0]})", emp[0])
    
    def create_account(self):
        employee_id = self.employee_combo.currentData()
        username = self.username.text().strip()
        password = self.password.text().strip()
        confirm_pass = self.confirm_password.text().strip()
        is_admin = 1 if self.is_admin.isChecked() else 0
        
        #validation
        if not employee_id:
            QMessageBox.warning(self, 'Error', 'No employee selected or all employees have accounts')
            return
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter username and password')
            return
        
        if len(username) < 3:
            QMessageBox.warning(self, 'Error', 'Username must be at least 3 characters')
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, 'Error', 'Password must be at least 6 characters')
            return
        
        if password != confirm_pass:
            QMessageBox.warning(self, 'Error', 'Passwords do not match')
            return
        
        #check if username already exists
        if self.db_manager.check_username_exists(username):
            QMessageBox.warning(self, 'Error', 'Username already exists. Please choose another.')
            return
        
        #create account
        if self.db_manager.create_user_account(employee_id, username, password, is_admin):
            role = 'Administrator' if is_admin else 'Employee'
            QMessageBox.information(self, 'Success', 
                                  f'User account created successfully as {role}!')
            self.accept()
        else:
            QMessageBox.warning(self, 'Error', 'Failed to create user account')
