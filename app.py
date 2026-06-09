import os
import sqlite3

from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename


app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def get_db_connection():
    connection = sqlite3.connect("registry.db")
    connection.row_factory = sqlite3.Row
    return connection


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    if file and file.filename != "" and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(file_path)
        return filename

    return None


def get_stars(rating):
    if rating is None:
        return "Немає оцінки"

    try:
        rating = int(rating)
    except ValueError:
        return "Немає оцінки"

    return "⭐" * rating


@app.route("/")
def index():
    system_name = request.args.get("system_name", "")
    target_device = request.args.get("target_device", "")
    status = request.args.get("status", "")

    query = """
        SELECT *
        FROM deployment_records
        WHERE system_name LIKE ?
        AND target_device LIKE ?
        AND status LIKE ?
        ORDER BY id DESC
    """

    parameters = (
        f"%{system_name}%",
        f"%{target_device}%",
        f"%{status}%"
    )

    connection = get_db_connection()
    records = connection.execute(query, parameters).fetchall()
    connection.close()

    return render_template(
        "index.html",
        records=records,
        system_name=system_name,
        target_device=target_device,
        status=status,
        get_stars=get_stars
    )


@app.route("/view/<int:record_id>")
def view_record(record_id):
    connection = get_db_connection()

    record = connection.execute("""
        SELECT *
        FROM deployment_records
        WHERE id = ?
    """, (record_id,)).fetchone()

    connection.close()

    return render_template(
        "view_record.html",
        record=record,
        get_stars=get_stars
    )


@app.route("/add", methods=["GET", "POST"])
def add_record():
    if request.method == "POST":
        system_name = request.form["system_name"]
        version = request.form["version"]
        target_device = request.form["target_device"]
        installation_method = request.form["installation_method"]
        demo_example = request.form["demo_example"]
        dependencies = request.form["dependencies"]
        launch_result = request.form["launch_result"]
        problems = request.form["problems"]
        educational_value = request.form["educational_value"]
        status = request.form["status"]

        logo_image = save_image(request.files.get("logo_image"))
        installation_image = save_image(request.files.get("installation_image"))
        launch_image = save_image(request.files.get("launch_image"))
        demo_image = save_image(request.files.get("demo_image"))

        connection = get_db_connection()

        connection.execute("""
            INSERT INTO deployment_records (
                system_name,
                version,
                target_device,
                installation_method,
                demo_example,
                dependencies,
                launch_result,
                problems,
                educational_value,
                status,
                logo_image,
                installation_image,
                launch_image,
                demo_image
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            system_name,
            version,
            target_device,
            installation_method,
            demo_example,
            dependencies,
            launch_result,
            problems,
            educational_value,
            status,
            logo_image,
            installation_image,
            launch_image,
            demo_image
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("index"))

    return render_template("add_record.html")


@app.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit_record(record_id):
    connection = get_db_connection()

    record = connection.execute("""
        SELECT *
        FROM deployment_records
        WHERE id = ?
    """, (record_id,)).fetchone()

    if request.method == "POST":
        system_name = request.form["system_name"]
        version = request.form["version"]
        target_device = request.form["target_device"]
        installation_method = request.form["installation_method"]
        demo_example = request.form["demo_example"]
        dependencies = request.form["dependencies"]
        launch_result = request.form["launch_result"]
        problems = request.form["problems"]
        educational_value = request.form["educational_value"]
        status = request.form["status"]

        logo_image = save_image(request.files.get("logo_image")) or record["logo_image"]
        installation_image = save_image(request.files.get("installation_image")) or record["installation_image"]
        launch_image = save_image(request.files.get("launch_image")) or record["launch_image"]
        demo_image = save_image(request.files.get("demo_image")) or record["demo_image"]

        connection.execute("""
            UPDATE deployment_records
            SET system_name = ?,
                version = ?,
                target_device = ?,
                installation_method = ?,
                demo_example = ?,
                dependencies = ?,
                launch_result = ?,
                problems = ?,
                educational_value = ?,
                status = ?,
                logo_image = ?,
                installation_image = ?,
                launch_image = ?,
                demo_image = ?
            WHERE id = ?
        """, (
            system_name,
            version,
            target_device,
            installation_method,
            demo_example,
            dependencies,
            launch_result,
            problems,
            educational_value,
            status,
            logo_image,
            installation_image,
            launch_image,
            demo_image,
            record_id
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("index"))

    connection.close()

    return render_template(
        "edit_record.html",
        record=record
    )


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    connection = get_db_connection()

    connection.execute("""
        DELETE FROM deployment_records
        WHERE id = ?
    """, (record_id,))

    connection.commit()
    connection.close()

    return redirect(url_for("index"))


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)