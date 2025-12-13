from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class EmployeeRosterView(QWidget):
    def __init__(self, db_manager, user_data=None):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QLabel('Employee Roster')
        header.setFont(QFont('Arial', 16))
        layout.addWidget(header)

        controls = QHBoxLayout()
        controls.addWidget(QLabel('Select Employee:'))

        self.employee_combo = QComboBox()
        self.employee_combo.currentIndexChanged.connect(self.on_employee_change)
        controls.addWidget(self.employee_combo)

        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.load_employees)
        controls.addWidget(refresh_btn)

        controls.addStretch()
        layout.addLayout(controls)

        # roster table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Date', 'Shift', 'Start Time', 'End Time', 'Published'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_employees()

    def load_employees(self):
        employees = self.db_manager.get_all_employees() or []
        self.employee_combo.clear()
        self.employee_combo.addItem('All Employees', None)

        for emp in employees:
            # emp: (employee_id, first_name, last_name, ...)
            display = f"{emp[1]} {emp[2]} (ID: {emp[0]})"
            self.employee_combo.addItem(display, emp[0])

        # load all shifts by default
        self.load_shifts(None)

    def on_employee_change(self, index):
        emp_id = self.employee_combo.currentData()
        self.load_shifts(emp_id)

    def load_shifts(self, employee_id=None):
        # If employee_id is None, show all employees' recent shifts
        if employee_id:
            shifts = self.db_manager.get_employee_shifts(employee_id) or []
        else:
            # aggregate shifts for all employees by calling get_all_employees then per-employee
            shifts = []
            employees = self.db_manager.get_all_employees() or []
            for emp in employees:
                emp_shifts = self.db_manager.get_employee_shifts(emp[0]) or []
                for s in emp_shifts:
                    # prepend employee name to shift rows
                    shifts.append((emp[1] + ' ' + emp[2],) + tuple(s))

        # normalize rows: if employee name included, row structure differs
        self.table.setRowCount(len(shifts))

        for row, s in enumerate(shifts):
            # Cases:
            # - employee-specific call: s = (assigned_date, shift_name, start_time, end_time, is_published)
            # - aggregated call: s = (employee_name, assigned_date, shift_name, start_time, end_time, is_published)
            if len(s) == 5:
                assigned_date, shift_name, start_time, end_time, is_published = s
                prefix = ''
            else:
                prefix = s[0] + ' - '
                assigned_date, shift_name, start_time, end_time, is_published = s[1:]

            self.table.setItem(row, 0, QTableWidgetItem(str(assigned_date)))
            self.table.setItem(row, 1, QTableWidgetItem(prefix + (shift_name or 'N/A')))
            self.table.setItem(row, 2, QTableWidgetItem(str(start_time) if start_time is not None else ''))
            self.table.setItem(row, 3, QTableWidgetItem(str(end_time) if end_time is not None else ''))
            pub_text = 'Yes' if is_published else 'No'
            pub_item = QTableWidgetItem(pub_text)
            if is_published:
                pub_item.setBackground(Qt.green)
            else:
                pub_item.setBackground(Qt.yellow)
            self.table.setItem(row, 4, pub_item)

        if not shifts:
            QMessageBox.information(self, 'No data', 'No shifts found for the selection')
