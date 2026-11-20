import os
from datetime import date, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-development-secret")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "library_management_db"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def query_db(sql, params=(), fetch=True):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        result = cur.fetchall() if fetch else None
        if not fetch:
            conn.commit()
        return result
    finally:
        cur.close()
        conn.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def home():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        try:
            user = query_db("SELECT * FROM admins WHERE username=%s AND is_active=1", (username,))
            if user and check_password_hash(user[0]["password_hash"], password):
                session["user_id"] = user[0]["admin_id"]
                session["username"] = user[0]["username"]
                flash("Welcome back!", "success")
                return redirect(url_for("dashboard"))
            flash("Invalid username or password.", "danger")
        except Error as e:
            flash(f"Database error: {e}", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    stats = {}
    for key, sql in {
        "books": "SELECT COUNT(*) n FROM books",
        "copies": "SELECT COUNT(*) n FROM book_copies",
        "available": "SELECT COUNT(*) n FROM book_copies WHERE status='AVAILABLE'",
        "members": "SELECT COUNT(*) n FROM members WHERE status='ACTIVE'",
        "issued": "SELECT COUNT(*) n FROM loans WHERE status='ISSUED'",
        "overdue": "SELECT COUNT(*) n FROM loans WHERE status='ISSUED' AND due_date<CURDATE()",
        "fines": "SELECT COALESCE(SUM(amount-paid_amount),0) n FROM fines WHERE status<>'WAIVED'"
    }.items():
        stats[key] = query_db(sql)[0]["n"]
    recent = query_db("""SELECT l.loan_id, m.full_name, b.title, l.issue_date, l.due_date, l.status
                         FROM loans l JOIN members m ON m.member_id=l.member_id
                         JOIN book_copies bc ON bc.copy_id=l.copy_id
                         JOIN books b ON b.book_id=bc.book_id
                         ORDER BY l.loan_id DESC LIMIT 8""")
    popular = query_db("""SELECT b.title, COUNT(*) borrow_count FROM loans l
                          JOIN book_copies bc ON bc.copy_id=l.copy_id
                          JOIN books b ON b.book_id=bc.book_id
                          GROUP BY b.book_id,b.title ORDER BY borrow_count DESC LIMIT 5""")
    return render_template("dashboard.html", stats=stats, recent=recent, popular=popular)

@app.route("/books", methods=["GET", "POST"])
@login_required
def books():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        isbn = request.form.get("isbn", "").strip()
        author_id = request.form.get("author_id") or None
        publisher_id = request.form.get("publisher_id") or None
        category_id = request.form.get("category_id") or None
        published_year = request.form.get("published_year") or None
        copies = max(1, int(request.form.get("copies", 1)))
        if not title or not isbn:
            flash("Title and ISBN are required.", "danger")
        else:
            conn = get_db()
            cur = conn.cursor()
            try:
                cur.execute("""INSERT INTO books(isbn,title,publisher_id,category_id,published_year)
                               VALUES(%s,%s,%s,%s,%s)""",
                            (isbn,title,publisher_id,category_id,published_year))
                book_id = cur.lastrowid
                if author_id:
                    cur.execute("INSERT INTO book_authors(book_id,author_id) VALUES(%s,%s)", (book_id,author_id))
                for _ in range(copies):
                    cur.execute("INSERT INTO book_copies(book_id,accession_no,status) VALUES(%s,%s,'AVAILABLE')",
                                (book_id, f"BK-{book_id}-{_+1}"))
                conn.commit()
                flash("Book and copies added successfully.", "success")
            except Error as e:
                conn.rollback()
                flash(f"Could not add book: {e}", "danger")
            finally:
                cur.close()
                conn.close()
        return redirect(url_for("books"))
    search = request.args.get("q", "").strip()
    rows = query_db("""SELECT b.book_id,b.isbn,b.title,COALESCE(c.category_name,'—') category_name,
                       COUNT(bc.copy_id) total_copies,
                       SUM(CASE WHEN bc.status='AVAILABLE' THEN 1 ELSE 0 END) available_copies
                       FROM books b LEFT JOIN categories c ON c.category_id=b.category_id
                       LEFT JOIN book_copies bc ON bc.book_id=b.book_id
                       WHERE b.title LIKE %s OR b.isbn LIKE %s
                       GROUP BY b.book_id,b.isbn,b.title,c.category_name ORDER BY b.title""",
                    (f"%{search}%", f"%{search}%"))
    authors = query_db("SELECT author_id,author_name FROM authors ORDER BY author_name")
    publishers = query_db("SELECT publisher_id,publisher_name FROM publishers ORDER BY publisher_name")
    categories = query_db("SELECT category_id,category_name FROM categories ORDER BY category_name")
    return render_template("books.html", books=rows, authors=authors, publishers=publishers, categories=categories, q=search)

@app.route("/books/delete/<int:book_id>", methods=["POST"])
@login_required
def delete_book(book_id):
    try:
        query_db("DELETE FROM books WHERE book_id=%s", (book_id,), fetch=False)
        flash("Book deleted.", "success")
    except Error as e:
        flash(f"Cannot delete this book because it may have circulation history: {e}", "danger")
    return redirect(url_for("books"))

@app.route("/members", methods=["GET", "POST"])
@login_required
def members():
    if request.method == "POST":
        try:
            query_db("""INSERT INTO members(member_no,full_name,email,phone,joined_on,status)
                        VALUES(%s,%s,%s,%s,CURDATE(),'ACTIVE')""",
                     (request.form["member_no"].strip(), request.form["full_name"].strip(),
                      request.form["email"].strip(), request.form.get("phone","").strip()), fetch=False)
            flash("Member added.", "success")
        except Error as e:
            flash(f"Could not add member: {e}", "danger")
        return redirect(url_for("members"))
    q = request.args.get("q","").strip()
    rows = query_db("""SELECT * FROM members WHERE full_name LIKE %s OR member_no LIKE %s
                       ORDER BY member_id DESC""", (f"%{q}%",f"%{q}%"))
    return render_template("members.html", members=rows, q=q)

@app.route("/members/status/<int:member_id>", methods=["POST"])
@login_required
def member_status(member_id):
    query_db("UPDATE members SET status=IF(status='ACTIVE','INACTIVE','ACTIVE') WHERE member_id=%s",
             (member_id,), fetch=False)
    flash("Member status updated.", "success")
    return redirect(url_for("members"))

@app.route("/loans", methods=["GET", "POST"])
@login_required
def loans():
    if request.method == "POST":
        member_id = request.form.get("member_id")
        copy_id = request.form.get("copy_id")
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()
            cur.execute("SELECT status FROM members WHERE member_id=%s FOR UPDATE", (member_id,))
            member = cur.fetchone()
            cur.execute("SELECT status FROM book_copies WHERE copy_id=%s FOR UPDATE", (copy_id,))
            copy = cur.fetchone()
            if not member or member["status"] != "ACTIVE":
                raise ValueError("Member is not active.")
            if not copy or copy["status"] != "AVAILABLE":
                raise ValueError("Selected copy is not available.")
            issue_date = date.today()
            due_date = issue_date + timedelta(days=14)
            cur.execute("""INSERT INTO loans(member_id,copy_id,issue_date,due_date,status)
                           VALUES(%s,%s,%s,%s,'ISSUED')""", (member_id,copy_id,issue_date,due_date))
            cur.execute("UPDATE book_copies SET status='ISSUED' WHERE copy_id=%s", (copy_id,))
            conn.commit()
            flash(f"Book issued. Due date: {due_date}", "success")
        except Exception as e:
            conn.rollback()
            flash(f"Issue failed: {e}", "danger")
        finally:
            cur.close()
            conn.close()
        return redirect(url_for("loans"))
    members_list = query_db("SELECT member_id,member_no,full_name FROM members WHERE status='ACTIVE' ORDER BY full_name")
    copies = query_db("""SELECT bc.copy_id,bc.accession_no,b.title FROM book_copies bc
                         JOIN books b ON b.book_id=bc.book_id WHERE bc.status='AVAILABLE' ORDER BY b.title""")
    rows = query_db("""SELECT l.loan_id,m.full_name,b.title,bc.accession_no,l.issue_date,l.due_date,l.return_date,l.status
                       FROM loans l JOIN members m ON m.member_id=l.member_id
                       JOIN book_copies bc ON bc.copy_id=l.copy_id
                       JOIN books b ON b.book_id=bc.book_id ORDER BY l.loan_id DESC""")
    return render_template("loans.html", loans=rows, members=members_list, copies=copies)

@app.route("/loans/return/<int:loan_id>", methods=["POST"])
@login_required
def return_loan(loan_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cur.execute("""SELECT loan_id,copy_id,due_date,status FROM loans
                       WHERE loan_id=%s FOR UPDATE""", (loan_id,))
        loan = cur.fetchone()
        if not loan or loan["status"] != "ISSUED":
            raise ValueError("Loan is not currently issued.")
        today = date.today()
        cur.execute("UPDATE loans SET status='RETURNED',return_date=%s WHERE loan_id=%s", (today,loan_id))
        cur.execute("UPDATE book_copies SET status='AVAILABLE' WHERE copy_id=%s", (loan["copy_id"],))
        late_days = max(0,(today-loan["due_date"]).days)
        if late_days:
            amount = late_days * 5
            cur.execute("""INSERT INTO fines(loan_id,amount,paid_amount,status,created_on)
                           VALUES(%s,%s,0,'UNPAID',%s)""", (loan_id,amount,today))
        conn.commit()
        flash(f"Book returned. Late days: {late_days}. Fine: ₹{late_days*5}", "success")
    except Exception as e:
        conn.rollback()
        flash(f"Return failed: {e}", "danger")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("loans"))

@app.route("/fines", methods=["GET", "POST"])
@login_required
def fines():
    if request.method == "POST":
        fine_id = request.form.get("fine_id")
        query_db("UPDATE fines SET paid_amount=amount,status='PAID' WHERE fine_id=%s", (fine_id,), fetch=False)
        flash("Fine marked as paid.", "success")
        return redirect(url_for("fines"))
    rows = query_db("""SELECT f.*,m.full_name,b.title FROM fines f
                       JOIN loans l ON l.loan_id=f.loan_id
                       JOIN members m ON m.member_id=l.member_id
                       JOIN book_copies bc ON bc.copy_id=l.copy_id
                       JOIN books b ON b.book_id=bc.book_id ORDER BY f.fine_id DESC""")
    return render_template("fines.html", fines=rows)

@app.route("/digital", methods=["GET", "POST"])
@login_required
def digital():
    if request.method == "POST":
        query_db("""INSERT INTO digital_resources(title,resource_type,url,description,added_on)
                    VALUES(%s,%s,%s,%s,CURDATE())""",
                 (request.form["title"],request.form["resource_type"],request.form["url"],request.form.get("description","")),
                 fetch=False)
        flash("Digital resource added.", "success")
        return redirect(url_for("digital"))
    rows = query_db("SELECT * FROM digital_resources ORDER BY resource_id DESC")
    return render_template("digital.html", resources=rows)

@app.route("/reports")
@login_required
def reports():
    overdue = query_db("""SELECT m.full_name,b.title,l.due_date,DATEDIFF(CURDATE(),l.due_date) late_days
                          FROM loans l JOIN members m ON m.member_id=l.member_id
                          JOIN book_copies bc ON bc.copy_id=l.copy_id JOIN books b ON b.book_id=bc.book_id
                          WHERE l.status='ISSUED' AND l.due_date<CURDATE() ORDER BY late_days DESC""")
    popular = query_db("""SELECT b.title,COUNT(*) borrow_count FROM loans l
                          JOIN book_copies bc ON bc.copy_id=l.copy_id JOIN books b ON b.book_id=bc.book_id
                          GROUP BY b.book_id,b.title ORDER BY borrow_count DESC LIMIT 10""")
    active = query_db("""SELECT m.full_name,COUNT(*) borrow_count FROM loans l
                         JOIN members m ON m.member_id=l.member_id
                         GROUP BY m.member_id,m.full_name ORDER BY borrow_count DESC LIMIT 10""")
    return render_template("reports.html", overdue=overdue, popular=popular, active=active)

@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
