# blueprints/admin.py - one generic CRUD for ALL tables (list, add, edit, delete)
# Instead of writing 44 x 4 routes by hand, the form is made from the columns of the model.
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, current_app, g
from sqlalchemy import Boolean, Integer, Float, Numeric, Text, Date, DateTime
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from extensions import db

admin_bp = Blueprint("admin", __name__)


@admin_bp.before_request
def only_admin():
    if g.user is None:
        flash("Please login first.", "warning")
        return redirect(url_for("auth.login", next=request.path))
    if g.user.role.name != "admin":
        flash("Only admin can open this area.", "danger")
        return redirect(url_for("main.index"))


def all_models():
    # dictionary like {"users": User, "jobs": Job, ...}
    return {m.class_.__tablename__: m.class_ for m in db.Model.registry.mappers}


def get_model_or_404(table):
    model = all_models().get(table)
    if model is None:
        abort(404)
    return model


def label_for(obj):
    """short readable name of a row, used in dropdowns and tables"""
    for attr in ("name", "title", "full_name", "email", "label", "subject", "degree"):
        value = getattr(obj, attr, None)
        if value:
            return str(value)
    return f"#{obj.id}"


def fk_model(col):
    fk = list(col.foreign_keys)[0]
    return all_models()[fk.column.table.name]


def is_auto_column(col):
    # created_at, applied_at ... are filled automatically
    return col.name.endswith("_at") and col.default is not None


def build_fields(model, obj=None, submitted=None):
    """make a list of form fields from the columns of the model"""
    fields = []
    for col in model.__table__.columns:
        if col.primary_key or is_auto_column(col):
            continue
        required = (not col.nullable) and col.default is None and col.server_default is None
        field = {"name": col.name, "label": col.name.replace("_id", "").replace("_", " ").title(),
                 "required": required, "options": [], "col": col}

        if col.foreign_keys:
            field["kind"] = "select"
            field["options"] = [(o.id, label_for(o)) for o in fk_model(col).query.order_by(fk_model(col).id).limit(500)]
        elif isinstance(col.type, Boolean):
            field["kind"] = "checkbox"
        elif col.name == "password_hash":
            field["kind"] = "password"
            field["label"] = "Password"
            field["required"] = obj is None
        elif isinstance(col.type, Text):
            field["kind"] = "textarea"
        elif isinstance(col.type, DateTime):
            field["kind"] = "datetime-local"
        elif isinstance(col.type, Date):
            field["kind"] = "date"
        elif isinstance(col.type, (Integer, Float, Numeric)):
            field["kind"] = "number"
        else:
            field["kind"] = "text"

        # value shown inside the form
        if submitted is not None:
            value = submitted.get(col.name, "")
            if field["kind"] == "checkbox":
                value = col.name in submitted
        elif obj is not None:
            value = getattr(obj, col.name)
            if value is None:
                value = ""
            elif isinstance(value, datetime):
                value = value.strftime("%Y-%m-%dT%H:%M")
            elif hasattr(value, "isoformat") and field["kind"] == "date":
                value = value.isoformat()
        else:
            value = True if (field["kind"] == "checkbox" and col.default is not None and col.default.arg) else ""
        field["value"] = "" if field["kind"] == "password" else value
        fields.append(field)
    return fields


def read_form(fields, form, obj=None):
    """server side validation. returns (values, errors)"""
    values, errors = {}, []
    for f in fields:
        col, name, label, kind = f["col"], f["name"], f["label"], f["kind"]
        if kind == "checkbox":
            values[name] = name in form
            continue
        raw = form.get(name, "").strip()
        if raw == "":
            if kind == "password" and obj is not None:
                continue  # keep the old password
            if f["required"]:
                errors.append(f"{label} is required.")
            elif col.nullable:
                values[name] = None
            continue  # not nullable with default: leave it, default is used
        try:
            if kind == "select":
                value = int(raw)
                if db.session.get(fk_model(col), value) is None:
                    errors.append(f"{label}: selected record does not exist.")
                    continue
            elif kind == "number":
                value = float(raw) if isinstance(col.type, (Float, Numeric)) else int(raw)
            elif kind == "date":
                value = datetime.strptime(raw, "%Y-%m-%d").date()
            elif kind == "datetime-local":
                value = datetime.strptime(raw, "%Y-%m-%dT%H:%M")
            elif kind == "password":
                if len(raw) < 6:
                    errors.append("Password must be at least 6 characters.")
                    continue
                name, value = "password_hash", generate_password_hash(raw)
            else:
                value = raw
                max_len = getattr(col.type, "length", None)
                if max_len and len(raw) > max_len:
                    errors.append(f"{label} can have at most {max_len} characters.")
                    continue
        except ValueError:
            errors.append(f"{label} has a wrong value.")
            continue
        values[name] = value
    return values, errors


@admin_bp.route("/")
def index():
    tables = [(name, model.query.count()) for name, model in sorted(all_models().items())]
    return render_template("admin/index.html", tables=tables)


@admin_bp.route("/<table>/")
def list_rows(table):
    model = get_model_or_404(table)
    page = request.args.get("page", 1, type=int)
    pagination = model.query.order_by(model.id.desc()).paginate(
        page=page, per_page=current_app.config["ADMIN_PER_PAGE"], error_out=False)

    columns = [c for c in model.__table__.columns if c.name != "password_hash"
               and not isinstance(c.type, Text)][:7]
    rows = []
    for obj in pagination.items:
        cells = []
        for col in columns:
            value = getattr(obj, col.name)
            if value is None:
                text = "-"
            elif col.foreign_keys:
                related = db.session.get(fk_model(col), value)
                text = label_for(related) if related else str(value)
            elif isinstance(value, bool):
                text = "Yes" if value else "No"
            else:
                text = str(value)[:40]
            cells.append(text)
        rows.append((obj.id, cells))
    return render_template("admin/list.html", table=table, columns=columns, rows=rows, pagination=pagination)


@admin_bp.route("/<table>/add", methods=["GET", "POST"])
def add_row(table):
    model = get_model_or_404(table)
    if request.method == "POST":
        fields = build_fields(model, submitted=request.form)
        values, errors = read_form(fields, request.form)
        if not errors:
            try:
                db.session.add(model(**values))
                db.session.commit()
                flash("Record added.", "success")
                return redirect(url_for("admin.list_rows", table=table))
            except IntegrityError:
                db.session.rollback()
                errors.append("Could not save. A unique value already exists or a linked record is missing.")
        for e in errors:
            flash(e, "danger")
        return render_template("admin/form.html", table=table, fields=fields, editing=False)
    return render_template("admin/form.html", table=table, fields=build_fields(model), editing=False)


@admin_bp.route("/<table>/<int:row_id>/edit", methods=["GET", "POST"])
def edit_row(table, row_id):
    model = get_model_or_404(table)
    obj = db.get_or_404(model, row_id)
    if request.method == "POST":
        fields = build_fields(model, obj=obj, submitted=request.form)
        values, errors = read_form(fields, request.form, obj=obj)
        if not errors:
            try:
                for key, value in values.items():
                    setattr(obj, key, value)
                db.session.commit()
                flash("Record updated.", "success")
                return redirect(url_for("admin.list_rows", table=table))
            except IntegrityError:
                db.session.rollback()
                errors.append("Could not save. A unique value already exists or a linked record is missing.")
        for e in errors:
            flash(e, "danger")
        return render_template("admin/form.html", table=table, fields=fields, editing=True, row_id=row_id)
    return render_template("admin/form.html", table=table, fields=build_fields(model, obj=obj),
                           editing=True, row_id=row_id)


@admin_bp.route("/<table>/<int:row_id>/delete", methods=["POST"])
def delete_row(table, row_id):
    model = get_model_or_404(table)
    obj = db.get_or_404(model, row_id)
    if table == "users" and obj.id == g.user.id:
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for("admin.list_rows", table=table))
    try:
        db.session.delete(obj)
        db.session.commit()
        flash("Record deleted.", "info")
    except IntegrityError:
        db.session.rollback()
        flash("Cannot delete this record because other tables are using it.", "danger")
    return redirect(url_for("admin.list_rows", table=table))
