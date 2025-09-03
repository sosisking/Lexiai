    consents = db.relationship('UserConsent', backref='user', lazy=True, cascade='all, even_if_not_found_in_db')

