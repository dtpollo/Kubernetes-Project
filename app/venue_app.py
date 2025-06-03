# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields, validate
from sqlalchemy import Column, Integer, String

venue_bp = Blueprint('venue_bp', __name__)

# SQLAlchemy Model
class Venue(db.Model):
    __tablename__ = 'venue'
    vn_id = Column(Integer, primary_key=True)
    vn_name = Column(String(100), nullable=False)
    vn_type = Column(String(10), nullable=False)
    vn_capacity = Column(Integer, nullable=False)

# Marshmallow Schema
class VenueSchema(Schema):
    vn_id = fields.Int(dump_only=True)
    vn_name = fields.Str(required=True)
    vn_type = fields.Str(
        required=True,
        validate=validate.OneOf(['VIP', 'General', 'Premium'])
    )
    vn_capacity = fields.Int(
        required=True,
        validate=validate.Range(min=1)
    )

venue_schema = VenueSchema()
venues_schema = VenueSchema(many=True)

# Endpoints (CRUD)
"""
-> GET all venues
curl http://localhost:5000/venues
"""
@venue_bp.route('/venues', methods=['GET'])
def get_venues():
    all_venues = Venue.query.all()
    if not all_venues:
        return jsonify({"Error": "No venues found"}), 404
    return jsonify(venues_schema.dump(all_venues)), 200



"""
-> GET single Venue by ID
# curl http://localhost:5000/venues/<venue_id>
"""
@venue_bp.route('/venues/<int:vn_id>', methods=['GET'])
def get_venue(vn_id):
    venue = Venue.query.get(vn_id)
    if venue:
        return jsonify(venue_schema.dump(venue)), 200
    else:
        return jsonify({"Error": "Venue not found"}), 404


"""
-> POST new venue
curl -X POST http://localhost:5000/venues \
    -H "Content-Type: application/json" \
    -d '{
            "vn_name": "<venue_name>",
            "vn_type": "<venue_type>",
            "vn_capacity": <venue_capacity>
        }'
"""
@venue_bp.route('/venues', methods=['POST'])
def add_venue():
    data = request.json
    errors = venue_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "Details": errors}), 400
    
    elif Venue.query.filter_by(vn_name=data['vn_name']).first():
        return jsonify({"Error": "Venue already exists"}), 409

    else:
        new_venue = Venue(
            vn_name=data['vn_name'],
            vn_type=data['vn_type'],
            vn_capacity=data['vn_capacity']
        )
        db.session.add(new_venue)
        db.session.commit()
        return jsonify(venue_schema.dump(new_venue)), 201


"""
-> PUT update venue info
curl -X PUT http://localhost:5000/venues/<venue_id> \
    -H "Content-Type: application/json" \
    -d '{"vn_name": <venue_name>}'
"""
@venue_bp.route('/venues/<int:vn_id>', methods=['PUT'])
def update_venue(vn_id):
    venue = Venue.query.get(vn_id)
    if not venue:
        return jsonify({"Error": "Venue not found"}), 404
    
    data = request.json
    errors = venue_schema.validate(data, partial=True)

    if errors:
        return jsonify({"Error": "Invalid data", "Details": errors}), 400
    
    if 'vn_name' in data:
        if data['vn_name'] != venue.vn_name:
            if Venue.query.filter_by(vn_name=data['vn_name']).first():
                return jsonify({"Error": "Venue name already exists"}), 409
        venue.vn_name = data['vn_name']

    if 'vn_type' in data:
        venue.vn_type = data['vn_type']

    if 'vn_capacity' in data:
        venue.vn_capacity = data['vn_capacity']

    db.session.commit()
    return jsonify(venue_schema.dump(venue)), 200

"""
-> DELETE venue
curl -X DELETE http://localhost:5000/venues/<venue_id>
"""
@venue_bp.route('/venues/<int:vn_id>', methods=['DELETE'])
def delete_venue(vn_id):
    venue = Venue.query.get(vn_id)
    if not venue:
        return jsonify({"Error": "Venue not found"}), 404
    
    db.session.delete(venue)
    db.session.commit()
    return jsonify({"message": "Venue deleted"}), 200
