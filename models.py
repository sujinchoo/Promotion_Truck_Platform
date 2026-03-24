from datetime import datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Lead(db.Model):
    __tablename__ = "leads"
    __table_args__ = (
        db.Index("ix_leads_created_at", "created_at"),
        db.Index("ix_leads_status", "status"),
        db.Index("ix_leads_landing_page", "landing_page"),
    )

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    landing_page = db.Column(db.String(50), default="main", nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    region = db.Column(db.String(100), nullable=False)
    vehicle_type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="신규", nullable=False)
    utm_source = db.Column(db.String(100), nullable=True)
    utm_medium = db.Column(db.String(100), nullable=True)
    utm_campaign = db.Column(db.String(100), nullable=True)
    referrer = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    agreement = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M"),
            "landing_page": self.landing_page,
            "name": self.name,
            "phone": self.phone,
            "region": self.region,
            "vehicle_type": self.vehicle_type,
            "message": self.message,
            "status": self.status,
            "utm_source": self.utm_source,
            "utm_medium": self.utm_medium,
            "utm_campaign": self.utm_campaign,
            "referrer": self.referrer,
            "agreement": self.agreement,
        }
