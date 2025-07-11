# clinic_app/routes/export.py

from flask import Blueprint, send_file, session, flash, redirect, url_for
from flask_login import login_required, current_user
import pandas as pd
import io
import pdfkit
from clinic_app.models.clinic_visit import ClinicVisit
from clinic_app import db
from flask import render_template

export_bp = Blueprint("export", __name__, url_prefix="/export")


def get_visits_for_user():
    if current_user.role == 'admin':
        return ClinicVisit.query.all()
    return ClinicVisit.query.filter_by(user_id=current_user.id).all()


@export_bp.route("/export_excel")
@login_required
def export_excel():
    visits = get_visits_for_user()
    df = pd.DataFrame([{
        "Date": v.visit_date,
        "Treatment": v.treatment,
        "Payment Method": v.payment_method,
        "Actual Amount": v.actual_amount,
        "Deposit Paid": "Yes" if v.deposit_paid else "No",
        "Deposit Method": v.deposit_method,
        "Net Amount": v.net_amount,
        "Month": v.month,
        "Year": v.year
    } for v in visits])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Visits')

    output.seek(0)
    return send_file(output, download_name="clinic_visits.xlsx", as_attachment=True)


@export_bp.route("/export_pdf")
@login_required
def export_pdf():
    visits = get_visits_for_user()

    try:
        html = render_template("export_pdf_template.html", visits=visits)
        pdf = pdfkit.from_string(html, False)

        return send_file(
            io.BytesIO(pdf),
            download_name="clinic_visits.pdf",
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f"Could not generate PDF: {e}", "danger")
        return redirect(url_for("dashboard.view"))
