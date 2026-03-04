from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.income import Income
from app.models.farm import Farm
from datetime import datetime

income_bp = Blueprint("income", __name__)

INCOME_SOURCES = [
    "Coffee Bean Sale",
    "Green Coffee Export",
    "Roasted Coffee Sale",
    "Government Subsidy",
    "Crop Insurance Claim",
    "By-product Sale",
    "Other",
]


@income_bp.route("/")
@login_required
def index():
    farms    = Farm.query.filter_by(user_id=current_user.id).all()
    farm_ids = [f.id for f in farms]

    farm_filter  = request.args.get("farm_id", "")
    month_filter = request.args.get("month", "")

    query = Income.query.filter(Income.farm_id.in_(farm_ids))

    if farm_filter:
        query = query.filter_by(farm_id=int(farm_filter))
    if month_filter:
        try:
            year, month = month_filter.split("-")
            query = query.filter(
                db.extract("year",  Income.date) == int(year),
                db.extract("month", Income.date) == int(month)
            )
        except ValueError:
            pass

    incomes = query.order_by(Income.date.desc()).all()
    total   = sum(i.amount for i in incomes)

    return render_template("income/index.html",
        incomes=incomes,
        farms=farms,
        sources=INCOME_SOURCES,
        total=total,
        farm_filter=farm_filter,
        month_filter=month_filter,
    )


@income_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    farms = Farm.query.filter_by(user_id=current_user.id).all()

    if not farms:
        flash("Please add a farm first.", "warning")
        return redirect(url_for("farms.add"))

    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        amount   = request.form.get("amount", "").strip()
        source   = request.form.get("source", "").strip()
        farm_id  = request.form.get("farm_id", "").strip()
        date_str = request.form.get("date", "").strip()
        notes    = request.form.get("notes", "").strip()

        if not title or not amount or not farm_id or not date_str:
            flash("All required fields must be filled.", "danger")
            return render_template("income/add.html",
                                   farms=farms, sources=INCOME_SOURCES)
        try:
            amount = float(amount)
        except ValueError:
            flash("Amount must be a valid number.", "danger")
            return render_template("income/add.html",
                                   farms=farms, sources=INCOME_SOURCES)

        farm = Farm.query.filter_by(id=int(farm_id), user_id=current_user.id).first()
        if not farm:
            flash("Invalid farm selected.", "danger")
            return render_template("income/add.html",
                                   farms=farms, sources=INCOME_SOURCES)

        income = Income(
            title   = title,
            amount  = amount,
            source  = source,
            farm_id = int(farm_id),
            date    = datetime.strptime(date_str, "%Y-%m-%d").date(),
            notes   = notes,
        )
        db.session.add(income)
        db.session.commit()
        flash(f"Income '{title}' of ₹{amount:.2f} added!", "success")
        return redirect(url_for("income.index"))

    return render_template("income/add.html",
                           farms=farms,
                           sources=INCOME_SOURCES,
                           today=datetime.today().strftime("%Y-%m-%d"))


@income_bp.route("/edit/<int:income_id>", methods=["GET", "POST"])
@login_required
def edit(income_id):
    farms    = Farm.query.filter_by(user_id=current_user.id).all()
    farm_ids = [f.id for f in farms]
    income   = Income.query.filter(
        Income.id == income_id,
        Income.farm_id.in_(farm_ids)
    ).first_or_404()

    if request.method == "POST":
        income.title  = request.form.get("title", "").strip()
        income.source = request.form.get("source", "").strip()
        income.notes  = request.form.get("notes", "").strip()
        amount        = request.form.get("amount", "").strip()
        date_str      = request.form.get("date", "").strip()
        farm_id       = request.form.get("farm_id", "").strip()

        try:
            income.amount  = float(amount)
            income.date    = datetime.strptime(date_str, "%Y-%m-%d").date()
            income.farm_id = int(farm_id)
        except ValueError:
            flash("Invalid amount or date.", "danger")
            return render_template("income/edit.html",
                                   income=income, farms=farms,
                                   sources=INCOME_SOURCES)

        db.session.commit()
        flash("Income updated successfully!", "success")
        return redirect(url_for("income.index"))

    return render_template("income/edit.html",
                           income=income, farms=farms,
                           sources=INCOME_SOURCES)


@income_bp.route("/delete/<int:income_id>", methods=["POST"])
@login_required
def delete(income_id):
    farms    = Farm.query.filter_by(user_id=current_user.id).all()
    farm_ids = [f.id for f in farms]
    income   = Income.query.filter(
        Income.id == income_id,
        Income.farm_id.in_(farm_ids)
    ).first_or_404()

    db.session.delete(income)
    db.session.commit()
    flash(f"Income '{income.title}' deleted.", "warning")
    return redirect(url_for("income.index"))