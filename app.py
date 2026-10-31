from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(basedir, "site.db")
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-before-deploying"
)

db = SQLAlchemy(app)


# =========================
# DATABASE MODELS
# =========================

class AdminUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    short_desc = db.Column(db.String(250), nullable=False)
    details = db.Column(db.Text, nullable=False)

    price = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(50), nullable=False)

    icon = db.Column(db.String(50), default="🛠️")
    is_active = db.Column(db.Boolean, default=True)


class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    key = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    value = db.Column(
        db.String(500),
        nullable=False
    )


# =========================
# SETTINGS FUNCTIONS
# =========================

def get_setting(key, default=""):
    item = SiteSetting.query.filter_by(key=key).first()

    if item:
        return item.value

    return default


def set_setting(key, value):
    item = SiteSetting.query.filter_by(key=key).first()

    if item:
        item.value = value
    else:
        db.session.add(
            SiteSetting(
                key=key,
                value=value
            )
        )

    db.session.commit()


# =========================
# DATABASE SETUP
# =========================

def ensure_db():

    with app.app_context():

        db.create_all()

        # Create default admin only if no admin exists
        if not AdminUser.query.first():

            username = os.environ.get(
                "ADMIN_USERNAME",
                "devilspy"
            )

            password = os.environ.get(
                "ADMIN_PASSWORD",
                "098098@890"
            )

            db.session.add(
                AdminUser(
                    username=username,
                    password_hash=generate_password_hash(password)
                )
            )

            db.session.commit()

        # Default website settings
        defaults = {

            "site_name": "ajkerkaj.com",

            "hero_title":
                "Home Cleaning & Repair Services",

            "hero_subtitle":
                "Fast, trusted, and affordable home solutions for your family.",

            "phone":
                "01733415305",

            "cta_text":
                "Book a Service",

            "banner_note":
                "Same-day service available in most areas",

            "footer_text":
                "Trusted home services for busy families."
        }

        for key, value in defaults.items():

            if not SiteSetting.query.filter_by(
                key=key
            ).first():

                db.session.add(
                    SiteSetting(
                        key=key,
                        value=value
                    )
                )

        # Default services
        services = [

            (
                "AC Servicing",
                "ac-servicing",
                "AC cleaning and performance check for better cooling.",
                "AC cleaning, filter replacement, gas check, and performance inspection.",
                "৳ 899",
                "❄️"
            ),

            (
                "AC Filter Cleaning",
                "ac-filter-cleaning",
                "Professional AC filter cleaning service.",
                "Professional AC filter cleaning to remove dust and dirt and improve airflow.",
                "৳ 300",
                "❄️"
            ),

            (
                "Plumber",
                "plumber",
                "Pipe, faucet, sink, and bathroom repair services.",
                "Fix leaks, tap issues, clogged sinks, bathroom drainage, and pipe maintenance.",
                "৳ 799",
                "🚰"
            ),

            (
                "Cleaner",
                "cleaner",
                "Home and office cleaning with trained cleaners.",
                "House cleaning, kitchen cleaning, room sanitization, and deep cleaning.",
                "৳ 699",
                "🧼"
            ),

            (
                "Gardener",
                "gardener",
                "Plant care, lawn maintenance, and gardening help.",
                "Garden cleaning, plant care, lawn trimming, and outdoor maintenance.",
                "৳ 899",
                "🌿"
            ),

            (
                "Electrician",
                "electrician",
                "Safe and expert electrical repairs for your home.",
                "Socket repair, fan fixing, wiring inspection, and light installation.",
                "৳ 849",
                "💡"
            )
        ]

        for title, slug, short, details, price, icon in services:

            if not Service.query.filter_by(
                slug=slug
            ).first():

                db.session.add(
                    Service(
                        title=title,
                        slug=slug,
                        short_desc=short,
                        details=details,
                        price=price,
                        phone="01733415305",
                        icon=icon,
                        is_active=True
                    )
                )

        db.session.commit()


ensure_db()


# =========================
# LOGIN CHECK
# =========================

def logged_in():
    return session.get("admin_logged_in") is True


# =========================
# WEBSITE ROUTES
# =========================

@app.route("/")
def index():

    services = Service.query.filter_by(
        is_active=True
    ).order_by(
        Service.id
    ).all()

    keys = [
        "site_name",
        "hero_title",
        "hero_subtitle",
        "phone",
        "banner_note",
        "footer_text",
        "cta_text"
    ]

    defaults = [
        "ajkerkaj.com",
        "Home Cleaning & Repair Services",
        "Fast, trusted, and affordable home solutions for your family.",
        "01733415305",
        "Same-day service available in most areas",
        "Trusted home services for busy families.",
        "Book a Service"
    ]

    settings = dict(
        zip(
            keys,
            [
                get_setting(k, d)
                for k, d in zip(keys, defaults)
            ]
        )
    )

    return render_template(
        "index.html",
        services=services,
        **settings
    )


@app.route("/service/<slug>")
def service_detail(slug):

    service = Service.query.filter_by(
        slug=slug,
        is_active=True
    ).first_or_404()

    return render_template(
        "service_detail.html",
        service=service,
        site_name=get_setting(
            "site_name",
            "ajkerkaj.com"
        ),
        phone=get_setting(
            "phone",
            "01733415305"
        )
    )


# =========================
# ADMIN LOGIN
# =========================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        user = AdminUser.query.filter_by(
            username=username
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):

            session["admin_logged_in"] = True
            session["admin_user"] = user.username

            return redirect(
                url_for("admin_dashboard")
            )

        flash(
            "Invalid username or password",
            "error"
        )

    return render_template(
        "admin_login.html"
    )


@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin_dashboard():

    if not logged_in():

        return redirect(
            url_for("admin_login")
        )

    keys = [
        "site_name",
        "hero_title",
        "hero_subtitle",
        "phone",
        "banner_note",
        "footer_text",
        "cta_text"
    ]

    vals = [
        get_setting(key)
        for key in keys
    ]

    return render_template(
        "admin_dashboard.html",
        services=Service.query.order_by(
            Service.id
        ).all(),
        **dict(zip(keys, vals))
    )


# =========================
# ADD SERVICE
# =========================

@app.route(
    "/admin/service/add",
    methods=["POST"]
)
def admin_add_service():

    if not logged_in():

        return redirect(
            url_for("admin_login")
        )

    title = request.form.get(
        "title",
        ""
    ).strip()

    slug = request.form.get(
        "slug",
        ""
    ).strip().lower().replace(
        " ",
        "-"
    )

    if not slug:

        slug = title.lower().replace(
            " ",
            "-"
        )

    required = [
        "short_desc",
        "details",
        "price"
    ]

    if (
        not title
        or any(
            not request.form.get(
                x,
                ""
            ).strip()
            for x in required
        )
    ):

        flash(
            "Please fill all required fields.",
            "error"
        )

    elif Service.query.filter_by(
        slug=slug
    ).first():

        flash(
            "Service slug already exists.",
            "error"
        )

    else:

        db.session.add(
            Service(
                title=title,
                slug=slug,

                short_desc=request.form[
                    "short_desc"
                ].strip(),

                details=request.form[
                    "details"
                ].strip(),

                price=request.form[
                    "price"
                ].strip(),

                phone=request.form.get(
                    "phone",
                    ""
                ).strip()
                or get_setting("phone"),

                icon=request.form.get(
                    "icon",
                    "🛠️"
                ).strip()
                or "🛠️",

                is_active=True
            )
        )

        db.session.commit()

        flash(
            "Service added successfully.",
            "success"
        )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================
# EDIT SERVICE
# =========================

@app.route(
    "/admin/service/<int:service_id>/edit",
    methods=["POST"]
)
def admin_edit_service(service_id):

    if not logged_in():

        return redirect(
            url_for("admin_login")
        )

    s = Service.query.get_or_404(
        service_id
    )

    s.title = request.form.get(
        "title",
        s.title
    ).strip()

    s.slug = request.form.get(
        "slug",
        s.slug
    ).strip().lower().replace(
        " ",
        "-"
    ) or s.slug

    s.short_desc = request.form.get(
        "short_desc",
        s.short_desc
    ).strip()

    s.details = request.form.get(
        "details",
        s.details
    ).strip()

    s.price = request.form.get(
        "price",
        s.price
    ).strip()

    s.phone = request.form.get(
        "phone",
        s.phone
    ).strip() or get_setting(
        "phone"
    )

    s.icon = request.form.get(
        "icon",
        s.icon
    ).strip() or s.icon

    s.is_active = (
        request.form.get("is_active") == "on"
    )

    db.session.commit()

    flash(
        "Service updated.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================
# DELETE SERVICE
# =========================

@app.route(
    "/admin/service/<int:service_id>/delete",
    methods=["POST"]
)
def admin_delete_service(service_id):

    if not logged_in():

        return redirect(
            url_for("admin_login")
        )

    s = Service.query.get_or_404(
        service_id
    )

    db.session.delete(s)
    db.session.commit()

    flash(
        "Service deleted.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================
# SAVE SETTINGS
# =========================

@app.route(
    "/admin/settings",
    methods=["POST"]
)
def admin_save_settings():

    if not logged_in():

        return redirect(
            url_for("admin_login")
        )

    setting_keys = [
        "site_name",
        "hero_title",
        "hero_subtitle",
        "phone",
        "banner_note",
        "footer_text",
        "cta_text"
    ]

    for key in setting_keys:

        value = request.form.get(
            key,
            get_setting(key)
        ).strip()

        set_setting(
            key,
            value
        )

    flash(
        "Settings updated.",
        "success"
    )

    return redirect(
        url_for("admin_dashboard")
    )


# =========================
# ROBOTS.TXT FOR GOOGLE
# =========================

@app.route("/robots.txt")
def robots():

    robots_text = """User-agent: *
Allow: /

Sitemap: https://ajkerkaj-com-1.onrender.com/sitemap.xml
"""

    return app.response_class(
        robots_text,
        mimetype="text/plain"
    )


# =========================
# SITEMAP.XML FOR GOOGLE
# =========================

@app.route("/sitemap.xml")
def sitemap():

    base_url = request.url_root.rstrip("/")

    services = Service.query.filter_by(
        is_active=True
    ).all()

    urls = [
        f"{base_url}/"
    ]

    for service in services:

        urls.append(
            f"{base_url}/service/{service.slug}"
        )

    xml = [

        '<?xml version="1.0" encoding="UTF-8"?>',

        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for url in urls:

        xml.append(
            f"<url><loc>{url}</loc></url>"
        )

    xml.append(
        "</urlset>"
    )

    return app.response_class(
        "\n".join(xml),
        mimetype="application/xml"
    )


# =========================
# RUN APP
# =========================

if __name__ == "__main__":

    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                5000
            )
        )
    )