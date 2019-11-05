from app import app, db
from app.models import User


if __name__ == '__main__':
    app.run(threaded=True, port=5000)

