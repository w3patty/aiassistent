from datetime import datetime

from . import db


class Case(db.Model):
    __tablename__ = "cases"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    client_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(50),
        default="овое"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    documents = db.relationship(
        "Document",
        foreign_keys="Document.case_id",
        primaryjoin="Case.id == Document.case_id",
        back_populates="case",
        lazy=True,
        cascade="all, delete-orphan"
    )
