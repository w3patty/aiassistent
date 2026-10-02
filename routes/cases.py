import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)

from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db
from models.case import Case
from models.document import Document

from services.document_parser import extract_text


cases = Blueprint("cases", __name__)


ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}


def allowed_file(filename):

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


@cases.route("/case", methods=["GET", "POST"])
@login_required
def case_list():

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        client_name = request.form.get("client_name", "").strip()
        description = request.form.get("description", "").strip()

        if not title or not client_name:

            flash(
                "азвание дела и клиент обязательны.",
                "error"
            )

            return redirect(
                url_for("cases.case_list")
            )

        new_case = Case(
            title=title,
            client_name=client_name,
            description=description,
            status="овое",
            user_id=current_user.id
        )

        db.session.add(new_case)
        db.session.commit()

        flash(
            "ело успешно создано.",
            "success"
        )

        return redirect(
            url_for("cases.case_list")
        )

    user_cases = Case.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Case.created_at.desc()
    ).all()

    return render_template(
        "cases.html",
        cases=user_cases
    )


@cases.route("/case/<int:case_id>", methods=["GET"])
@login_required
def case_detail(case_id):

    case = Case.query.filter_by(
        id=case_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "case.html",
        case=case
    )


@cases.route(
    "/case/<int:case_id>/upload",
    methods=["POST"]
)
@login_required
def upload_document(case_id):

    case = Case.query.filter_by(
        id=case_id,
        user_id=current_user.id
    ).first_or_404()

    file = request.files.get("document")

    if not file or not file.filename:

        flash(
            "ыберите документ.",
            "error"
        )

        return redirect(
            url_for(
                "cases.case_detail",
                case_id=case.id
            )
        )

    if not allowed_file(file.filename):

        flash(
            "оддерживаются только PDF, DOCX и TXT.",
            "error"
        )

        return redirect(
            url_for(
                "cases.case_detail",
                case_id=case.id
            )
        )

    original_filename = secure_filename(
        file.filename
    )

    extension = original_filename.rsplit(
        ".",
        1
    )[1].lower()

    unique_filename = (
        str(uuid.uuid4())
        + "."
        + extension
    )

    upload_folder = os.path.join(
        "uploads",
        str(current_user.id),
        str(case.id)
    )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    filepath = os.path.join(
        upload_folder,
        unique_filename
    )

    file.save(filepath)

    try:

        extracted_text = extract_text(
            filepath,
            extension
        )

    except Exception as error:

        print(
            "шибка извлечения текста:",
            error
        )

        extracted_text = ""

    document = Document(
        filename=original_filename,
        filepath=filepath,
        file_type=extension,
        extracted_text=extracted_text,
        case_id=case.id
    )

    db.session.add(document)
    db.session.commit()

    flash(
        "окумент успешно загружен.",
        "success"
    )

    return redirect(
        url_for(
            "cases.case_detail",
            case_id=case.id
        )
    )


@cases.route(
    "/document/<int:document_id>",
    methods=["GET"]
)
@login_required
def document_detail(document_id):

    document = Document.query.get_or_404(
        document_id
    )

    case = Case.query.filter_by(
        id=document.case_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "document.html",
        document=document,
        case=case
    )
