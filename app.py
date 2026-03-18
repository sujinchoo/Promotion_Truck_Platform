from flask import Flask, flash, redirect, render_template, request, url_for

from config import Config
from models import Lead, db


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


@app.before_request
def create_tables():
    db.create_all()


@app.route("/")
def index():
    vehicle_options = [
        "봉고3 전기차",
        "1톤 카고",
        "1톤 냉동탑차",
        "LPG 화물차",
        "법인/리스 상담",
    ]
    return render_template("index.html", vehicle_options=vehicle_options)


@app.route("/lead", methods=["POST"])
def create_lead():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    region = request.form.get("region", "").strip()
    business_type = request.form.get("business_type", "").strip()
    vehicle_type = request.form.get("vehicle_type", "").strip()

    if not all([name, phone, region, business_type, vehicle_type]):
        flash("필수 항목을 모두 입력해 주세요.", "error")
        return redirect(url_for("index"))

    lead = Lead(
        name=name,
        phone=phone,
        region=region,
        business_type=business_type,
        vehicle_type=vehicle_type,
        budget=request.form.get("budget", "").strip(),
        contact_time=request.form.get("contact_time", "").strip(),
        message=request.form.get("message", "").strip(),
        utm_source=request.form.get("utm_source", "").strip(),
        utm_medium=request.form.get("utm_medium", "").strip(),
        utm_campaign=request.form.get("utm_campaign", "").strip(),
        referrer=request.referrer,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
    )
    db.session.add(lead)
    db.session.commit()

    return redirect(url_for("thank_you"))


@app.route("/thank-you")
def thank_you():
    return render_template("thank_you.html")


@app.route("/admin")
def admin():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    total_leads = len(leads)
    new_leads = sum(1 for lead in leads if lead.status == "new")
    return render_template(
        "admin.html",
        leads=leads,
        total_leads=total_leads,
        new_leads=new_leads,
    )


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
