# Header
from flask import Flask
from use_db import db
from attendee_app import attendee_bp
from event_app import event_bp
from purchase_app import purchase_bp
from staff_app import staff_bp
from staff_venue_app import staff_venue_bp
from supplier_app import supplier_bp
from ticket_app import ticket_bp
from ticket_status_app import ticket_status_bp
from venue_app import venue_bp
from event_venue_app import event_venue_bp
from config import Config

# Database Configuration
app = Flask(__name__)
app.config.from_object(Config) 
db.init_app(app)

# Blueprint Registration
app.register_blueprint(attendee_bp)
app.register_blueprint(event_bp)
app.register_blueprint(purchase_bp)
app.register_blueprint(staff_bp)
app.register_blueprint(staff_venue_bp)
app.register_blueprint(supplier_bp)
app.register_blueprint(ticket_bp)
app.register_blueprint(ticket_status_bp)
app.register_blueprint(venue_bp)
app.register_blueprint(event_venue_bp)

# Create all tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0")

