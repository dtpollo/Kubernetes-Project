# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields
from sqlalchemy import Column, Integer, String, Date

event_bp = Blueprint('event_bp', __name__)

# SQLAlchemy Model
class Event(db.Model):
    __tablename__ = 'event'
    ev_id = Column(Integer, primary_key=True)
    ev_name = Column(String(100), nullable=False)
    ev_description = Column(String(200), nullable=False)
    ev_date = Column(Date, nullable=False, unique=True)

# Marshmallow Schema
class EventSchema(Schema):
    ev_id = fields.Int(dump_only=True)
    ev_name = fields.Str(required=True)
    ev_description = fields.Str(required=True)
    ev_date = fields.Date(required=True)

event_schema = EventSchema()
events_schema = EventSchema(many=True)

#Endpoints (CRUD)
"""
-> GET all events
curl http://localhost:5000/events
"""
@event_bp.route('/events', methods=['GET'])
def get_events():
    all_events = Event.query.all()
    if not all_events:
        return jsonify({"Error": "No Events found"}), 404
    return jsonify(events_schema.dump(all_events)), 200


"""
-> GET one event by ID
curl http://localhost:5000/events/<event_id>
"""
@event_bp.route('/events/<int:ev_id>', methods=['GET'])
def get_event(ev_id):
    event = Event.query.get(ev_id)
    if not event:
        return jsonify({"Error": "Event not found"}), 404
    return jsonify(event_schema.dump(event)), 200



"""
-> POST new event
curl -X POST http://localhost:5000/events \
    -H "Content-Type: application/json" \
    -d '{
            "ev_name": "<event_name>",
            "ev_description": "<event_description>",
            "ev_date": "<year-month-day>"
        }'
"""
@event_bp.route('/events', methods=['POST'])
def add_event():
    data = request.json
    errors = event_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400
    
    new_event = Event(
        ev_name=data['ev_name'],
        ev_description=data['ev_description'],
        ev_date=data['ev_date']
    )
    db.session.add(new_event)
    db.session.commit()
    return jsonify(event_schema.dump(new_event)), 201


"""
-> PUT update event info
curl -X PUT http://localhost:5000/events/<event_id> \
    -H "Content-Type: application/json" \
    -d '{"ev_description": "<event_description>"}'
"""
@event_bp.route('/events/<int:ev_id>', methods=['PUT'])
def update_event(ev_id):
    event = Event.query.get(ev_id)
    if not event:
        return jsonify({"Error": "Event not found"}), 404
    
    data = request.json
    errors = event_schema.validate(data, partial=True)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400

    if 'ev_name' in data:
        event.ev_name = data['ev_name']

    if 'ev_description' in data:
        event.ev_description = data['ev_description']
    
    if 'ev_date' in data and data['ev_date'] != str(event.ev_date):
        if Event.query.filter_by(ev_date=data['ev_date']).first():
            return jsonify({"Error": "Event date already exists"}), 409

    db.session.commit()
    return jsonify(event_schema.dump(event)), 200

"""
-> DELETE event by ID
curl -X DELETE http://localhost:5000/events/<event_id>
"""
@event_bp.route('/events/<int:ev_id>', methods=['DELETE'])
def delete_event(ev_id):
    event = Event.query.get(ev_id)
    if not event:
        return jsonify({"Error": "Event not found"}), 404
    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "Event deleted"}), 200
