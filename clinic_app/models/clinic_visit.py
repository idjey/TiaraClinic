from clinic_app import db

class ClinicVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    visit_date = db.Column(db.Date, nullable=False)
    treatment = db.Column(db.String(100), nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    actual_amount = db.Column(db.Float, nullable=False)
    deposit_paid = db.Column(db.Boolean, default=False)
    deposit_amount = db.Column(db.Float, default=0.0)
    deposit_method = db.Column(db.String(20))
    net_amount = db.Column(db.Float)
    month = db.Column(db.String(20))
    year = db.Column(db.Integer)
