from flask import Flask
from models import db
from bharat.services.scheduler_service import start_scheduler
from bharat.routes.monitoring_routes import monitoring_bp

import threading
import os


# =========================================================
# App Factory
# =========================================================
def create_app():

    app = Flask(__name__)

    # -----------------------------------------------------
    # Database in project root
    # -----------------------------------------------------
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(BASE_DIR, "sentinelops.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JSON_SORT_KEYS"] = False

    db.init_app(app)

    # -----------------------------------------------------
    # Create tables
    # -----------------------------------------------------
    with app.app_context():
        db.create_all()

    print(f"✅ Database ready at: {db_path}")

    # -----------------------------------------------------
    # Register APIs
    # -----------------------------------------------------
    app.register_blueprint(monitoring_bp, url_prefix="/api")

    # -----------------------------------------------------
    # Health Route
    # -----------------------------------------------------
    @app.route("/")
    def home():
        return {
            "status": "running",
            "service": "SentinelOps",
            "mode": "Predictive Monitoring",
            "api_base": "/api"
        }

    return app


# =========================================================
# Create App Instance
# =========================================================
app = create_app()


# =========================================================
# Background Scheduler
# =========================================================
def run_scheduler(app):

    print("🟢 Scheduler thread started")

    # Ensure Flask context available to background tasks
    with app.app_context():
        start_scheduler()


# =========================================================
# Main Entry
# =========================================================
if __name__ == "__main__":

    print("🚀 Starting SentinelOps...")

    # -----------------------------------------------------
    # Start scheduler ONCE (handles debug reloader)
    # -----------------------------------------------------
    if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":

        scheduler_thread = threading.Thread(
            target=run_scheduler,
            args=(app,),
            daemon=True
        )
        scheduler_thread.start()

    # -----------------------------------------------------
    # Run Flask server
    # -----------------------------------------------------
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
