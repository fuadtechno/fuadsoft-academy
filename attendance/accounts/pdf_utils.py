import io
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


class PDFWithHeader(SimpleDocTemplate):
    def __init__(self, filename, title, school_name="School Management System", **kwargs):
        self.school_name = school_name
        self.report_title = title
        super().__init__(filename, **kwargs)

    def beforePage(self):
        self.canv.saveState()
        self.canv.setFont("Helvetica-Bold", 16)
        self.canv.drawCentredString(self.pagesize[0] / 2, self.pagesize[1] - 30, self.school_name)
        self.canv.setFont("Helvetica", 10)
        self.canv.drawCentredString(self.pagesize[0] / 2, self.pagesize[1] - 45, self.report_title)
        self.canv.setFont("Helvetica", 8)
        self.canv.drawRightString(self.pagesize[0] - 20, self.pagesize[1] - 30, f"Generated: {date.today().strftime('%Y-%m-%d')}")
        self.canv.setLineWidth(0.5)
        self.canv.line(20, self.pagesize[1] - 55, self.pagesize[0] - 20, self.pagesize[1] - 55)
        self.canv.restoreState()


def generate_student_list_pdf(students, school_name="School Management System"):
    buffer = io.BytesIO()
    doc = PDFWithHeader(buffer, "Student List Report", school_name, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=60, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    data = [["#", "Name", "Email", "Class", "Roll No", "Status"]]
    for i, s in enumerate(students, 1):
        try:
            user = s.user
            name = f"{user.first_name} {user.last_name}".strip() or user.username
            email = user.email or "-"
        except Exception:
            name = "-"
            email = "-"
        class_name = s.class_enrolled.name if s.class_enrolled else "-"
        roll = str(s.roll_number) if s.roll_number else "-"
        status = "Active" if s.is_active else "Inactive"
        data.append([i, name, email, class_name, roll, status])

    table = Table(data, colWidths=[25, 120, 130, 60, 40, 45])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#667eea")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (3, 1), (4, -1), "CENTER"),
        ("ALIGN", (5, 1), (5, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_fee_collection_pdf(payments, school_name="School Management System"):
    buffer = io.BytesIO()
    doc = PDFWithHeader(buffer, "Fee Collection Report", school_name, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=60, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    total_amount = sum(p.amount_paid for p in payments)
    elements.append(Paragraph(f"Total Collection: <b>${total_amount:,.2f}</b>", styles["Normal"]))
    elements.append(Spacer(1, 12))

    data = [["#", "Student", "Amount", "Payment Date", "Month", "Status"]]
    for i, p in enumerate(payments, 1):
        student = p.student.user.get_full_name() if p.student and p.student.user else "-"
        amount = f"${p.amount_paid:,.2f}"
        pay_date = p.payment_date.strftime("%Y-%m-%d") if p.payment_date else "-"
        month = p.month if p.month else "-"
        status = p.payment_status.capitalize() if p.payment_status else "-"
        data.append([i, student, amount, pay_date, month, status])

    table = Table(data, colWidths=[25, 130, 70, 75, 60, 50])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#11998e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (2, 1), (2, -1), "RIGHT"),
        ("ALIGN", (5, 1), (5, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_exam_results_pdf(results, school_name="School Management System"):
    buffer = io.BytesIO()
    doc = PDFWithHeader(buffer, "Exam Results Report", school_name, pagesize=A4, leftMargin=20, rightMargin=20, topMargin=60, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    data = [["#", "Student", "Exam", "Subject", "Score", "Grade", "Remarks"]]
    for i, r in enumerate(results, 1):
        student = r.student.user.get_full_name() if r.student and r.student.user else "-"
        exam = r.exam.name if r.exam else "-"
        subject = r.exam.subject.name if r.exam and r.exam.subject else "-"
        score = f"{r.score}/{r.exam.total_marks}" if r.exam else "-"
        grade = r.grade or "-"
        remarks = r.remarks or "-"
        data.append([i, student, exam, subject, score, grade, remarks])

    table = Table(data, colWidths=[25, 100, 80, 60, 40, 35, 60])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f5576c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("ALIGN", (4, 1), (4, -1), "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f8f9fa")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer