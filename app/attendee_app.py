# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields, validate
from sqlalchemy import Column, Integer, String

attendee_bp = Blueprint('attendee_bp', __name__)

# SQLAlchemy Model
class Attendee(db.Model):
    __tablename__ = 'attendee'
    att_id = Column(Integer, primary_key=True)
    att_name = Column(String(100), nullable=False)
    att_last_name = Column(String(100), nullable=False)
    att_email = Column(String(100), nullable=False, unique=True)
    att_phone = Column(String(10), nullable=False)

# Marshmallow Schema
class AttendeeSchema(Schema):
    att_id = fields.Int(dump_only=True)
    att_name = fields.Str(required=True)
    att_last_name = fields.Str(required=True)
    att_email = fields.Email(required=True)
    att_phone = fields.Str(required=True, validate=validate.Regexp(r'^09[0-9]{8}$',error="Phone must start with 09 and have 10 digits"))

attendee_schema = AttendeeSchema()
attendees_schema = AttendeeSchema(many=True)

# Endpoints (CRUD)
"""
-> GET all attendees
curl http://localhost:5000/attendees
"""
@attendee_bp.route('/attendees', methods=['GET'])
def get_attendees():
    all_attendees = Attendee.query.all()
    if not all_attendees:
        return jsonify({"Error": "Attendees not found"}), 404
    return jsonify(attendees_schema.dump(all_attendees)), 200



"""
-> GET single attendee by ID
curl http://localhost:5000/attendees/<attendee_id>
"""
@attendee_bp.route('/attendees/<int:att_id>', methods=['GET'])
def get_attendee(att_id):
    attendee = Attendee.query.get(att_id)
    if attendee:
        return jsonify(attendee_schema.dump(attendee)), 200
    else:
        return jsonify({"Error": "Attendee not found"}), 404


"""
-> POST new attendee
curl -X POST http://localhost:5000/attendees \
    -H "Content-Type: application/json" \
    -d '{
        "att_name": "<name>",
        "att_last_name": "<lastname>",
        "att_email": "<email>",
        "att_phone": "<number>"
    }'
"""
@attendee_bp.route('/attendees', methods=['POST'])
def add_attendee():
    data = request.json
    errors = attendee_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400

    elif Attendee.query.filter_by(att_email=data['att_email']).first():
        return jsonify({"Error": "Email already exists"}), 409
    
    else:
        new_attendee = Attendee(
            att_name=data['att_name'],
            att_last_name=data['att_last_name'],
            att_email=data['att_email'],
            att_phone=data['att_phone']
        )
        db.session.add(new_attendee)
        db.session.commit()
        return jsonify(attendee_schema.dump(new_attendee)), 201


"""
-> PUT update attendee info
curl -X PUT http://localhost:5000/attendees/<attendee_id> \
    -H "Content-Type: application/json" \
    -d '{"att_phone": "<attendee_phone>"}'
"""
@attendee_bp.route('/attendees/<int:att_id>', methods=['PUT'])
def update_attendee(att_id):
    attendee = Attendee.query.get(att_id)
    if not attendee:
        return jsonify({"Error": "Attendee not found"}), 404
    
    else:
        data = request.json
        if 'att_name' in data:
            attendee.att_name = data['att_name']

        if 'att_last_name' in data:
            attendee.att_last_name = data['att_last_name']

        if 'att_email' in data:
            if "@" not in data['att_email']:
                return jsonify({"Error": "Invalid email format"}), 400
            attendee.att_email = data['att_email']

        if 'att_phone' in data:
            if len(data['att_phone']) != 10:
                return jsonify({"Error": "Phone must have 10 digits"}), 400
            attendee.att_phone = data['att_phone']
        
        db.session.commit()
        return jsonify(attendee_schema.dump(attendee)), 200

"""
-> DELETE attendee by ID
curl -X DELETE http://localhost:5000/attendees/<attendee_id>
"""
@attendee_bp.route('/attendees/<int:att_id>', methods=['DELETE'])
def delete_attendee(att_id):
    attendee = Attendee.query.get(att_id)
    if not attendee:
        return jsonify({"Error": "Attendee not found"}), 404
    
    db.session.delete(attendee)
    db.session.commit()
    return jsonify({"Message": "Attendee deleted"}), 200
