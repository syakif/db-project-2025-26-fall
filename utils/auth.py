from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class LoginDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('HR Management System - Login')
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # title
        title = QLabel('HR Management System')
        title.setFont(QFont('Arial', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # username
        username_layout = QHBoxLayout()
        username_label = QLabel('Username:')
        username_label.setFixedWidth(100)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter username')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # password
        password_layout = QHBoxLayout()
        password_label = QLabel('Password:')
        password_label.setFixedWidth(100)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Enter password')
        self.password_input.returnPressed.connect(self.login)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # login button
        self.login_btn = QPushButton('Login')
        self.login_btn.setFixedHeight(40)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        
        # info label
        info_label = QLabel('Demo users: jdoe/pass123 (employee), asmith/admin789 (admin)')
        info_label.setStyleSheet('color: gray; font-size: 10px;')
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, 'Error', 'Please enter both username and password')
            return
        
        user = self.db_manager.authenticate_user(username, password)
        
        if user:
            self.user_data = {
                'user_id': user[0],
                'employee_id': user[1],
                'is_admin': bool(user[2]),
                'first_name': user[3],
                'last_name': user[4]
            }
            self.accept()
        else:
            QMessageBox.warning(self, 'Login Failed', 'Invalid username or password')
            self.password_input.clear()