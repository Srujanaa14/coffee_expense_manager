from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.farm import Farm
from app.models.expense import Expense
from app.models.income import Income
from app.extensions import db
from datetime import datetime, date
import json

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    farms    = Farm.query.filter_by(user_id=current_user.id).all()
    farm_ids = [f.id for f in farms]

    # ── Totals ──────────────────────────────────────────────
    total_expenses = db.session.query(
        db.func.coalesce(db.func.sum(Expense.amount), 0)
    ).filter(Expense.farm_id.in_(farm_ids)).scalar()

    total_income = db.session.query(
        db.func.coalesce(db.func.sum(Income.amount), 0)
    ).filter(Income.farm_id.in_(farm_ids)).scalar()

    net_profit = total_income - total_expenses

    # ── Recent transactions (last 5) ────────────────────────
    recent_expenses = Expense.query.filter(
        Expense.farm_id.in_(farm_ids)
    ).order_by(Expense.date.desc()).limit(5).all()

    recent_income = Income.query.filter(
        Income.farm_id.in_(farm_ids)
    ).order_by(Income.date.desc()).limit(5).all()

    # ── Monthly chart data (last 6 months) ──────────────────
    current_year  = datetime.now().year
    current_month = datetime.now().month

    months_labels   = []
    monthly_expense = []
    monthly_income  = []

    for i in range(5, -1, -1):
        month = current_month - i
        year  = current_year
        if month <= 0:
            month += 12
            year  -= 1

        label = datetime(year, month, 1).strftime("%b %Y")
        months_labels.append(label)

        exp = db.session.query(
            db.func.coalesce(db.func.sum(Expense.amount), 0)
        ).filter(
            Expense.farm_id.in_(farm_ids),
            db.extract("year",  Expense.date) == year,
            db.extract("month", Expense.date) == month,
        ).scalar()

        inc = db.session.query(
            db.func.coalesce(db.func.sum(Income.amount), 0)
        ).filter(
            Income.farm_id.in_(farm_ids),
            db.extract("year",  Income.date) == year,
            db.extract("month", Income.date) == month,
        ).scalar()

        monthly_expense.append(float(exp))
        monthly_income.append(float(inc))

    # ── Expense breakdown by category ───────────────────────
    cat_data = db.session.query(
        Expense.category,
        db.func.sum(Expense.amount)
    ).filter(
        Expense.farm_id.in_(farm_ids)
    ).group_by(Expense.category).all()

    cat_labels = [row[0] for row in cat_data]
    cat_values = [float(row[1]) for row in cat_data]

    return render_template("dashboard/index.html",
        farms          = farms,
        total_expenses = total_expenses,
        total_income   = total_income,
        net_profit     = net_profit,
        recent_expenses= recent_expenses,
        recent_income  = recent_income,
        months_labels  = json.dumps(months_labels),
        monthly_expense= json.dumps(monthly_expense),
        monthly_income = json.dumps(monthly_income),
        cat_labels     = json.dumps(cat_labels),
        cat_values     = json.dumps(cat_values),
    )