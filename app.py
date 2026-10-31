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

@app.route("/robots.txt")
def robots_txt():
    lines = [
        "User-agent: *",
        "Allow: /"
    ]
    return "\n".join(lines), 200, {"Content-Type": "text/plain"}


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
        ).first() # আপনার আগের কোড এখানে কিছুটা কাটা ছিল, তাই ফিক্স করে দেওয়া হলো

        if user and check_password_hash(user.password_hash, password):
            session["admin_logged_in"] = True
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password")

    return render_template("login.html")
