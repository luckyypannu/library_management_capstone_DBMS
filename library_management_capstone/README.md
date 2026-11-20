# Intelligent Library and Digital Resource Management System

Academic DBMS capstone built with Flask + MySQL.

## Features
- Admin sign-in
- Dashboard statistics
- Book and copy management
- Member management
- Book issue/return with transaction handling
- Late-return fine generation (₹5/day)
- Digital resource catalogue
- Overdue, popular-book and active-member reports
- SQL scripts for schema, sample data, views, indexes, joins, subqueries, CTEs and window functions

## Requirements
- Python 3.10+
- MySQL 8.0.31+
- VS Code (recommended)

## Setup (macOS / Linux)
1. Extract the ZIP and open the project folder in VS Code.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create the database and tables:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
5. Load sample data:
   ```bash
   mysql -u root -p library_management_db < database/sample_data.sql
   ```
6. Copy `.env.example` to `.env` and enter your local MySQL password:
   ```bash
   cp .env.example .env
   ```
7. Generate a secure admin password hash:
   ```bash
   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('YourNewPassword'))"
   ```
   Copy the output, then in MySQL run:
   ```sql
   USE library_management_db;
   UPDATE admins SET password_hash='PASTE_HASH_HERE' WHERE username='admin';
   ```
8. Start the app:
   ```bash
   python app.py
   ```
9. Open http://127.0.0.1:5000

Login username: `admin`
Password: the password you chose in step 7.

## Important
- Do not deploy with Flask debug mode enabled.
- Change `SECRET_KEY` and database credentials before sharing.
- The sample SQL includes a placeholder demo password hash; replace it using the steps above before login.
- Never commit `.env` to GitHub.
- Use only synthetic/sample data for academic demonstration.

## SQL practice
Run the query examples in `database/queries.sql` from MySQL Workbench or the MySQL CLI. Some DDL/DCL/TCL examples are comments so they can be run separately and safely.
