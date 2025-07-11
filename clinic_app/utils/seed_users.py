import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from clinic_app import create_app, db
from clinic_app.models import User 
from typing import List, Dict


def seed_users():
    app = create_app()
    with app.app_context():
        users: List[Dict[str, str]] = [
            {"email": "h.thiara0@yahoo.com", "role": "admin"},
            {"email": "tiara.aesthetics@gmail.com", "role": "standard"},
            {"email": "info@tiaraclinics.com", "role": "standard"},
            {"email": "djkanjaria@gmail.com", "role": "admin"},
        ]

        for user in users:
            if not User.query.filter_by(email=user["email"]).first():
                new_user = User()
                new_user.email = user["email"]
                new_user.role = user["role"]
                db.session().add(new_user)

        db.session().commit()
        print("✅ Users seeded successfully!")


if __name__ == "__main__":
    seed_users()
