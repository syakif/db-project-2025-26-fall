import pyodbc
from datetime import datetime, date, time

class DatabaseManager:
    def __init__(self, server='localhost\\SQLEXPRESS', database='DBPROJECT', trusted_connection=True):
        self.connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection={"yes" if trusted_connection else "no"};'
        )
        self.conn = None
    
    def connect(self):
        try:
            self.conn = pyodbc.connect(self.connection_string)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def disconnect(self):
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None, fetch=True):
        try:
            cursor = self.conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                return cursor.fetchall()
            else:
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Query execution error: {e}")
            return None if fetch else False
    
    # Authentication
    def authenticate_user(self, username, password):
        query = """
        SELECT ua.user_id, ua.employee_id, ua.is_admin, e.first_name, e.last_name
        FROM UserAccounts ua
        JOIN Employees e ON ua.employee_id = e.employee_id
        WHERE ua.username = ? AND ua.password = ?
        """
        result = self.execute_query(query, (username, password))
        return result[0] if result else None
    
    # Employee Management
    def get_all_employees(self):
        query = """
        SELECT e.employee_id, e.first_name, e.last_name, 
               d.department_name, jt.title_name, et.type_name, s.skill_name
        FROM Employees e
        LEFT JOIN Departments d ON e.department_id = d.department_id
        LEFT JOIN JobTitles jt ON e.job_id = jt.job_id
        LEFT JOIN EmploymentTypes et ON e.type_id = et.type_id
        LEFT JOIN Skills s ON e.skill_id = s.skill_id
        """
        return self.execute_query(query)
    
    def add_employee(self, first_name, last_name, dept_id, job_id, type_id, skill_id):
        query = """
        INSERT INTO Employees (first_name, last_name, department_id, job_id, type_id, skill_id)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.execute_query(query, (first_name, last_name, dept_id, job_id, type_id, skill_id), fetch=False)
    
    # Departments, JobTitles, Skills, etc.
    def get_departments(self):
        return self.execute_query("SELECT department_id, department_name FROM Departments")
    
    def get_job_titles(self):
        return self.execute_query("SELECT job_id, title_name FROM JobTitles")
    
    def get_skills(self):
        return self.execute_query("SELECT skill_id, skill_name FROM Skills")
    
    def get_employment_types(self):
        return self.execute_query("SELECT type_id, type_name FROM EmploymentTypes")
    
    # Weekly Schedules
    def get_weekly_schedules(self):
        query = """
        SELECT schedule_id, start_date, end_date, is_published
        FROM WeeklySchedules
        ORDER BY start_date DESC
        """
        return self.execute_query(query)
    
    def create_weekly_schedule(self, start_date, end_date):
        query = "INSERT INTO WeeklySchedules (start_date, end_date) VALUES (?, ?)"
        return self.execute_query(query, (start_date, end_date), fetch=False)
    
    def publish_schedule(self, schedule_id):
        query = "UPDATE WeeklySchedules SET is_published = 1 WHERE schedule_id = ?"
        return self.execute_query(query, (schedule_id,), fetch=False)
    
    # Shift Types
    def get_shift_types(self):
        return self.execute_query("SELECT shift_type_id, shift_name, start_time, end_time FROM ShiftTypes")
    
    # Shift Assignments
    def get_shift_assignments(self, schedule_id):
        query = """
        SELECT sa.assignment_id, sa.assigned_date, 
               e.first_name, e.last_name, st.shift_name, st.start_time, st.end_time
        FROM ShiftAssignments sa
        JOIN Employees e ON sa.employee_id = e.employee_id
        JOIN ShiftTypes st ON sa.shift_type_id = st.shift_type_id
        WHERE sa.schedule_id = ?
        ORDER BY sa.assigned_date, st.start_time
        """
        return self.execute_query(query, (schedule_id,))
    
    def add_shift_assignment(self, schedule_id, employee_id, shift_type_id, assigned_date):
        query = """
        INSERT INTO ShiftAssignments (schedule_id, employee_id, shift_type_id, assigned_date)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (schedule_id, employee_id, shift_type_id, assigned_date), fetch=False)
    
    def delete_shift_assignment(self, assignment_id):
        query = "DELETE FROM ShiftAssignments WHERE assignment_id = ?"
        return self.execute_query(query, (assignment_id,), fetch=False)
    
    # Employee Roster
    def get_employee_shifts(self, employee_id):
        query = """
        SELECT sa.assigned_date, st.shift_name, st.start_time, st.end_time, ws.is_published
        FROM ShiftAssignments sa
        JOIN ShiftTypes st ON sa.shift_type_id = st.shift_type_id
        JOIN WeeklySchedules ws ON sa.schedule_id = ws.schedule_id
        WHERE sa.employee_id = ?
        ORDER BY sa.assigned_date DESC
        """
        return self.execute_query(query, (employee_id,))
    
    # Attendance Logs
    def get_today_shift(self, employee_id, today=None):
        if today is None:
            today = date.today()
        query = """
        SELECT sa.assignment_id, st.shift_name, st.start_time, st.end_time
        FROM ShiftAssignments sa
        JOIN ShiftTypes st ON sa.shift_type_id = st.shift_type_id
        WHERE sa.employee_id = ? AND sa.assigned_date = ?
        """
        result = self.execute_query(query, (employee_id, today))
        return result[0] if result else None
    
    def get_attendance_log(self, employee_id, today=None):
        if today is None:
            today = date.today()
        query = """
        SELECT log_id, clock_in, clock_out
        FROM AttendanceLogs
        WHERE employee_id = ? AND date = ?
        """
        result = self.execute_query(query, (employee_id, today))
        return result[0] if result else None
    
    def clock_in(self, employee_id):
        query = "INSERT INTO AttendanceLogs (employee_id, date, clock_in) VALUES (?, CAST(GETDATE() AS DATE), CAST(GETDATE() AS TIME))"
        return self.execute_query(query, (employee_id,), fetch=False)
    
    def clock_out(self, log_id):
        query = "UPDATE AttendanceLogs SET clock_out = CAST(GETDATE() AS TIME) WHERE log_id = ?"
        return self.execute_query(query, (log_id,), fetch=False)
    
    # Break Logs
    def get_active_break(self, log_id):
        query = "SELECT break_id FROM BreakLogs WHERE log_id = ? AND end_time IS NULL"
        result = self.execute_query(query, (log_id,))
        return result[0] if result else None
    
    def start_break(self, log_id):
        query = "INSERT INTO BreakLogs (log_id, start_time) VALUES (?, CAST(GETDATE() AS TIME))"
        return self.execute_query(query, (log_id,), fetch=False)
    
    def end_break(self, break_id):
        query = "UPDATE BreakLogs SET end_time = CAST(GETDATE() AS TIME) WHERE break_id = ?"
        return self.execute_query(query, (break_id,), fetch=False)
    
    # Leave Requests
    def get_leave_types(self):
        return self.execute_query("SELECT leave_type_id, type_name FROM LeaveTypes")
    
    def submit_leave_request(self, employee_id, leave_type_id, start_date, end_date):
        query = """
        INSERT INTO LeaveRequests (employee_id, leave_type_id, start_date, end_date)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (employee_id, leave_type_id, start_date, end_date), fetch=False)
    
    def get_leave_requests(self, employee_id=None):
        if employee_id:
            query = """
            SELECT lr.request_id, e.first_name, e.last_name, lt.type_name, 
                   lr.start_date, lr.end_date, lr.is_approved
            FROM LeaveRequests lr
            JOIN Employees e ON lr.employee_id = e.employee_id
            JOIN LeaveTypes lt ON lr.leave_type_id = lt.leave_type_id
            WHERE lr.employee_id = ?
            ORDER BY lr.start_date DESC
            """
            return self.execute_query(query, (employee_id,))
        else:
            query = """
            SELECT lr.request_id, e.first_name, e.last_name, lt.type_name, 
                   lr.start_date, lr.end_date, lr.is_approved
            FROM LeaveRequests lr
            JOIN Employees e ON lr.employee_id = e.employee_id
            JOIN LeaveTypes lt ON lr.leave_type_id = lt.leave_type_id
            ORDER BY lr.is_approved, lr.start_date DESC
            """
            return self.execute_query(query)
    
    def approve_leave_request(self, request_id):
        query = "UPDATE LeaveRequests SET is_approved = 1 WHERE request_id = ?"
        return self.execute_query(query, (request_id,), fetch=False)
    
    # Manager Attendance Report
    def get_attendance_report(self, report_date=None):
        if report_date is None:
            report_date = date.today()
        query = """
        SELECT e.employee_id, e.first_name, e.last_name,
               st.start_time as scheduled_start, st.end_time as scheduled_end,
               al.clock_in, al.clock_out,
               CASE 
                   WHEN al.clock_in IS NULL THEN 'Absent'
                   WHEN al.clock_in > st.start_time THEN 'Late'
                   ELSE 'On Time'
               END as status,
               lr.leave_type_id
        FROM Employees e
        LEFT JOIN ShiftAssignments sa ON e.employee_id = sa.employee_id AND sa.assigned_date = ?
        LEFT JOIN ShiftTypes st ON sa.shift_type_id = st.shift_type_id
        LEFT JOIN AttendanceLogs al ON e.employee_id = al.employee_id AND al.date = ?
        LEFT JOIN LeaveRequests lr ON e.employee_id = lr.employee_id 
            AND ? BETWEEN lr.start_date AND lr.end_date AND lr.is_approved = 1
        WHERE sa.assignment_id IS NOT NULL OR lr.request_id IS NOT NULL
        ORDER BY e.last_name, e.first_name
        """
        return self.execute_query(query, (report_date, report_date, report_date))
    
    # User Account Management
    def get_all_user_accounts(self):
        query = """
        SELECT ua.user_id, ua.employee_id, e.first_name, e.last_name, ua.username, ua.is_admin
        FROM UserAccounts ua
        JOIN Employees e ON ua.employee_id = e.employee_id
        ORDER BY e.last_name, e.first_name
        """
        return self.execute_query(query)
    
    def get_employees_without_accounts(self):
        query = """
        SELECT e.employee_id, e.first_name, e.last_name
        FROM Employees e
        LEFT JOIN UserAccounts ua ON e.employee_id = ua.employee_id
        WHERE ua.user_id IS NULL
        ORDER BY e.last_name, e.first_name
        """
        return self.execute_query(query)
    
    def check_username_exists(self, username):
        query = "SELECT COUNT(*) FROM UserAccounts WHERE username = ?"
        result = self.execute_query(query, (username,))
        return result[0][0] > 0 if result else False
    
    def create_user_account(self, employee_id, username, password, is_admin):
        query = """
        INSERT INTO UserAccounts (employee_id, username, password, is_admin)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_query(query, (employee_id, username, password, is_admin), fetch=False)
    
    def delete_user_account(self, user_id):
        query = "DELETE FROM UserAccounts WHERE user_id = ?"
        return self.execute_query(query, (user_id,), fetch=False)