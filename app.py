import os

from flask import Flask

from config import Config
from models import db, login_manager
from models.user import User


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Инициализация базы
    db.init_app(app)

    # Инициализация авторизации
    login_manager.init_app(app)

    # Создание папки instance
    os.makedirs(
        os.path.join(app.root_path, "instance"),
        exist_ok=True
    )

    # Импортируем модели
    from models.case import Case
    from models.document import Document

    # Создаём базу и таблицы
    with app.app_context():
        db.create_all()

    # Подключаем маршруты
    from routes.main import main
    from routes.auth import auth
    from routes.cases import cases

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(cases)

    return app


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )