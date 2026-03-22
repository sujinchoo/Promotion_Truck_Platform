from functools import wraps

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import load_only

from config import Config
from models import Lead, db
from telegram_service import TelegramNotifier


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
telegram_notifier = TelegramNotifier(
    app.config.get("TELEGRAM_BOT_TOKEN"),
    app.config.get("TELEGRAM_CHAT_ID"),
    app.config.get("TELEGRAM_NOTIFICATIONS_ENABLED", True),
)


STATUS_OPTIONS = ["신규", "통화중", "진행중", "연결안됨", "거절", "계약완료"]
STATUS_CLASS_MAP = {
    "신규": "status-new",
    "통화중": "status-calling",
    "진행중": "status-progress",
    "연결안됨": "status-unreachable",
    "거절": "status-rejected",
    "계약완료": "status-contracted",
}
LEAD_COLUMNS = {
    "created_at": "TIMESTAMP",
    "landing_page": "VARCHAR(50) DEFAULT 'main' NOT NULL",
    "name": "VARCHAR(100)",
    "phone": "VARCHAR(30)",
    "region": "VARCHAR(100)",
    "business_type": "VARCHAR(100)",
    "vehicle_type": "VARCHAR(100)",
    "contact_time": "VARCHAR(100)",
    "message": "TEXT",
    "status": "VARCHAR(50) DEFAULT '신규' NOT NULL",
    "utm_source": "VARCHAR(100)",
    "utm_medium": "VARCHAR(100)",
    "utm_campaign": "VARCHAR(100)",
    "referrer": "VARCHAR(255)",
    "ip_address": "VARCHAR(64)",
    "agreement": "BOOLEAN DEFAULT FALSE NOT NULL",
}
REQUIRED_FIELDS = ["name", "phone", "region", "business_type", "vehicle_type"]
MOBILE_VEHICLE_OPTIONS = [
    "1톤 내장탑",
    "1톤 냉동탑차",
    "2.5톤 / 3.5톤 화물차",
    "영업용 번호판 상담",
    "법인·개인사업자 운용리스",
]


def drop_budget_column_if_present():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            if "leads" not in inspector.get_table_names():
                return

            existing_columns = {column["name"] for column in inspector.get_columns("leads")}
            if "budget" not in existing_columns:
                return

            db.session.execute(text("ALTER TABLE leads DROP COLUMN budget"))
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.warning("Budget column drop skipped because the database connection is unavailable.")


def ensure_database_schema():
    with app.app_context():
        try:
            db.create_all()
            inspector = inspect(db.engine)
            if "leads" not in inspector.get_table_names():
                db.create_all()
                return

            existing_columns = {column["name"] for column in inspector.get_columns("leads")}
            for column_name, column_definition in LEAD_COLUMNS.items():
                if column_name not in existing_columns:
                    db.session.execute(text(f"ALTER TABLE leads ADD COLUMN {column_name} {column_definition}"))

            db.session.execute(text("UPDATE leads SET status = '신규' WHERE status IS NULL OR status = '' OR status = 'new'"))
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            app.logger.warning("Database schema initialization skipped because the database connection is unavailable.")


ensure_database_schema()
drop_budget_column_if_present()


@app.context_processor
def inject_shared_context():
    return {
        "vehicle_options": MOBILE_VEHICLE_OPTIONS,
        "hero_image_path": app.config["HERO_IMAGE_PATH"],
        "status_options": STATUS_OPTIONS,
        "status_class_map": STATUS_CLASS_MAP,
    }


def admin_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_authenticated"):
            return redirect(url_for("admin_login", next=request.path))
        return view_func(*args, **kwargs)

    return wrapped_view


def render_page(template_name, **context):
    show_header = context.pop("show_header", True)
    return render_template(template_name, show_header=show_header, **context)


def resolve_destination(landing_page):
    return "mobile_landing" if landing_page == "mobile_ad" else "index"


@app.route("/")
def index():
    return render_page("index.html")


@app.route("/mobile")
def mobile_landing():
    return render_page("mobile.html", show_header=False)


@app.route("/privacy")
def privacy_policy():
    return render_page("privacy.html")


@app.route("/privacy-consent")
def privacy_consent():
    return render_page("privacy_consent.html")


@app.route("/lead", methods=["POST"])
def create_lead():
    landing_page = request.form.get("landing_page", "main").strip() or "main"
    destination = resolve_destination(landing_page)
    form_data = {field: request.form.get(field, "").strip() for field in REQUIRED_FIELDS}

    if not request.form.get("privacy_agree"):
        flash("개인정보 수집·이용 및 통합 상담 안내에 동의해 주세요.", "error")
        return redirect(url_for(destination) + "#consult")

    if not all(form_data.values()):
        flash("필수 항목을 모두 입력해 주세요.", "error")
        return redirect(url_for(destination) + "#consult")

    lead = Lead(
        landing_page=landing_page,
        name=form_data["name"],
        phone=form_data["phone"],
        region=form_data["region"],
        business_type=form_data["business_type"],
        vehicle_type=form_data["vehicle_type"],
        contact_time=request.form.get("contact_time", "").strip(),
        message=request.form.get("message", "").strip(),
        status="신규",
        utm_source=request.form.get("utm_source", "").strip(),
        utm_medium=request.form.get("utm_medium", "").strip(),
        utm_campaign=request.form.get("utm_campaign", "").strip(),
        referrer=request.referrer,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        agreement=request.form.get("privacy_agree") == "yes",
    )
    db.session.add(lead)
    db.session.commit()
    telegram_notifier.send_new_lead_notification(lead)

    return redirect(url_for("thank_you"))


@app.route("/thank-you")
def thank_you():
    return render_page("thank_you.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if not app.config["ADMIN_USERNAME"] or not app.config["ADMIN_PASSWORD"]:
        abort(503, description="관리자 환경 변수가 설정되지 않았습니다.")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == app.config["ADMIN_USERNAME"] and password == app.config["ADMIN_PASSWORD"]:
            session["admin_authenticated"] = True
            flash("관리자 인증이 완료되었습니다.", "success")
            return redirect(request.args.get("next") or url_for("admin"))

        flash("아이디 또는 비밀번호가 올바르지 않습니다.", "error")

    return render_page("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_authenticated", None)
    flash("관리자 세션이 종료되었습니다.", "success")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin():
    leads = (
        Lead.query.options(
            load_only(
                Lead.id,
                Lead.created_at,
                Lead.landing_page,
                Lead.name,
                Lead.phone,
                Lead.region,
                Lead.business_type,
                Lead.vehicle_type,
                Lead.contact_time,
                Lead.utm_source,
                Lead.utm_campaign,
                Lead.agreement,
                Lead.message,
                Lead.status,
            )
        )
        .order_by(Lead.created_at.desc())
        .all()
    )
    total_leads = len(leads)
    new_leads = sum(1 for lead in leads if lead.status == "신규")
    mobile_leads = sum(1 for lead in leads if lead.landing_page == "mobile_ad")
    return render_page(
        "admin.html",
        leads=leads,
        total_leads=total_leads,
        new_leads=new_leads,
        mobile_leads=mobile_leads,
    )


@app.route("/admin/leads/status", methods=["POST"])
@admin_required
def update_lead_statuses():
    payload = request.get_json(silent=True) or {}
    updates = payload.get("updates", [])
    if not updates:
        return jsonify({"message": "변경된 상태가 없습니다."}), 400

    updated_ids = []
    try:
        for item in updates:
            lead_id = item.get("id")
            status = item.get("status")
            if status not in STATUS_OPTIONS:
                return jsonify({"message": f"허용되지 않는 상태값입니다: {status}"}), 400

            lead = db.session.get(Lead, lead_id)
            if not lead:
                continue
            lead.status = status
            updated_ids.append(lead_id)

        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "상태 저장 중 오류가 발생했습니다."}), 500

    return jsonify({"message": "업데이트 완료", "updated_ids": updated_ids})


@app.route("/admin/leads/<int:lead_id>", methods=["DELETE"])
@admin_required
def delete_lead(lead_id):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        return jsonify({"message": "삭제할 리드를 찾을 수 없습니다."}), 404

    try:
        db.session.delete(lead)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"message": "리드 삭제 중 오류가 발생했습니다."}), 500

    return jsonify({"message": "리드가 삭제되었습니다.", "deleted_id": lead_id})


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
