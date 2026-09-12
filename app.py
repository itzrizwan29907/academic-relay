from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
    send_file,
    g,
)
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import psycopg
import os
import mimetypes
import io
from supabase import create_client, Client
import secrets
import hashlib
import smtplib
from email.message import EmailMessage
from urllib.parse import quote

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set in the environment.")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

STORAGE_BUCKET = "academic-relay-files"


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in the environment.")

app.secret_key = SECRET_KEY


# ============================================================
# DATABASE CONNECTION
# ============================================================


def get_db():

    if "db" not in g:

        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError("DATABASE_URL is not set in the environment.")

        g.db = psycopg.connect(
            database_url,
            sslmode="require",
        )

    return g.db


@app.teardown_appcontext
def close_db(exception=None):

    db = g.pop("db", None)

    if db is not None:
        db.close()


# ============================================================
# SUPABASE STORAGE HELPERS
# ============================================================


def upload_to_storage(file, folder):
    """
    Upload a Flask uploaded file to Supabase Storage.

    Returns:
        storage_path, file_size, file_type
    """

    original_filename = file.filename

    filename = secure_filename(original_filename)

    if not filename:
        raise ValueError("Invalid filename.")

    name, ext = os.path.splitext(filename)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"{name}_{timestamp}{ext}"

    storage_path = f"{folder}/{filename}"

    file_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    file_bytes = file.read()

    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    file_size = len(file_bytes)

    supabase.storage.from_(STORAGE_BUCKET).upload(
        storage_path,
        file_bytes,
        {
            "content-type": file_type,
            "upsert": False,
        },
    )

    return storage_path, file_size, file_type


def download_from_storage(storage_path):
    """
    Download a file from Supabase Storage.

    Returns:
        file bytes
    """

    return supabase.storage.from_(STORAGE_BUCKET).download(storage_path)


def delete_from_storage(storage_path):
    """
    Delete a file from Supabase Storage.
    """

    if not storage_path:
        return

    try:

        supabase.storage.from_(STORAGE_BUCKET).remove([storage_path])

    except Exception as e:

        print("Warning: Could not delete Storage file " f"'{storage_path}': {e}")


# ============================================================
# SEND PASSWORD-RESET EMAIL
# ============================================================


def send_password_reset_email(
    recipient_email,
    reset_url,
):
    """
    Send a password-reset email using SMTP.

    Required environment variables:

        SMTP_HOST
        SMTP_PORT
        SMTP_USERNAME
        SMTP_PASSWORD
    """

    smtp_host = os.getenv("SMTP_HOST")

    smtp_port = int(
        os.getenv(
            "SMTP_PORT",
            "465",
        )
    )

    smtp_username = os.getenv("SMTP_USERNAME")

    smtp_password = os.getenv("SMTP_PASSWORD")

    if not all(
        [
            smtp_host,
            smtp_username,
            smtp_password,
        ]
    ):
        raise RuntimeError("SMTP configuration is incomplete.")

    message = EmailMessage()

    message["Subject"] = "Academic Relay - Password Reset"

    message["From"] = smtp_username

    message["To"] = recipient_email

    message.set_content(f"""Hello,

We received a request to reset your Academic Relay password.

Use the link below to create a new password:

{reset_url}

This link will expire in 30 minutes and can only be used once.

If you did not request a password reset, you can safely ignore this email.

Regards,
Academic Relay
""")

    with smtplib.SMTP_SSL(
        smtp_host,
        smtp_port,
    ) as smtp:

        smtp.login(
            smtp_username,
            smtp_password,
        )

        smtp.send_message(message)


# ============================================================
# HOME
# ============================================================


@app.route("/")
def home():

    message = request.args.get("message")

    category = request.args.get("category")

    if message and category:

        flash(
            message,
            category,
        )

    return render_template("index.html")


# ============================================================
# REGISTER
# ============================================================


@app.route(
    "/register",
    methods=["POST"],
)
def register():

    email = request.form["email"].strip().lower()

    password = request.form["password"]

    user_type = request.form.get(
        "user_type",
        "student",
    )

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT *
            FROM users
            WHERE LOWER(email) = %s
            """,
            (email,),
        )

        existing_user = cur.fetchone()

        if existing_user:

            flash(
                "User already exists with this email! " "Please login.",
                "danger",
            )

            return redirect(url_for("home"))

        hashed_password = generate_password_hash(password)

        cur.execute(
            """
            INSERT INTO users
            (
                email,
                password,
                user_type
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                email,
                hashed_password,
                user_type,
            ),
        )

        get_db().commit()

        flash(
            "Registration successful! Please login.",
            "success",
        )

        return redirect(url_for("home"))

    except Exception as e:

        get_db().rollback()

        print(f"Registration error: {e}")

        flash(
            "Unable to complete registration right now.",
            "danger",
        )

        return redirect(url_for("home"))

    finally:

        cur.close()


# ============================================================
# LOGIN
# ============================================================


@app.route(
    "/login",
    methods=["POST"],
)
def login():

    email = request.form["email"].strip().lower()

    password = request.form["password"]

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                email,
                password,
                user_type
            FROM users
            WHERE LOWER(email) = %s
              AND is_active = TRUE
            """,
            (email,),
        )

        result = cur.fetchone()

        if result:

            user_id = result[0]
            db_email = result[1]
            db_password = result[2]
            user_type = result[3]

            if check_password_hash(
                db_password,
                password,
            ):

                session.clear()

                session["user_id"] = user_id
                session["email"] = db_email
                session["user_type"] = user_type

                cur.execute(
                    """
                    UPDATE users
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (user_id,),
                )

                get_db().commit()

                flash(
                    "Login successful! Welcome.",
                    "success",
                )

                if user_type == "faculty":

                    return redirect(url_for("faculty_dashboard"))

                return redirect(url_for("student_dashboard"))

            else:

                flash(
                    "Incorrect password.",
                    "danger",
                )

        else:

            flash(
                "Email not registered.",
                "danger",
            )

    except Exception as e:

        get_db().rollback()

        print(f"Login error: {e}")

        flash(
            "Unable to process login right now.",
            "danger",
        )

    finally:

        cur.close()

    return redirect(url_for("home"))


# ============================================================
# RESET PASSWORD REQUEST
# ============================================================


@app.route(
    "/reset_password",
    methods=["GET", "POST"],
)
def reset_password():

    # --------------------------------------------------------
    # GET:
    # Show forgot-password page.
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template("reset_password.html")

    # --------------------------------------------------------
    # POST:
    # Process password-reset request.
    # --------------------------------------------------------

    email = (
        request.form.get(
            "email",
            "",
        )
        .strip()
        .lower()
    )

    if not email:

        flash(
            "Please enter your email address.",
            "danger",
        )

        return redirect(url_for("reset_password"))

    cur = get_db().cursor()

    try:

        # ----------------------------------------------------
        # Find active account.
        # ----------------------------------------------------

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(email) = %s
              AND is_active = TRUE
            """,
            (email,),
        )

        user = cur.fetchone()

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # We always return the same message regardless of
        # whether the email exists.
        #
        # This prevents simple email enumeration.
        # ----------------------------------------------------

        if user:

            user_id = user[0]

            # ------------------------------------------------
            # Basic cooldown:
            #
            # Only one reset request per account every
            # 60 seconds.
            # ------------------------------------------------

            cur.execute(
                """
                SELECT id
                FROM password_reset_tokens
                WHERE user_id = %s
                  AND created_at >=
                      CURRENT_TIMESTAMP
                      - INTERVAL '60 seconds'
                LIMIT 1
                """,
                (user_id,),
            )

            recent_request = cur.fetchone()

            if not recent_request:

                # --------------------------------------------
                # Invalidate previous unused reset tokens.
                # --------------------------------------------

                cur.execute(
                    """
                    UPDATE password_reset_tokens
                    SET used_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                      AND used_at IS NULL
                    """,
                    (user_id,),
                )

                # --------------------------------------------
                # Generate a cryptographically secure token.
                #
                # token_urlsafe(32) gives us 32 random bytes
                # encoded into a URL-safe string.
                # --------------------------------------------

                raw_token = secrets.token_urlsafe(32)

                # --------------------------------------------
                # Store only the SHA-256 hash.
                #
                # The actual reset token is never stored in
                # the database.
                # --------------------------------------------

                token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

                # --------------------------------------------
                # Store token with 30-minute expiration.
                # --------------------------------------------

                cur.execute(
                    """
                    INSERT INTO password_reset_tokens
                    (
                        user_id,
                        token_hash,
                        expires_at
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        CURRENT_TIMESTAMP
                        + INTERVAL '30 minutes'
                    )
                    """,
                    (
                        user_id,
                        token_hash,
                    ),
                )

                # --------------------------------------------
                # Build reset URL.
                #
                # APP_BASE_URL should be your Render URL in
                # production.
                # --------------------------------------------

                base_url = os.getenv("APP_BASE_URL")

                if not base_url:

                    base_url = request.url_root.rstrip("/")

                reset_url = f"{base_url}" f"/reset_password/" f"{quote(raw_token)}"

                try:

                    # ----------------------------------------
                    # Send email.
                    # ----------------------------------------

                    send_password_reset_email(
                        email,
                        reset_url,
                    )

                except Exception as email_error:

                    # ----------------------------------------
                    # Email failed.
                    #
                    # Roll back the token creation and any
                    # previous-token invalidation.
                    # ----------------------------------------

                    get_db().rollback()

                    print("Password reset email error: " f"{email_error}")

                else:

                    # ----------------------------------------
                    # Email was sent successfully.
                    # Commit token transaction.
                    # ----------------------------------------

                    get_db().commit()

        # ----------------------------------------------------
        # Always return the same response.
        # ----------------------------------------------------

        flash(
            "If an account with that email exists, "
            "a password reset link has been sent.",
            "info",
        )

    except Exception as e:

        get_db().rollback()

        print(f"Password reset request error: {e}")

        flash(
            "Unable to process the request right now. " "Please try again later.",
            "danger",
        )

    finally:

        cur.close()

    return redirect(url_for("home"))


# ============================================================
# RESET PASSWORD USING TOKEN
# ============================================================


@app.route(
    "/reset_password/<token>",
    methods=["GET", "POST"],
)
def reset_password_with_token(token):

    # --------------------------------------------------------
    # Convert the supplied token into the hash stored in DB.
    # --------------------------------------------------------

    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    cur = get_db().cursor()

    try:

        # ----------------------------------------------------
        # GET:
        #
        # We only need to check whether the token is valid.
        # No database lock is necessary here.
        # ----------------------------------------------------

        if request.method == "GET":

            cur.execute(
                """
                SELECT
                    prt.id,
                    prt.user_id
                FROM password_reset_tokens AS prt
                INNER JOIN users AS u
                    ON u.id = prt.user_id
                WHERE prt.token_hash = %s
                  AND prt.used_at IS NULL
                  AND prt.expires_at > CURRENT_TIMESTAMP
                  AND u.is_active = TRUE
                """,
                (token_hash,),
            )

            reset_token = cur.fetchone()

            if not reset_token:

                flash(
                    "This password reset link is invalid " "or has expired.",
                    "danger",
                )

                return redirect(url_for("home"))

            # ------------------------------------------------
            # Valid token:
            # Show new-password form.
            # ------------------------------------------------

            return render_template(
                "reset_password_form.html",
                token=token,
            )

        # ----------------------------------------------------
        # POST:
        #
        # Lock the token row using FOR UPDATE.
        #
        # This prevents two simultaneous requests from
        # successfully using the same token.
        # ----------------------------------------------------

        cur.execute(
            """
            SELECT
                prt.id,
                prt.user_id
            FROM password_reset_tokens AS prt
            INNER JOIN users AS u
                ON u.id = prt.user_id
            WHERE prt.token_hash = %s
              AND prt.used_at IS NULL
              AND prt.expires_at > CURRENT_TIMESTAMP
              AND u.is_active = TRUE
            FOR UPDATE
            """,
            (token_hash,),
        )

        reset_token = cur.fetchone()

        if not reset_token:

            get_db().rollback()

            flash(
                "This password reset link is invalid " "or has expired.",
                "danger",
            )

            return redirect(url_for("home"))

        reset_token_id = reset_token[0]

        user_id = reset_token[1]

        # ----------------------------------------------------
        # Read submitted passwords.
        # ----------------------------------------------------

        new_password = request.form.get(
            "new_password",
            "",
        )

        confirm_password = request.form.get(
            "confirm_password",
            "",
        )

        # ----------------------------------------------------
        # Password length validation.
        # ----------------------------------------------------

        if len(new_password) < 8:

            get_db().rollback()

            flash(
                "Password must be at least " "8 characters long.",
                "danger",
            )

            return render_template(
                "reset_password_form.html",
                token=token,
            )

        # ----------------------------------------------------
        # Password confirmation.
        # ----------------------------------------------------

        if new_password != confirm_password:

            get_db().rollback()

            flash(
                "Passwords do not match.",
                "danger",
            )

            return render_template(
                "reset_password_form.html",
                token=token,
            )

        # ----------------------------------------------------
        # Hash new password.
        # ----------------------------------------------------

        hashed_password = generate_password_hash(new_password)

        # ----------------------------------------------------
        # Update password.
        # ----------------------------------------------------

        cur.execute(
            """
            UPDATE users
            SET
                password = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
              AND is_active = TRUE
            """,
            (
                hashed_password,
                user_id,
            ),
        )

        # ----------------------------------------------------
        # Mark the current token as used.
        # ----------------------------------------------------

        cur.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = CURRENT_TIMESTAMP
            WHERE id = %s
            """,
            (reset_token_id,),
        )

        # ----------------------------------------------------
        # Invalidate all other outstanding reset tokens
        # belonging to this user.
        # ----------------------------------------------------

        cur.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
              AND used_at IS NULL
            """,
            (user_id,),
        )

        # ----------------------------------------------------
        # Commit password change + token invalidation
        # atomically.
        # ----------------------------------------------------

        get_db().commit()

        flash(
            "Your password has been reset successfully. "
            "You can now log in with your new password.",
            "success",
        )

        return redirect(url_for("home"))

    except Exception as e:

        get_db().rollback()

        print("Password reset completion error: " f"{e}")

        flash(
            "Unable to reset your password right now.",
            "danger",
        )

        return redirect(url_for("home"))

    finally:

        cur.close()


# ============================================================
# CONTACT US
# ============================================================


@app.route(
    "/contact_us",
    methods=["POST"],
)
def contact_us():

    email = request.form["email"]

    message = request.form["message"]

    flash(
        "Thanks for contacting us! " "We'll get back to you soon.",
        "success",
    )

    return redirect(url_for("home"))


# ============================================================
# ABOUT US
# ============================================================


@app.route("/about_us")
def about_us():

    message = request.args.get("message")

    category = request.args.get("category")

    if message and category:

        flash(
            message,
            category,
        )

    return render_template("about_us.html")


# ============================================================
# FACULTY DASHBOARD
# ============================================================


@app.route("/faculty_dashboard")
def faculty_dashboard():

    if "user_id" not in session:

        flash(
            "Please login as faculty to access this page.",
            "warning",
        )

        return redirect(url_for("home"))

    if session.get("user_type") != "faculty":

        flash(
            "Access denied. " "This page is for faculty members only.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                title,
                type,
                audience,
                date_posted,
                CASE
                    WHEN valid_until IS NULL
                        THEN 'Active'
                    WHEN valid_until > CURRENT_DATE
                        THEN 'Active'
                    WHEN valid_until = CURRENT_DATE
                        THEN 'Expiring'
                    ELSE 'Expired'
                END AS status
            FROM circulars
            WHERE posted_by_id = %s
            ORDER BY date_posted DESC
            LIMIT 5
            """,
            (session["user_id"],),
        )

        recent_circulars = cur.fetchall()

        return render_template(
            "faculty_dashboard.html",
            user_email=session.get("email"),
            recent_circulars=recent_circulars,
        )

    finally:

        cur.close()


# ============================================================
# STUDENT DASHBOARD
# ============================================================


@app.route("/student_dashboard")
def student_dashboard():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        cur.execute("""
            SELECT
                id,
                title,
                description,
                type,
                audience,
                priority,
                TO_CHAR(
                    date_posted,
                    'YYYY-MM-DD'
                ) AS date_posted
            FROM circulars
            WHERE (
                audience = 'students'
                OR audience = 'all'
                OR audience LIKE '%%students%%'
            )
            ORDER BY date_posted DESC
            LIMIT 3
            """)

        columns = [col[0] for col in cur.description]

        recent_circulars = []

        for row in cur.fetchall():

            circular = dict(zip(columns, row))

            recent_circulars.append(circular)

        cur.execute("""
            SELECT
                id,
                title,
                subject,
                branch,
                semester,
                deadline,
                total_marks
            FROM assignments
            WHERE status = 'active'
            ORDER BY deadline ASC
            LIMIT 3
            """)

        columns = [col[0] for col in cur.description]

        upcoming_assignments = []

        for row in cur.fetchall():

            assignment = dict(zip(columns, row))

            upcoming_assignments.append(assignment)

        return render_template(
            "student_dashboard.html",
            user_email=session.get("email"),
            recent_circulars=recent_circulars,
            upcoming_assignments=upcoming_assignments,
        )

    finally:

        cur.close()


# ============================================================
# STUDENTS
# ============================================================


@app.route("/students")
def students():

    if "user_id" not in session:

        flash(
            "Please login as student to access this page.",
            "warning",
        )

        return redirect(url_for("home"))

    if session.get("user_type") != "student":

        flash(
            "Access denied. " "This page is for students only.",
            "danger",
        )

        return redirect(url_for("home"))

    return render_template("students.html")


# ============================================================
# LOGOUT
# ============================================================


@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success",
    )

    return redirect(url_for("home"))


# ============================================================
# POST CIRCULAR
# ============================================================


@app.route(
    "/post_circular",
    methods=["POST"],
)
def post_circular():

    if not session.get("user_id") or session.get("user_type") != "faculty":

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Unauthorized",
                }
            ),
            401,
        )

    try:

        title = request.form.get("title")

        description = request.form.get("description")

        circular_type = request.form.get("circular_type")

        audience = request.form.get("target_audience")

        priority = request.form.get(
            "priority",
            "medium",
        )

        valid_until = request.form.get("valid_until")

        attachment = None

        # ----------------------------------------------------
        # Upload attachment to Supabase Storage
        # ----------------------------------------------------

        if "attachment" in request.files:

            file = request.files["attachment"]

            if file and file.filename:

                attachment, _, _ = upload_to_storage(
                    file,
                    "circulars",
                )

        # ----------------------------------------------------
        # Insert database record
        # ----------------------------------------------------

        cur = get_db().cursor()

        try:

            query = """
                INSERT INTO circulars
                (
                    title,
                    description,
                    type,
                    audience,
                    priority,
                    valid_until,
                    attachment,
                    date_posted,
                    posted_by,
                    posted_by_id
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
            """

            values = (
                title,
                description,
                circular_type,
                audience,
                priority,
                valid_until if valid_until else None,
                attachment,
                datetime.now(),
                session.get("email"),
                session.get("user_id"),
            )

            cur.execute(
                query,
                values,
            )

            get_db().commit()

        finally:

            cur.close()

        print(f"Circular inserted: {title}")

        return jsonify(
            {
                "success": True,
                "message": "Circular posted successfully",
            }
        )

    except Exception as e:

        get_db().rollback()

        print(f"Error posting circular: {e}")

        return (
            jsonify(
                {
                    "success": False,
                    "message": str(e),
                }
            ),
            500,
        )


# ============================================================
# DOWNLOAD CIRCULAR
# ============================================================


@app.route("/download_circular/<int:circular_id>")
def download_circular(circular_id):

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT attachment
            FROM circulars
            WHERE id = %s
            """,
            (circular_id,),
        )

        result = cur.fetchone()

        if not result or not result[0]:

            flash(
                "Attachment not found.",
                "danger",
            )

            return redirect(url_for("announcements"))

        storage_path = result[0]

        file_bytes = download_from_storage(storage_path)

        original_filename = os.path.basename(storage_path)

        return send_file(
            io.BytesIO(file_bytes),
            as_attachment=False,
            download_name=original_filename,
            mimetype=(
                mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
            ),
        )

    except Exception as e:

        print("Error downloading circular " f"attachment: {e}")

        flash(
            "Unable to open attachment.",
            "danger",
        )

        return redirect(url_for("announcements"))

    finally:

        cur.close()


# ============================================================
# ANNOUNCEMENTS
# ============================================================


@app.route("/announcements")
def announcements():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        today = datetime.now().date()

        print("=" * 60)

        print("ANNOUNCEMENTS PAGE DEBUG - START")

        print(f"Today's date: {today}")

        cur.execute("SELECT to_regclass('public.circulars')")

        table_exists_result = cur.fetchone()

        table_exists = table_exists_result and table_exists_result[0] is not None

        print("Circulars table exists: " f"{table_exists}")

        if not table_exists:

            print("ERROR: circulars table " "does not exist!")

            return render_template(
                "announcements.html",
                circulars=[],
                today=today,
            )

        cur.execute("SELECT COUNT(*) FROM circulars")

        count = cur.fetchone()[0]

        print(f"Total circulars in database: {count}")

        if count == 0:

            print("No circulars found - " "showing empty state")

            return render_template(
                "announcements.html",
                circulars=[],
                today=today,
            )

        query = """
            SELECT
                id,
                title,
                description,
                type,
                audience,
                priority,
                date_posted,
                attachment,
                valid_until,
                posted_by
            FROM circulars
            ORDER BY date_posted DESC
        """

        cur.execute(query)

        columns = [col[0] for col in cur.description]

        rows = cur.fetchall()

        circulars = []

        for row in rows:

            circular = dict(zip(columns, row))

            if circular["valid_until"]:

                try:

                    if isinstance(
                        circular["valid_until"],
                        str,
                    ):

                        valid_date = datetime.strptime(
                            circular["valid_until"],
                            "%Y-%m-%d",
                        ).date()

                    else:

                        valid_date = circular["valid_until"]

                    circular["is_active"] = 1 if valid_date >= today else 0

                except Exception as e:

                    print(f"Error parsing date: {e}")

                    circular["is_active"] = 1

            else:

                circular["is_active"] = 1

            circulars.append(circular)

        return render_template(
            "announcements.html",
            circulars=circulars,
            today=today,
        )

    except Exception as e:

        print(f"ERROR in announcements route: {e}")

        import traceback

        traceback.print_exc()

        return render_template(
            "announcements.html",
            circulars=[],
            today=today,
        )

    finally:

        cur.close()


# ============================================================
# GET CIRCULAR
# ============================================================


@app.route("/get_circular/<int:circular_id>")
def get_circular(circular_id):

    if "user_id" not in session:

        return (
            jsonify({"error": "Unauthorized"}),
            401,
        )

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                title,
                description,
                type,
                audience,
                priority,
                TO_CHAR(
                    date_posted,
                    'YYYY-MM-DD HH24:MI:SS'
                ) AS date_posted,
                attachment,
                valid_until,
                posted_by
            FROM circulars
            WHERE id = %s
            """,
            (circular_id,),
        )

        columns = [col[0] for col in cur.description]

        row = cur.fetchone()

        if row:

            circular = dict(zip(columns, row))

            return jsonify(circular)

        return (
            jsonify({"error": "Circular not found"}),
            404,
        )

    except Exception as e:

        print(f"Error in get_circular: {e}")

        return (
            jsonify({"error": str(e)}),
            500,
        )

    finally:

        cur.close()


# ============================================================
# GET RECENT CIRCULARS
# ============================================================


@app.route("/get_recent_circulars")
def get_recent_circulars():

    if "user_id" not in session:

        return (
            jsonify({"circulars": []}),
            401,
        )

    cur = get_db().cursor()

    try:

        cur.execute("""
            SELECT
                id,
                title,
                description,
                type,
                TO_CHAR(
                    date_posted,
                    'YYYY-MM-DD HH24:MI:SS'
                ) AS date_posted
            FROM circulars
            WHERE date_posted >=
                NOW() - INTERVAL '7 days'
            ORDER BY date_posted DESC
            """)

        columns = [col[0] for col in cur.description]

        recent = []

        for row in cur.fetchall():

            item = dict(zip(columns, row))

            if item["description"] and len(item["description"]) > 100:

                item["description"] = item["description"][:100] + "..."

            recent.append(item)

        return jsonify({"circulars": recent})

    except Exception:

        return jsonify({"circulars": []})

    finally:

        cur.close()


# ============================================================
# CONTEXT PROCESSORS
# ============================================================


@app.context_processor
def inject_user():

    return dict(
        logged_in="user_id" in session,
        user_type=session.get("user_type"),
        user_email=session.get("email"),
    )


@app.context_processor
def inject_current_year():

    return {"current_year": datetime.now().year}


# ============================================================
# ASSIGNMENTS
# ============================================================


@app.route("/assignments")
def assignments():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        cur.execute("""
            SELECT
                id,
                title,
                description,
                branch,
                semester,
                subject,
                total_questions,
                deadline,
                total_marks,
                attachment,
                date_posted,
                created_by,
                status
            FROM assignments
            ORDER BY date_posted DESC
            """)

        columns = [col[0] for col in cur.description]

        assignments_list = []

        for row in cur.fetchall():

            assignment = dict(zip(columns, row))

            assignments_list.append(assignment)

        return render_template(
            "assignments.html",
            assignments=assignments_list,
        )

    except Exception as e:

        print(f"Error: {e}")

        return render_template(
            "assignments.html",
            assignments=[],
        )

    finally:

        cur.close()


# ============================================================
# POST ASSIGNMENT
# ============================================================


@app.route(
    "/post_assignment",
    methods=["POST"],
)
def post_assignment():

    if not session.get("user_id") or session.get("user_type") != "faculty":

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Unauthorized",
                }
            ),
            401,
        )

    try:

        title = request.form.get("title")

        description = request.form.get("description")

        branch = request.form.get("branch")

        semester = request.form.get("semester")

        subject = request.form.get("subject")

        total_questions = request.form.get(
            "total_questions",
            5,
        )

        deadline = request.form.get("deadline")

        total_marks = request.form.get(
            "total_marks",
            100,
        )

        attachment = None

        # ----------------------------------------------------
        # Upload assignment attachment
        # ----------------------------------------------------

        if "attachment" in request.files:

            file = request.files["attachment"]

            if file and file.filename:

                attachment, _, _ = upload_to_storage(
                    file,
                    "assignments",
                )

        # ----------------------------------------------------
        # Insert assignment
        # ----------------------------------------------------

        cur = get_db().cursor()

        try:

            query = """
                INSERT INTO assignments
                (
                    title,
                    description,
                    branch,
                    semester,
                    subject,
                    total_questions,
                    deadline,
                    total_marks,
                    attachment,
                    date_posted,
                    created_by,
                    created_by_id,
                    status
                )
                VALUES
                (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s
                )
            """

            values = (
                title,
                description,
                branch,
                semester,
                subject,
                total_questions,
                deadline,
                total_marks,
                attachment,
                datetime.now(),
                session.get("email"),
                session.get("user_id"),
                "active",
            )

            cur.execute(
                query,
                values,
            )

            get_db().commit()

        finally:

            cur.close()

        return jsonify(
            {
                "success": True,
                "message": "Assignment posted successfully",
            }
        )

    except Exception as e:

        get_db().rollback()

        print(f"Error posting assignment: {e}")

        return (
            jsonify(
                {
                    "success": False,
                    "message": str(e),
                }
            ),
            500,
        )


# ============================================================
# GET ASSIGNMENT
# ============================================================


@app.route("/get_assignment/<int:assignment_id>")
def get_assignment(assignment_id):

    if "user_id" not in session:

        return (
            jsonify({"error": "Unauthorized"}),
            401,
        )

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                title,
                description,
                branch,
                semester,
                subject,
                total_questions,
                deadline,
                total_marks,
                attachment,
                TO_CHAR(
                    date_posted,
                    'YYYY-MM-DD HH24:MI:SS'
                ) AS date_posted,
                created_by,
                status
            FROM assignments
            WHERE id = %s
            """,
            (assignment_id,),
        )

        columns = [col[0] for col in cur.description]

        row = cur.fetchone()

        if row:

            assignment = dict(zip(columns, row))

            return jsonify(assignment)

        return (
            jsonify({"error": "Assignment not found"}),
            404,
        )

    except Exception as e:

        return (
            jsonify({"error": str(e)}),
            500,
        )

    finally:

        cur.close()


# ============================================================
# DOWNLOAD ASSIGNMENT
# ============================================================


@app.route("/download_assignment/<int:assignment_id>")
def download_assignment(assignment_id):

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT attachment
            FROM assignments
            WHERE id = %s
            """,
            (assignment_id,),
        )

        result = cur.fetchone()

        if not result or not result[0]:

            flash(
                "Attachment not found.",
                "danger",
            )

            return redirect(url_for("assignments"))

        storage_path = result[0]

        file_bytes = download_from_storage(storage_path)

        original_filename = os.path.basename(storage_path)

        return send_file(
            io.BytesIO(file_bytes),
            as_attachment=False,
            download_name=original_filename,
            mimetype=(
                mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
            ),
        )

    except Exception as e:

        print("Error downloading assignment " f"attachment: {e}")

        flash(
            "Unable to open attachment.",
            "danger",
        )

        return redirect(url_for("assignments"))

    finally:

        cur.close()


# ============================================================
# INTERNAL MARKS - UPLOAD
# ============================================================


@app.route(
    "/upload_marks",
    methods=["GET", "POST"],
)
def upload_marks():

    if "user_id" not in session or session.get("user_type") != "faculty":

        flash(
            "Please login as faculty " "to access this page.",
            "warning",
        )

        return redirect(url_for("home"))

    if request.method == "POST":

        try:

            pin = request.form.get("pin")

            student_name = request.form.get("student_name")

            branch = request.form.get("branch")

            semester = request.form.get("semester")

            subject_code = request.form.get("subject_code")

            subject_name = request.form.get("subject_name")

            marks_obtained = request.form.get(
                "marks_obtained",
                0,
            )

            max_marks = request.form.get(
                "max_marks",
                30,
            )

            cur = get_db().cursor()

            try:

                query = """
                    INSERT INTO internal_marks
                    (
                        pin,
                        student_name,
                        branch,
                        semester,
                        subject_code,
                        subject_name,
                        marks_obtained,
                        max_marks,
                        uploaded_by,
                        uploaded_by_id,
                        date_uploaded
                    )
                    VALUES
                    (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s
                    )
                """

                values = (
                    pin,
                    student_name,
                    branch,
                    semester,
                    subject_code,
                    subject_name,
                    marks_obtained,
                    max_marks,
                    session.get("email"),
                    session.get("user_id"),
                    datetime.now(),
                )

                cur.execute(
                    query,
                    values,
                )

                get_db().commit()

            finally:

                cur.close()

            flash(
                "Marks uploaded successfully!",
                "success",
            )

            return redirect(url_for("view_marks"))

        except Exception as e:

            get_db().rollback()

            flash(
                f"Error: {str(e)}",
                "danger",
            )

            return redirect(url_for("upload_marks"))

    return render_template("upload_marks.html")


# ============================================================
# VIEW MARKS
# ============================================================


@app.route("/view_marks")
def view_marks():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        branch = request.args.get(
            "branch",
            "all",
        )

        semester = request.args.get(
            "semester",
            "all",
        )

        pin = request.args.get(
            "pin",
            None,
        )

        if pin:

            query = """
                SELECT *
                FROM internal_marks
                WHERE pin = %s
                ORDER BY id ASC
            """

            params = [pin]

            print(f"PIN search: {pin}")

        else:

            query = """
                SELECT *
                FROM internal_marks
                WHERE 1=1
            """

            params = []

            if session.get("user_type") == "faculty":

                query += """
                    AND uploaded_by_id = %s
                """

                params.append(session["user_id"])

            if branch != "all":

                query += """
                    AND branch = %s
                """

                params.append(branch)

            if semester != "all":

                query += """
                    AND semester = %s
                """

                params.append(semester)

            query += """
                ORDER BY date_uploaded DESC
            """

        print(f"Query: {query}")

        print(f"Params: {params}")

        cur.execute(
            query,
            params,
        )

        columns = [col[0] for col in cur.description]

        marks_list = []

        for row in cur.fetchall():

            mark = dict(zip(columns, row))

            if mark["date_uploaded"] and isinstance(
                mark["date_uploaded"],
                datetime,
            ):

                mark["date_uploaded"] = mark["date_uploaded"].strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            marks_list.append(mark)

        print("Total records found: " f"{len(marks_list)}")

        return render_template(
            "view_marks.html",
            marks_list=marks_list,
            current_branch=branch,
            current_semester=semester,
        )

    finally:

        cur.close()


# ============================================================
# STUDY MATERIALS
# ============================================================


@app.route("/study_materials")
def study_materials():

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        branch = request.args.get(
            "branch",
            "all",
        )

        semester = request.args.get(
            "semester",
            "all",
        )

        search = request.args.get(
            "search",
            "",
        )

        query = """
            SELECT *
            FROM study_materials
            WHERE 1=1
        """

        params = []

        if branch != "all":

            query += """
                AND branch = %s
            """

            params.append(branch)

        if semester != "all":

            query += """
                AND semester = %s
            """

            params.append(semester)

        if search:

            query += """
                AND (
                    title ILIKE %s
                    OR description ILIKE %s
                    OR filename ILIKE %s
                    OR subject_name ILIKE %s
                )
            """

            search_term = f"%{search}%"

            params.extend(
                [
                    search_term,
                    search_term,
                    search_term,
                    search_term,
                ]
            )

        query += """
            ORDER BY date_uploaded DESC
        """

        cur.execute(
            query,
            params,
        )

        columns = [col[0] for col in cur.description]

        materials = []

        for row in cur.fetchall():

            material = dict(zip(columns, row))

            if material["date_uploaded"] and isinstance(
                material["date_uploaded"],
                datetime,
            ):

                material["date_uploaded"] = material["date_uploaded"].strftime(
                    "%Y-%m-%d"
                )

            elif material["date_uploaded"]:

                material["date_uploaded"] = str(material["date_uploaded"])

            materials.append(material)

        return render_template(
            "view_study_materials.html",
            materials=materials,
            current_branch=branch,
            current_semester=semester,
            search_term=search,
        )

    finally:

        cur.close()


# ============================================================
# UPLOAD STUDY MATERIAL
# ============================================================


@app.route(
    "/upload_study_material",
    methods=["GET", "POST"],
)
def upload_study_material():

    if "user_id" not in session or session.get("user_type") != "faculty":

        flash(
            "Please login as faculty " "to access this page.",
            "warning",
        )

        return redirect(url_for("home"))

    if request.method == "POST":

        try:

            title = request.form.get("title")

            description = request.form.get("description")

            branch = request.form.get("branch")

            semester = request.form.get("semester")

            subject_code = request.form.get("subject_code")

            subject_name = request.form.get("subject_name")

            # ------------------------------------------------
            # Validate file
            # ------------------------------------------------

            if "file" not in request.files:

                flash(
                    "No file selected",
                    "danger",
                )

                return redirect(url_for("upload_study_material"))

            file = request.files["file"]

            if not file or not file.filename:

                flash(
                    "No file selected",
                    "danger",
                )

                return redirect(url_for("upload_study_material"))

            # ------------------------------------------------
            # Upload to Supabase Storage
            # ------------------------------------------------

            (
                storage_path,
                file_size,
                file_type,
            ) = upload_to_storage(
                file,
                "study_materials",
            )

            original_filename = file.filename

            # ------------------------------------------------
            # Insert metadata into PostgreSQL
            # ------------------------------------------------

            cur = get_db().cursor()

            try:

                query = """
                    INSERT INTO study_materials
                    (
                        title,
                        description,
                        filename,
                        original_filename,
                        file_size,
                        file_type,
                        branch,
                        semester,
                        subject_code,
                        subject_name,
                        uploaded_by,
                        uploaded_by_id,
                        date_uploaded
                    )
                    VALUES
                    (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s
                    )
                """

                values = (
                    title,
                    description,
                    storage_path,
                    original_filename,
                    file_size,
                    file_type,
                    branch,
                    semester if semester else None,
                    subject_code,
                    subject_name,
                    session.get("email"),
                    session.get("user_id"),
                    datetime.now(),
                )

                cur.execute(
                    query,
                    values,
                )

                get_db().commit()

            finally:

                cur.close()

            flash(
                "Study material uploaded successfully!",
                "success",
            )

            return redirect(url_for("study_materials"))

        except Exception as e:

            get_db().rollback()

            print("Error uploading study " f"material: {e}")

            flash(
                f"Error uploading file: {str(e)}",
                "danger",
            )

            return redirect(url_for("upload_study_material"))

    return render_template("upload_study_material.html")


# ============================================================
# DOWNLOAD STUDY MATERIAL
# ============================================================


@app.route("/download_study_material/<int:material_id>")
def download_study_material(material_id):

    if "user_id" not in session:

        flash(
            "Please login first.",
            "danger",
        )

        return redirect(url_for("home"))

    cur = get_db().cursor()

    try:

        cur.execute(
            """
            SELECT
                filename,
                original_filename
            FROM study_materials
            WHERE id = %s
            """,
            (material_id,),
        )

        result = cur.fetchone()

        if not result:

            flash(
                "Material not found",
                "danger",
            )

            return redirect(url_for("study_materials"))

        storage_path = result[0]

        original_filename = result[1]

        # ----------------------------------------------------
        # Download from Supabase Storage
        # ----------------------------------------------------

        try:

            file_bytes = download_from_storage(storage_path)

        except Exception as e:

            print("Error downloading from " "Supabase Storage: " f"{e}")

            flash(
                "File not found in " "Supabase Storage.",
                "danger",
            )

            return redirect(url_for("study_materials"))

        # ----------------------------------------------------
        # Increment download count
        # ----------------------------------------------------

        cur.execute(
            """
            UPDATE study_materials
            SET download_count =
                download_count + 1
            WHERE id = %s
            """,
            (material_id,),
        )

        get_db().commit()

        return send_file(
            io.BytesIO(file_bytes),
            as_attachment=True,
            download_name=original_filename,
            mimetype=(
                mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
            ),
        )

    finally:

        cur.close()


# ============================================================
# DELETE STUDY MATERIAL
# ============================================================


@app.route(
    "/delete_study_material/<int:material_id>",
    methods=["POST"],
)
def delete_study_material(material_id):

    if "user_id" not in session or session.get("user_type") != "faculty":

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Unauthorized",
                }
            ),
            401,
        )

    cur = get_db().cursor()

    try:

        # ----------------------------------------------------
        # Find Storage path
        # ----------------------------------------------------

        cur.execute(
            """
            SELECT filename
            FROM study_materials
            WHERE id = %s
              AND uploaded_by_id = %s
            """,
            (
                material_id,
                session["user_id"],
            ),
        )

        result = cur.fetchone()

        if not result:

            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Material not found",
                    }
                ),
                404,
            )

        storage_path = result[0]

        # ----------------------------------------------------
        # Delete database record
        # ----------------------------------------------------

        cur.execute(
            """
            DELETE FROM study_materials
            WHERE id = %s
              AND uploaded_by_id = %s
            """,
            (
                material_id,
                session["user_id"],
            ),
        )

        get_db().commit()

        # ----------------------------------------------------
        # Delete file from Supabase Storage
        # ----------------------------------------------------

        delete_from_storage(storage_path)

        return jsonify(
            {
                "success": True,
                "message": "Material deleted successfully",
            }
        )

    except Exception as e:

        get_db().rollback()

        print(f"Error deleting study material: {e}")

        return (
            jsonify(
                {
                    "success": False,
                    "message": "Unable to delete material.",
                }
            ),
            500,
        )

    finally:

        cur.close()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000,
    )
