from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from datetime import date


class TimeClockDashboard(QWidget):
    def __init__(self, db_manager, user_data):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = user_data or {}
        # user_data expected as a dict returned by LoginDialog: contains 'employee_id'
        self.employee_id = None
        if isinstance(self.user_data, dict):
            self.employee_id = self.user_data.get('employee_id')
        else:
            # backwards compatibility with tuple/list style
            try:
                if len(self.user_data) >= 2:
                    self.employee_id = self.user_data[1]
            except Exception:
                self.employee_id = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        header = QLabel('Time Clock Dashboard')
        header.setFont(QFont('Arial', 16))
        layout.addWidget(header)

        # status labels
        self.shift_label = QLabel('Scheduled Shift: -')
        self.shift_label.setWordWrap(True)
        layout.addWidget(self.shift_label)

        self.attendance_label = QLabel('Attendance: -')
        layout.addWidget(self.attendance_label)

        # buttons
        btn_layout = QHBoxLayout()

        self.clock_in_btn = QPushButton('Clock In')
        self.clock_in_btn.clicked.connect(self.clock_in)
        btn_layout.addWidget(self.clock_in_btn)

        self.clock_out_btn = QPushButton('Clock Out')
        self.clock_out_btn.clicked.connect(self.clock_out)
        btn_layout.addWidget(self.clock_out_btn)

        self.start_break_btn = QPushButton('Start Break')
        self.start_break_btn.clicked.connect(self.start_break)
        btn_layout.addWidget(self.start_break_btn)

        self.end_break_btn = QPushButton('End Break')
        self.end_break_btn.clicked.connect(self.end_break)
        btn_layout.addWidget(self.end_break_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        refresh_layout = QHBoxLayout()
        refresh_btn = QPushButton('Refresh')
        refresh_btn.clicked.connect(self.refresh_view)
        refresh_layout.addWidget(refresh_btn)
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)

        self.setLayout(layout)

        self.refresh_view()

    def refresh_view(self):
        if not self.employee_id:
            self.shift_label.setText('Scheduled Shift: (no employee selected)')
            self.attendance_label.setText('Attendance: (no employee selected)')
            return

        today = date.today()
        sched = self.db_manager.get_today_shift(self.employee_id, today)
        if sched:
            # sched: (assignment_id, shift_name, start_time, end_time)
            try:
                _, shift_name, start_time, end_time = sched
            except Exception:
                shift_name = sched[1] if len(sched) > 1 else 'N/A'
                start_time = sched[2] if len(sched) > 2 else None
                end_time = sched[3] if len(sched) > 3 else None

            self.shift_label.setText(f"Scheduled Shift: {shift_name} ({start_time} - {end_time})")
        else:
            self.shift_label.setText('Scheduled Shift: No shift scheduled for today')

        log = self.db_manager.get_attendance_log(self.employee_id, today)
        if log:
            # log: (log_id, clock_in, clock_out)
            log_id, clock_in, clock_out = log
            status = f"Clock In: {clock_in or '-'} | Clock Out: {clock_out or '-'}"
            self.attendance_label.setText('Attendance: ' + status)
        else:
            self.attendance_label.setText('Attendance: No record for today')

    def clock_in(self):
        if not self.employee_id:
            QMessageBox.warning(self, 'Error', 'No employee associated with this session')
            return

        today = date.today()
        log = self.db_manager.get_attendance_log(self.employee_id, today)
        if log:
            QMessageBox.information(self, 'Already In', 'You have already clocked in today')
            self.refresh_view()
            return

        if self.db_manager.clock_in(self.employee_id):
            QMessageBox.information(self, 'Success', 'Clocked in successfully')
        else:
            QMessageBox.warning(self, 'Error', 'Failed to clock in')
        self.refresh_view()

    def clock_out(self):
        if not self.employee_id:
            QMessageBox.warning(self, 'Error', 'No employee associated with this session')
            return

        today = date.today()
        log = self.db_manager.get_attendance_log(self.employee_id, today)
        if not log:
            QMessageBox.warning(self, 'Error', 'No clock-in record found for today')
            return

        log_id, clock_in, clock_out = log
        if clock_out:
            QMessageBox.information(self, 'Already Out', 'You have already clocked out')
            return

        if self.db_manager.clock_out(log_id):
            QMessageBox.information(self, 'Success', 'Clocked out successfully')
        else:
            QMessageBox.warning(self, 'Error', 'Failed to clock out')
        self.refresh_view()

    def start_break(self):
        if not self.employee_id:
            QMessageBox.warning(self, 'Error', 'No employee associated with this session')
            return

        today = date.today()
        log = self.db_manager.get_attendance_log(self.employee_id, today)
        if not log:
            QMessageBox.warning(self, 'Error', 'You must clock in before starting a break')
            return

        log_id = log[0]
        active = self.db_manager.get_active_break(log_id)
        if active:
            QMessageBox.information(self, 'Active Break', 'A break is already active')
            return

        if self.db_manager.start_break(log_id):
            QMessageBox.information(self, 'Success', 'Break started')
        else:
            QMessageBox.warning(self, 'Error', 'Failed to start break')
        self.refresh_view()

    def end_break(self):
        if not self.employee_id:
            QMessageBox.warning(self, 'Error', 'No employee associated with this session')
            return

        today = date.today()
        log = self.db_manager.get_attendance_log(self.employee_id, today)
        if not log:
            QMessageBox.warning(self, 'Error', 'No clock-in record found for today')
            return

        log_id = log[0]
        active = self.db_manager.get_active_break(log_id)
        if not active:
            QMessageBox.information(self, 'No Active Break', 'There is no active break to end')
            return

        # active may be a row tuple (break_id,) or similar
        try:
            break_id = active[0]
        except Exception:
            break_id = active

        if self.db_manager.end_break(break_id):
            QMessageBox.information(self, 'Success', 'Break ended')
        else:
            QMessageBox.warning(self, 'Error', 'Failed to end break')
        self.refresh_view()
