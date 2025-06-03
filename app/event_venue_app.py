# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields
from sqlalchemy import Column, Integer, ForeignKey
from event_app import Event
from venue_app import Venue

event_venue_bp = Blueprint('event_venue_bp', __name__)

# SQLAlchemy Model
class EventVenue(db.Model):
    __tablename__ = 'event_venue'
    ev_ven_id = Column(Integer, primary_key=True)
    ev_id = Column(Integer, ForeignKey('event.ev_id', ondelete='CASCADE'), nullable=False)
    vn_id = Column(Integer, ForeignKey('venue.vn_id', ondelete='CASCADE'), nullable=False)

# Marshmallow Schema
class EventVenueSchema(Schema):
    ev_ven_id = fields.Int(dump_only=True)
    ev_id = fields.Int(required=True)
    vn_id = fields.Int(required=True)

event_venue_schema = EventVenueSchema()
event_venues_schema = EventVenueSchema(many=True)


#Endpoints (CRUD)
"""
-> GET all event_venue relations
curl http://localhost:5000/event_venues
"""
@event_venue_bp.route('/event_venues', methods=['GET'])
def get_event_venues():
    all_entries = EventVenue.query.all()
    if not all_entries:
        return jsonify({"Error": "Venues assign to Events not found"}), 404
    return jsonify(event_venues_schema.dump(all_entries)), 200


"""
-> GET all the venues assigined to an event
curl http://localhost:5000/event_venues/<event_id>
"""
@event_venue_bp.route('/event_venues/<int:ev_id>', methods=['GET'])
def get_venues_by_event(ev_id):
    entries = EventVenue.query.filter_by(ev_id=ev_id).all()
    if not entries:
        return jsonify({"Error": "Venues assign to Events not found"}), 404
    return jsonify(event_venues_schema.dump(entries)), 200


"""
-> POST: Assign a new venue that is either available (free) or used on a different date
curl -X POST http://localhost:5000/event_venues \
    -H "Content-Type: application/json" \
    -d '{"ev_id": <event_id>, "vn_id": <venue_id>}'
"""
@event_venue_bp.route('/event_venues', methods=['POST'])
def add_event_venue():
    data = request.json
    errors = event_venue_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400
    
    existing = EventVenue.query.filter_by(ev_id=data['ev_id'], vn_id=data['vn_id']).first()
    if existing:
        return jsonify({'Error': 'This event already has this venue assigned'}), 409

    if not Event.query.get(data['ev_id']):
        return jsonify({'Error': 'Event ID not found'}), 404
    if not Venue.query.get(data['vn_id']):
        return jsonify({'Error': 'Venue ID not found'}), 404

    new_entry = EventVenue(
        ev_id=data['ev_id'],
        vn_id=data['vn_id']
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(event_venue_schema.dump(new_entry)), 201


"""
-> PUT update venue of event
curl -X PUT http://localhost:5000/event_venues/<event_venue_id> \
    -H "Content-Type: application/json" \
    -d '{"ev_id": <event_id>, "vn_id": <venue_id>}'
"""
@event_venue_bp.route('/event_venues/<int:ev_ven_id>', methods=['PUT'])
def update_event_venue(ev_ven_id):
    entry = EventVenue.query.get(ev_ven_id)
    data = request.json

    if not entry:
        return jsonify({"Error": "Venue assignment not found"}), 404
    
    if 'ev_id' in data:
        if not Event.query.get(data['ev_id']):
            return jsonify({'Error': 'Event ID not found'}), 404
        entry.ev_id = data['ev_id']

    if 'vn_id' in data:
        if not Venue.query.get(data['vn_id']):
            return jsonify({'Error': 'Venue ID not found'}), 404
        entry.vn_id = data['vn_id']

    db.session.commit()
    return jsonify(event_venue_schema.dump(entry)), 200



"""
-> DELETE venue for an event
curl -X DELETE http://localhost:5000/event_venues/<event_venue_id>
"""
@event_venue_bp.route('/event_venues/<int:ev_ven_id>', methods=['DELETE'])
def delete_event_venue(ev_ven_id):
    entry = EventVenue.query.get(ev_ven_id)
    if not entry:
        return jsonify({"Error": "Venue assignment not found"}), 404
    
    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Venue assignment to event has been deleted"}), 200
