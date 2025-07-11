# clinic_app/routes/api.py

from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from clinic_app.models.clinic_visit import ClinicVisit
from clinic_app import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/dashboard/stats')
@login_required
def dashboard_stats():
    query = ClinicVisit.query

    # Filter for non-admin users
    if current_user.role != 'admin':
        query = query.filter_by(user_id=current_user.id)

    visits = query.all()

    treatment_counts = {}
    treatment_revenue = {}

    for v in visits:
        treatment = v.treatment or "Unknown"
        treatment_counts[treatment] = treatment_counts.get(treatment, 0) + 1
        treatment_revenue[treatment] = treatment_revenue.get(treatment, 0) + (v.net_amount or 0)

    return jsonify({
        "treatment_counts": treatment_counts,
        "treatment_revenue": treatment_revenue
    })
