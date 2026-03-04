from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.expense import Expense
from app.models.farm import Farm
from datetime import datetime

expenses_bp = Blueprint("expenses", __name__)

# Coffee farming expense categories
EXPENSE_CATEGORIES = [
    "Fertilizer",
    "Pesticides / Fungicides",
    "Labour / Wages",
    "Irrigation",
    "Harvesting",
    "Processing",
    "Transportation",
    "Equipment / Tools",
    "Land Lease / Rent",
    "Seeds / Seedlings",
    "Electricity",
    "Miscellaneous",
]


@expenses_bp.route("/")
@login_required
def index():
    # Get all farms for the current user
    farms = Farm.query.filter_by(user_id=current_user.id).all()
    farm_ids = [f.id for f in farms]

    # Filters
    farm_filter     = request.args.get("farm_id", "")
    category_filter = request.args.get("category", "")
    month_filter    = request.args.get("month", "")

    query = Expense.query.filter(Expense.farm_id.in_(farm_ids))

    if farm_filter:
        query = query.filter_by(farm_id=int(farm_filter))
    if category_filter:
        query = query.filter_by(category=category_filter)
    if month_filter:
        try:
            year, month = month_filter.split("-")
            query = query.filter(
                db.extract("year",  Expense.date) == int(year),
                db.extract("month", Expense.date) == int(month)
            )
        except ValueError:
            pass

    expenses = query.order_by(Expense.date.desc()).all()
    total    = sum(e.amount for e in expenses)

    return render_template("expenses/index.html",
        expenses=expenses,
        farms=farms,
        categories=EXPENSE_CATEGORIES,
        total=total,
        farm_filter=farm_filter,
        category_filter=category_filter,
        month_filter=month_filter,
    )


@expenses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    farms = Farm.query.filter_by(user_id=current_user.id).all()

    if not farms:
        flash("Please add a farm first before adding expenses.", "warning")
        return redirect(url_for("farms.add"))

    if request.method == "POST":
        title    = request.form.get("title", "").strip()
        amount   = request.form.get("amount", "").strip()
        category = request.form.get("category", "").strip()
        farm_id  = request.form.get("farm_id", "").strip()
        date_str = request.form.get("date", "").strip()
        notes    = request.form.get("notes", "").strip()

        # Validation
        if not title or not amount or not category or not farm_id or not date_str:
            flash("All required fields must be filled.", "danger")
            return render_template("expenses/add.html",
                                   farms=farms, categories=EXPENSE_CATEGORIES)
        try:
            amount = float(amount)
        except ValueError:
            flash("Amount must be a valid number.", "danger")
            return render_template("expenses/add.html",
                                   farms=farms, categories=EXPENSE_CATEGORIES)

        # Verify farm belongs to current user
        farm = Farm.query.filter_by(id=int(farm_id), user_id=current_user.id).first()
        if not farm:
            flash("Invalid farm selected.", "danger")
            return render_template("expenses/add.html",
                                   farms=farms, categories=EXPENSE_CATEGORIES)

        expense = Expense(
            title    = title,
            amount   = amount,
            category = category,
            farm_id  = int(farm_id),
            date     = datetime.strptime(date_str, "%Y-%m-%d").date(),
            notes    = notes,
        )
        db.session.add(expense)
        db.session.commit()
        flash(f"Expense '{title}' of ₹{amount:.2f} added!", "success")
        return redirect(url_for("expenses.index"))

    return render_template("expenses/add.html",
                           farms=farms, categories=EXPENSE_CATEGORIES)


@expenses_bp.route("/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit(expense_id):
    farms   = Farm.query.filter_by(user_id=current_user.id).all()
    farm_ids = [f.id for f in farms]
    expense = Expense.query.filter(
        Expense.id == expense_id,
        Expense.farm_id.in_(farm_ids)
    ).first_or_404()

    if request.method == "POST":
        expense.title    = request.form.get("title", "").strip()
        expense.category = request.form.get("category", "").strip()
        expense.notes    = request.form.get("notes", "").strip()
        amount           = request.form.get("amount", "").strip()
        date_str         = request.form.get("date", "").strip()
        farm_id          = request.form.get("farm_id", "").strip()

        if not expense.title or not amount or not date_str:
            flash("All required fields must be filled.", "danger")
            return render_template("expenses/edit.html",
                                   expense=expense, farms=farms,
                                   categories=EXPENSE_CATEGORIES)
        try:
            expense.amount  = float(amount)
            expense.date    = datetime.strptime(date_str, "%Y-%m-%d").date()
            expense.farm_id = int(farm_id)
        except ValueError:
            flash("Invalid amount or date.", "danger")
            return render_template("expenses/edit.html",
                                   expense=expense, farms=farms,
                                   categories=EXPENSE_CATEGORIES)

        db.session.commit()
        flash("Expense updated successfully!", "success")
        return redirect(url_for("expenses.index"))

    return render_template("expenses/edit.html",
                           expense=expense, farms=farms,
                           categories=EXPENSE_CATEGORIES)


@expenses_bp.route("/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete(expense_id):
    farms    = Farm.query.filter_by(user_id=current_user.id).all()
    farm_ids = [f.id for f in farms]
    expense  = Expense.query.filter(
        Expense.id == expense_id,
        Expense.farm_id.in_(farm_ids)
    ).first_or_404()

    db.session.delete(expense)
    db.session.commit()
    flash(f"Expense '{expense.title}' deleted.", "warning")
    return redirect(url_for("expenses.index"))