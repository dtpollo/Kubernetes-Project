# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from event_app import Event
from staff_app import Staff
from venue_app import Venue

staff_venue_bp = Blueprint('staff_venue_bp', __name__)

# SQLAlchemy Model
class StaffVenue(db.Model):
    __tablename__ = 'staff_venue'
    sv_id = Column(Integer, primary_key=True)
    ev_id = Column(Integer, ForeignKey('event.ev_id', ondelete='CASCADE'), nullable=False)
    stf_id = Column(Integer, ForeignKey('staff.stf_id', ondelete='CASCADE'), nullable=False)
    vn_id = Column(Integer, ForeignKey('venue.vn_id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('ev_id', 'stf_id', 'vn_id', name='unique_assignment'),
    )

# Marshmallow Schema
class StaffVenueSchema(Schema):
    sv_id = fields.Int(dump_only=True)
    ev_id = fields.Int(required=True)
    stf_id = fields.Int(required=True)
    vn_id = fields.Int(required=True)

staff_venue_schema = StaffVenueSchema()
staff_venues_schema = StaffVenueSchema(many=True)

# Endpoints (CRUD)
"""
-> GET: Retrieve all staff assigned to venue entries
curl http://localhost:5000/staff_venue
"""
@staff_venue_bp.route('/staff_venue', methods=['GET'])
def get_staff_venue():
    all_records = StaffVenue.query.all()
    if not all_records:
        return jsonify({"Error": "Assigned Staff not found"}), 404
    return jsonify(staff_venues_schema.dump(all_records)), 200


"""
-> GET: Retrieve all staff assigned to a venue
curl http://localhost:5000/staff_venue/<venue_id>
"""
@staff_venue_bp.route('/staff_venue/<int:vn_id>', methods=['GET'])
def get_staff_by_venue(vn_id):
    records = StaffVenue.query.filter_by(vn_id=vn_id).all()
    if not records:
        return jsonify({"Error": "Staff-Venue assignment not found"}), 404
    return jsonify(staff_venues_schema.dump(records)), 200


"""
-> POST: assigned a staff member to a venue
curl -X POST http://localhost:5000/staff_venue \
    -H "Content-Type: application/json" \
    -d '{
            "ev_id": <event_id>,
            "stf_id": <staff_member_id>,
            "vn_id": <venue_id>
        }'
"""
@staff_venue_bp.route('/staff_venue', methods=['POST'])
def add_staff_venue():
    data = request.json
    errors = staff_venue_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400
    
    if not Event.query.get(data['ev_id']):
        return jsonify({'Error': 'Event not found'}), 404
    if not Staff.query.get(data['stf_id']):
        return jsonify({'Error': 'Staff not found'}), 404
    if not Venue.query.get(data['vn_id']):
        return jsonify({'Error': 'Venue not found'}), 404

    new_record = StaffVenue(
        ev_id=data['ev_id'],
        stf_id=data['stf_id'],
        vn_id=data['vn_id']
    )
    db.session.add(new_record)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    return jsonify(staff_venue_schema.dump(new_record)), 201


"""
-> PUT: Update assignment
curl -X PUT http://localhost:5000/staff_venue/<staff_venue_id> \
    -H "Content-Type: application/json" \
    -d '{"ev_id": <event_id>}'
"""
@staff_venue_bp.route('/staff_venue/<int:sv_id>', methods=['PUT'])
def update_staff_venue(sv_id):
    record = StaffVenue.query.get(sv_id)
    data = request.json
    errors = staff_venue_schema.validate(data, partial=True)
    if not record:
        return jsonify({"Error": "Staff-Venue assignment not found"}), 404
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400

    ev_id = data.get('ev_id')
    stf_id = data.get('stf_id')
    vn_id = data.get('vn_id')

    if ev_id and not Event.query.get(ev_id):
        return jsonify({'Error': 'Event not found'}), 404

    if stf_id and not Staff.query.get(stf_id):
        return jsonify({'Error': 'Staff not found'}), 404

    if vn_id and not Venue.query.get(vn_id):
        return jsonify({'Error': 'Venue not found'}), 404

    if ev_id:
        record.ev_id = ev_id
    if stf_id:
        record.stf_id = stf_id
    if vn_id:
        record.vn_id = vn_id

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    return jsonify(staff_venue_schema.dump(record)), 200

"""
-> DELETE: Remove a staff member's assignment from a venue
curl -X DELETE http://localhost:5000/staff_venue/<staff_venue_id>
"""
@staff_venue_bp.route('/staff_venue/<int:sv_id>', methods=['DELETE'])
def delete_staff_venue(sv_id):
    record = StaffVenue.query.get(sv_id)
    if not record:
        return jsonify({"Error": "Staff-Venue assignment not found"}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({"Message": "Staff assignment deleted from Venue"}), 200
