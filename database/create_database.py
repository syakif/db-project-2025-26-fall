import pyodbc

def create_database():
    """Creates the database and all tables with sample data"""
    
    # Connect to SQL Server (without database)
    try:
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS;'
            'Trusted_Connection=yes;'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute("IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'DBPROJECT') CREATE DATABASE DBPROJECT")
        print("Database created successfully!")
        
        conn.close()
        
        # Connect to the new database
        conn = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS;'
            'DATABASE=DBPROJECT;'
            'Trusted_Connection=yes;'
        )
        cursor = conn.cursor()
        
        # Create tables (from CREATE QUERIES.pdf)
        tables = [
            """CREATE TABLE WorkLocations (
                location_id INT PRIMARY KEY IDENTITY(1,1),
                address VARCHAR(150) NOT NULL
            )""",
            """CREATE TABLE Skills (
                skill_id INT PRIMARY KEY IDENTITY(1,1),
                skill_name VARCHAR(50) NOT NULL
            )""",
            """CREATE TABLE Departments (
                department_id INT PRIMARY KEY IDENTITY(1,1),
                department_name VARCHAR(50) NOT NULL,
                location_id INT REFERENCES WorkLocations(location_id)
            )""",
            """CREATE TABLE JobTitles (
                job_id INT PRIMARY KEY IDENTITY(1,1),
                title_name VARCHAR(50) NOT NULL
            )""",
            """CREATE TABLE EmploymentTypes (
                type_id INT PRIMARY KEY IDENTITY(1,1),
                type_name VARCHAR(50) NOT NULL
            )""",
            """CREATE TABLE Employees (
                employee_id INT PRIMARY KEY IDENTITY(1,1),
                first_name VARCHAR(50) NOT NULL,
                last_name VARCHAR(50) NOT NULL,
                department_id INT REFERENCES Departments(department_id),
                job_id INT REFERENCES JobTitles(job_id),
                type_id INT REFERENCES EmploymentTypes(type_id),
                skill_id INT REFERENCES Skills(skill_id)
            )""",
            """CREATE TABLE UserAccounts (
                user_id INT PRIMARY KEY IDENTITY(1,1),
                employee_id INT UNIQUE REFERENCES Employees(employee_id),
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(50) NOT NULL,
                is_admin BIT DEFAULT 0
            )""",
            """CREATE TABLE ShiftTypes (
                shift_type_id INT PRIMARY KEY IDENTITY(1,1),
                shift_name VARCHAR(20) NOT NULL,
                start_time TIME NOT NULL,
                end_time TIME NOT NULL
            )""",
            """CREATE TABLE WeeklySchedules (
                schedule_id INT PRIMARY KEY IDENTITY(1,1),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                is_published BIT DEFAULT 0
            )""",
            """CREATE TABLE EmployeeAvailability (
                availability_id INT PRIMARY KEY IDENTITY(1,1),
                employee_id INT REFERENCES Employees(employee_id),
                day_of_week VARCHAR(10) NOT NULL,
                is_available BIT DEFAULT 1
            )""",
            """CREATE TABLE ShiftAssignments (
                assignment_id INT PRIMARY KEY IDENTITY(1,1),
                schedule_id INT REFERENCES WeeklySchedules(schedule_id),
                employee_id INT REFERENCES Employees(employee_id),
                shift_type_id INT REFERENCES ShiftTypes(shift_type_id),
                assigned_date DATE NOT NULL
            )""",
            """CREATE TABLE LeaveTypes (
                leave_type_id INT PRIMARY KEY IDENTITY(1,1),
                type_name VARCHAR(50) NOT NULL
            )""",
            """CREATE TABLE LeaveRequests (
                request_id INT PRIMARY KEY IDENTITY(1,1),
                employee_id INT REFERENCES Employees(employee_id),
                leave_type_id INT REFERENCES LeaveTypes(leave_type_id),
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                is_approved BIT DEFAULT 0
            )""",
            """CREATE TABLE AttendanceLogs (
                log_id INT PRIMARY KEY IDENTITY(1,1),
                employee_id INT REFERENCES Employees(employee_id),
                date DATE DEFAULT CAST(GETDATE() AS DATE),
                clock_in TIME,
                clock_out TIME
            )""",
            """CREATE TABLE BreakLogs (
                break_id INT PRIMARY KEY IDENTITY(1,1),
                log_id INT REFERENCES AttendanceLogs(log_id),
                start_time TIME NOT NULL,
                end_time TIME
            )"""
        ]
        
        for table_sql in tables:
            try:
                cursor.execute(table_sql)
                print(f"Table created successfully!")
            except Exception as e:
                print(f"Table creation warning: {e}")
        
        # Insert sample data (from INSERT QUERIES.pdf)
        inserts = [
            "INSERT INTO WorkLocations (address) VALUES ('123 Tech Park, Building A'), ('456 Industrial Rd, Warehouse 1')",
            "INSERT INTO Skills (skill_name) VALUES ('Python Programming'), ('Project Management'), ('First Aid Certified')",
            "INSERT INTO Departments (department_name, location_id) VALUES ('IT Department', 1), ('HR Department', 1), ('Logistics', 2)",
            "INSERT INTO JobTitles (title_name) VALUES ('Software Engineer'), ('HR Manager'), ('Warehouse Supervisor')",
            "INSERT INTO EmploymentTypes (type_name) VALUES ('Full-Time'), ('Part-Time')",
            "INSERT INTO Employees (first_name, last_name, department_id, job_id, type_id, skill_id) VALUES ('John', 'Doe', 1, 1, 1, 1), ('Alice', 'Smith', 2, 2, 1, 2), ('Bob', 'Jones', 3, 3, 2, 3)",
            "INSERT INTO UserAccounts (employee_id, username, password, is_admin) VALUES (1, 'jdoe', 'pass123', 0), (2, 'asmith', 'admin789', 1), (3, 'bjones', 'pass456', 0)",
            "INSERT INTO ShiftTypes (shift_name, start_time, end_time) VALUES ('Morning', '09:00:00', '17:00:00'), ('Night', '18:00:00', '02:00:00')",
            "INSERT INTO WeeklySchedules (start_date, end_date, is_published) VALUES ('2025-12-01', '2025-12-07', 1)",
            "INSERT INTO EmployeeAvailability (employee_id, day_of_week, is_available) VALUES (1, 'Monday', 1), (1, 'Tuesday', 1), (3, 'Monday', 0)",
            "INSERT INTO ShiftAssignments (schedule_id, employee_id, shift_type_id, assigned_date) VALUES (1, 1, 1, '2025-12-01'), (1, 2, 1, '2025-12-01'), (1, 3, 2, '2025-12-02')",
            "INSERT INTO LeaveTypes (type_name) VALUES ('Sick Leave'), ('Vacation')",
            "INSERT INTO LeaveRequests (employee_id, leave_type_id, start_date, end_date, is_approved) VALUES (1, 2, '2025-12-20', '2025-12-25', 1)",
            "INSERT INTO AttendanceLogs (employee_id, date, clock_in, clock_out) VALUES (1, '2025-12-01', '08:55:00', '17:05:00'), (2, '2025-12-01', '09:15:00', '17:00:00')",
            "INSERT INTO BreakLogs (log_id, start_time, end_time) VALUES (1, '12:30:00', '13:00:00')"
        ]
        
        for insert_sql in inserts:
            try:
                cursor.execute(insert_sql)
                conn.commit()
                print(f"Data inserted successfully!")
            except Exception as e:
                print(f"Insert warning: {e}")
        
        conn.close()
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    create_database()