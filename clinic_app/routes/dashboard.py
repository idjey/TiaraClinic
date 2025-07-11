from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from clinic_app import db
from clinic_app.models.clinic_visit import ClinicVisit
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def view():
    visits = ClinicVisit.query.filter_by(user_id=current_user.id).all(
    ) if current_user.role == 'standard' else ClinicVisit.query.all()
    return render_template('dashboard.html', visits=visits)


@dashboard_bp.route('/visit', methods=['POST'])
@login_required
def add_visit():
    data = request.json
    visit = ClinicVisit(
        user_id=current_user.id,
        visit_date=datetime.strptime(data['visit_date'], "%Y-%m-%d"),
        treatment=data['treatment'],
        payment_method=data['payment_method'],
        actual_amount=float(data['actual_amount']),
        deposit_paid=data['deposit_paid'],
        deposit_amount=100.0 if data['deposit_paid'] else 0.0,
        deposit_method=data['deposit_method'] if data['deposit_paid'] else None,
        net_amount=float(data['actual_amount']) -
        (100.0 if data['deposit_paid'] else 0.0),
        month=data['month'],
        year=int(data['year'])
    )
    db.session.add(visit)
    db.session.commit()
    return jsonify({'status': 'success', 'id': visit.id})


@dashboard_bp.route('/visit/<int:id>', methods=['PUT'])
@login_required
def edit_visit(id):
    visit = ClinicVisit.query.get_or_404(id)
    data = request.json
    visit.visit_date = datetime.strptime(data['visit_date'], "%Y-%m-%d")
    visit.treatment = data['treatment']
    visit.payment_method = data['payment_method']
    visit.actual_amount = float(data['actual_amount'])
    visit.deposit_paid = data['deposit_paid']
    visit.deposit_amount = 100.0 if data['deposit_paid'] else 0.0
    visit.deposit_method = data['deposit_method'] if data['deposit_paid'] else None
    visit.net_amount = visit.actual_amount - visit.deposit_amount
    visit.month = data['month']
    visit.year = int(data['year'])
    db.session.commit()
    return jsonify({'status': 'updated'})


@dashboard_bp.route('/visit/<int:id>', methods=['DELETE'])
@login_required
def delete_visit(id):
    visit = ClinicVisit.query.get_or_404(id)
    db.session.delete(visit)
    db.session.commit()
    return jsonify({'status': 'deleted'})


@dashboard_bp.route('/api/dashboard/stats')
@login_required
def dashboard_stats():
    from clinic_app.models.clinic_visit import ClinicVisit
    from flask import jsonify
    from sqlalchemy import func

    qb = ClinicVisit.query.filter_by(
        user_id=current_user.id) if current_user.role != 'admin' else ClinicVisit.query

    counts = dict(qb.with_entities(ClinicVisit.treatment, func.count(
        ClinicVisit.id)).group_by(ClinicVisit.treatment).all())
    revenue = dict(qb.with_entities(ClinicVisit.treatment, func.sum(
        ClinicVisit.net_amount)).group_by(ClinicVisit.treatment).all())

    return jsonify({
        'treatment_counts': counts,
        'treatment_revenue': revenue
    })
