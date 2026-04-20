CREATE TABLE departments (
  department_id INTEGER PRIMARY KEY,
  department_name TEXT NOT NULL,
  city TEXT NOT NULL
);

CREATE TABLE employees (
  employee_id INTEGER PRIMARY KEY,
  employee_name TEXT NOT NULL,
  department_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  hire_date TEXT NOT NULL,
  FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE salaries (
  employee_id INTEGER NOT NULL,
  salary_month TEXT NOT NULL,
  base_salary REAL NOT NULL,
  bonus REAL NOT NULL,
  FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
);
