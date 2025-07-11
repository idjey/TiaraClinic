from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os

from clinic_app.utils.excel_parser import validate_excel
from clinic_app import db
from clinic_app.models.clinic_visit import ClinicVisit

import_wizard_bp = Blueprint("import_wizard", __name__)
UPLOAD_FOLDER = "clinic_app/uploads"
ALLOWED_EXTENSIONS = {"xlsx"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@import_wizard_bp.route("/import", methods=["GET", "POST"])
@login_required
def import_excel():
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename or not allowed_file(file.filename):
            flash("Please upload a valid .xlsx file", "danger")
            return redirect(url_for("import_wizard.import_excel"))

        filename = secure_filename(file.filename or "")
        path = os.path.join(UPLOAD_FOLDER, filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(path)

        # ✅ Use our Excel parser
        rows, error = validate_excel(path)
        if error:
            flash(error, "danger")
            return redirect(url_for("import_wizard.import_excel"))

        if rows is None:
            flash("No data found in the file", "warning")
            return redirect(url_for("import_wizard.import_excel"))

        session["import_data"] = rows
        flash(f"{len(rows) if rows is not None else 0} rows ready to import", "info")
        return redirect(url_for("import_wizard.preview_import"))

    return render_template("import_wizard.html")


@import_wizard_bp.route("/import/preview", methods=["GET", "POST"])
@login_required
def preview_import():
    rows = session.get("import_data")
    if not rows:
        flash("No data to import", "warning")
        return redirect(url_for("import_wizard.import_excel"))

    if request.method == "POST":
        for row in rows:
            visit = ClinicVisit()
            visit.user_id = current_user.id
            visit.visit_date = row["visit_date"]
            visit.treatment = row["treatment"]
            visit.payment_method = row["payment_method"]
            visit.actual_amount = row["actual_amount"]
            visit.deposit_paid = bool(row["deposit_paid"])
            visit.deposit_amount = 100.0 if row["deposit_paid"] else 0.0
            visit.deposit_method = row["deposit_method"] if row["deposit_paid"] else None
            visit.net_amount = float(row["actual_amount"]) - (100.0 if row["deposit_paid"] else 0.0)
            visit.month = row["month"]
            visit.year = row["year"]
            db.session.add(visit)
        db.session.commit()
        flash("Data imported successfully", "success")
        session.pop("import_data", None)
        return redirect(url_for("dashboard.view"))

    return render_template("import_preview.html", rows=rows)
