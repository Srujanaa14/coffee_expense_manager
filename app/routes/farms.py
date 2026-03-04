from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.models.farm import Farm

farms_bp = Blueprint("farms", __name__)


@farms_bp.route("/")
@login_required
def index():
    farms = Farm.query.filter_by(user_id=current_user.id).order_by(Farm.created_at.desc()).all()
    return render_template("farms/index.html", farms=farms)


@farms_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name       = request.form.get("name", "").strip()
        location   = request.form.get("location", "").strip()
        area_acres = request.form.get("area_acres", "").strip()

        if not name or not area_acres:
            flash("Farm name and area are required.", "danger")
            return render_template("farms/add.html")

        try:
            area_acres = float(area_acres)
        except ValueError:
            flash("Area must be a valid number.", "danger")
            return render_template("farms/add.html")

        farm = Farm(
            name       = name,
            location   = location,
            area_acres = area_acres,
            user_id    = current_user.id
        )
        db.session.add(farm)
        db.session.commit()
        flash(f"Farm '{name}' added successfully!", "success")
        return redirect(url_for("farms.index"))

    return render_template("farms/add.html")


@farms_bp.route("/edit/<int:farm_id>", methods=["GET", "POST"])
@login_required
def edit(farm_id):
    farm = Farm.query.filter_by(id=farm_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        farm.name       = request.form.get("name", "").strip()
        farm.location   = request.form.get("location", "").strip()
        area_acres      = request.form.get("area_acres", "").strip()

        if not farm.name or not area_acres:
            flash("Farm name and area are required.", "danger")
            return render_template("farms/edit.html", farm=farm)

        try:
            farm.area_acres = float(area_acres)
        except ValueError:
            flash("Area must be a valid number.", "danger")
            return render_template("farms/edit.html", farm=farm)

        db.session.commit()
        flash("Farm updated successfully!", "success")
        return redirect(url_for("farms.index"))

    return render_template("farms/edit.html", farm=farm)


@farms_bp.route("/delete/<int:farm_id>", methods=["POST"])
@login_required
def delete(farm_id):
    farm = Farm.query.filter_by(id=farm_id, user_id=current_user.id).first_or_404()
    db.session.delete(farm)
    db.session.commit()
    flash(f"Farm '{farm.name}' deleted.", "warning")
    return redirect(url_for("farms.index"))