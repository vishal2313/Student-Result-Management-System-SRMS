from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import mysql.connector
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ---------- DB CONFIG ----------
DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ---------- GRADE CALCULATION ----------
def calculate_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B"
    elif marks >= 60:
        return "C"
    elif marks >= 50:
        return "D"
    elif marks >= 40:
        return "E"
    else:
        return "Fail"

# ---------- HOME ----------
@app.route("/")
def home():
    return send_from_directory("frontend", "login.html")

@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory("frontend", filename)

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if not user or user["password"] != password:
        return jsonify({"error": "Invalid email or password"}), 401

    return jsonify({
        "message": "Login successful",
        "email": user["email"],
        "role": user.get("role", "admin")
    })

# ================= STUDENTS =================

# ADD STUDENT
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json()

    if (
        not data.get("roll_no")
        or not data.get("name")
        or not data.get("semester")
        or not data.get("academic_year")
    ):
        return jsonify({"error": "Please enter all student fields"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO students (roll_no, name, semester, academic_year) "
        "VALUES (%s,%s,%s,%s)",
        (
            data["roll_no"],
            data["name"],
            data["semester"],
            data["academic_year"]
        )
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Student added successfully"})

# EDIT STUDENT
@app.route("/students", methods=["PUT"])
def edit_student():
    data = request.get_json()

    if (
        not data.get("roll_no")
        or not data.get("name")
        or not data.get("semester")
        or not data.get("academic_year")
    ):
        return jsonify({"error": "Please enter all student fields"}), 400

    db = get_db()
    cursor = db.cursor()

    # Check whether student exists
    cursor.execute(
        "SELECT roll_no FROM students WHERE roll_no=%s",
        (data["roll_no"],)
    )

    student = cursor.fetchone()

    if not student:
        cursor.close()
        db.close()
        return jsonify({"error": "Student not found"}), 404

    # Update student
    cursor.execute("""
        UPDATE students
        SET name=%s, semester=%s, academic_year=%s
        WHERE roll_no=%s
    """, (
        data["name"],
        data["semester"],
        data["academic_year"],
        data["roll_no"]
    ))

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Student updated successfully"})

# ================= SUBJECTS =================

# ADD SUBJECT
@app.route("/subjects", methods=["POST"])
def add_subject():
    data = request.get_json()

    if not data.get("subject_name"):
        return jsonify({"error": "Please enter subject name"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO subjects (subject_name) VALUES (%s)",
        (data["subject_name"],)
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Subject added successfully"})

# EDIT SUBJECT
@app.route("/subjects", methods=["PUT"])
def edit_subject():
    data = request.get_json()

    if not data.get("id") or not data.get("subject_name"):
        return jsonify({"error": "Please enter subject ID and subject name"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        UPDATE subjects
        SET subject_name=%s
        WHERE id=%s
    """, (
        data["subject_name"],
        data["id"]
    ))

    if cursor.rowcount == 0:
        db.rollback()
        cursor.close()
        db.close()
        return jsonify({"error": "Subject ID not found"}), 404

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Subject updated successfully"})


# GET SUBJECTS
@app.route("/subjects", methods=["GET"])
def get_subjects():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM subjects")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify({"subjects": rows})

# ================= MARKS =================

# ADD MARKS
@app.route("/marks", methods=["POST"])
def add_marks():
    data = request.get_json()

    if not data.get("roll_no") or not data.get("subject_id") or data.get("marks") is None:
        return jsonify({"error": "Please enter all marks fields"}), 400

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "INSERT INTO marks (roll_no, subject_id, marks) VALUES (%s,%s,%s)",
        (
            data["roll_no"],
            data["subject_id"],
            data["marks"]
        )
    )

    db.commit()
    cursor.close()
    db.close()

    return jsonify({"message": "Marks added successfully"})


# EDIT MARKS
@app.route("/marks", methods=["PUT"])
def edit_marks():
    data = request.get_json()

    if not data.get("roll_no") or not data.get("subject_id") or data.get("marks") is None:
        return jsonify({"error": "Please enter all marks fields"}), 400

    db = get_db()
    cursor = db.cursor()

    # First check whether the record exists
    cursor.execute("""
        SELECT * FROM marks
        WHERE roll_no=%s AND subject_id=%s
    """, (
        data["roll_no"],
        data["subject_id"]
    ))

    record = cursor.fetchone()

    if not record:
        cursor.close()
        db.close()
        return jsonify({"error": "No matching marks record found"}), 404

    # Record exists, so update the marks
    cursor.execute("""
        UPDATE marks
        SET marks=%s
        WHERE roll_no=%s AND subject_id=%s
    """, (
        data["marks"],
        data["roll_no"],
        data["subject_id"]
    ))

    db.commit()

    cursor.close()
    db.close()

    return jsonify({"message": "Marks updated successfully"})

# ================= RESULT =================

@app.route("/result/<roll_no>")
def get_result(roll_no):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.roll_no, s.name, s.semester, s.academic_year,
               sub.subject_name, m.marks
        FROM students s
        JOIN marks m ON s.roll_no = m.roll_no
        JOIN subjects sub ON m.subject_id = sub.id
        WHERE s.roll_no=%s
    """, (roll_no,))
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    
    if not rows:
     return jsonify({"error": "Invalid roll number"}), 404
 
    total = sum(r["marks"] for r in rows)
    percentage = (total / (len(rows) * 100)) * 100

    return jsonify({
        "roll_no": rows[0]["roll_no"],
        "name": rows[0]["name"],
        "semester": rows[0]["semester"],
        "academic_year": rows[0]["academic_year"],
        "subjects": rows,
        "total": total,
        "percentage": round(percentage, 2)
    })

# ================= RESULT PDF =================

@app.route("/result_pdf/<roll_no>")
def result_pdf(roll_no):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.roll_no, s.name, s.semester, s.academic_year,
               sub.subject_name, m.marks
        FROM students s
        JOIN marks m ON s.roll_no = m.roll_no
        JOIN subjects sub ON m.subject_id = sub.id
        WHERE s.roll_no=%s
    """, (roll_no,))

    rows = cursor.fetchall()

    cursor.close()
    db.close()

    if not rows:
        return jsonify({"message": "Result not found"}), 404

    # ---------- CALCULATIONS ----------
    total = sum(r["marks"] for r in rows)
    percentage = (total / (len(rows) * 100)) * 100

    # ---------- PDF ----------
    buffer = io.BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4

    # ---------- HEADER ----------
    pdf.setFillColorRGB(0.2, 0.40, 0.9)

    pdf.roundRect(
     55,
     height - 80,
     width - 110,
     38,
     8,
     fill=1,
     stroke=0
     )

    pdf.setFillColorRGB(1, 1, 1)
    pdf.setFont("Helvetica-Bold", 16)

    pdf.drawCentredString(
     width / 2,
     height - 67,
     "SRMS"
    )

    pdf.setFillColorRGB(0.10, 0.14, 0.20)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(
        width / 2,
        height - 105,
        "Student's Result"
    )

    # ---------- STUDENT INFORMATION ----------
    info_y = height - 150

    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(55, info_y, "Student Information")

    pdf.setStrokeColorRGB(0.65, 0.87, 0.90)
    pdf.line(55, info_y - 8, width - 55, info_y - 8)

    pdf.setFont("Helvetica", 11)

    pdf.drawString(
        60, info_y - 35,
        f"Name: {rows[0]['name']}"
    )

    pdf.drawString(
        320, info_y - 35,
        f"Roll No: {rows[0]['roll_no']}"
    )

    pdf.drawString(
        60, info_y - 60,
        f"Semester: {rows[0]['semester']}"
    )

    pdf.drawString(
        320, info_y - 60,
        f"Academic Year: {rows[0]['academic_year']}"
    )

    # ---------- TABLE ----------
    table_top = info_y - 80

    x_subject = 60
    x_marks = 300
    x_grade = 410

    row_height = 28

    # Header background
    pdf.setFillColorRGB(0.7, 0.6, 0.98)
    pdf.rect(
        55,
        table_top - row_height,
        width - 110,
        row_height,
        fill=1,
        stroke=0
    )

    # Table header
    pdf.setFillColorRGB(0.10, 0.14, 0.20)
    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        x_subject,
        table_top - 18,
        "Subject"
    )

    pdf.drawCentredString(
        x_marks,
        table_top - 18,
        "Marks"
    )

    pdf.drawCentredString(
        x_grade,
        table_top - 18,
        "Grade"
    )

    # Table rows
    y = table_top - row_height

    pdf.setFont("Helvetica", 11)

    for r in rows:

        y -= row_height

        grade = calculate_grade(r["marks"])

        pdf.setFillColorRGB(0.10, 0.14, 0.20)

        pdf.drawString(
            x_subject,
            y + 9,
            r["subject_name"]
        )

        pdf.drawCentredString(
            x_marks,
            y + 9,
            str(r["marks"])
        )

        pdf.drawCentredString(
            x_grade,
            y + 9,
            grade
        )

        # Row line
        pdf.setStrokeColorRGB(0.85, 0.87, 0.90)

        pdf.line(
            55,
            y,
            width - 55,
            y
        )

    # Outer table border
    table_bottom = y

    pdf.rect(
        55,
        table_bottom,
        width - 110,
        table_top - table_bottom,
        fill=0,
        stroke=1
    )

    # Vertical separators
    pdf.line(
        250,
        table_bottom,
        250,
        table_top
    )

    pdf.line(
        355,
        table_bottom,
        355,
        table_top
    )

    # ---------- SUMMARY ----------
    summary_y = table_bottom - 30

    pdf.setFillColorRGB(0.75, 0.88, 0.95)
    
    pdf.roundRect(
        55,
        summary_y - 55,
        width - 110,
        50,
        8,
        fill=1,
        stroke=0
    )

    pdf.setFillColorRGB(0.10, 0.14, 0.20)

    pdf.setFont("Helvetica-Bold", 11)

    pdf.drawString(
        75,
        summary_y - 22,
        f"Total Marks: {total}"
    )

    pdf.drawString(
        330,
        summary_y - 22,
        f"Percentage: {percentage:.2f}%"
    )

    # ---------- FOOTER ----------
    pdf.setFont("Helvetica", 8)
    pdf.setFillColorRGB(0.45, 0.48, 0.52)

    pdf.drawCentredString(
        width / 2,
        35,
        "Student Result Management System"
    )

    pdf.drawCentredString(
        width / 2,
        22,
        "Generated electronically"
    )

    # ---------- SAVE ----------
    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{roll_no}_result.pdf",
        mimetype="application/pdf"
    )

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
