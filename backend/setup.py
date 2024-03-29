from flask_migrate import Migrate
from app import create_app, db
from app.models import User
from app.auth.routes import current_user

app = create_app()
# migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, current_user=current_user)

print("App created")