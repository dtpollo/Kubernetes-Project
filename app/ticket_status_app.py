# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields
from sqlalchemy import Column, Integer, String

ticket_status_bp = Blueprint('ticket_status_bp', __name__)

# SQLAlchemy Model
class TicketStatus(db.Model):
    __tablename__ = 'ticket_status'
    tic_status_id = Column(Integer, primary_key=True)
    description = Column(String(20), nullable=False)

# Marshmallow Schema
class TicketStatusSchema(Schema):
    tic_status_id = fields.Int(required=True)
    description = fields.Str(required=True)

ticket_status_schema = TicketStatusSchema()
statuses_schema = TicketStatusSchema(many=True)

# Endpoints (CRUD)
"""
-> GET all ticket status
curl http://localhost:5000/ticket_statuses
"""
@ticket_status_bp.route('/ticket_statuses', methods=['GET'])
def get_ticket_statuses():
    statuses = TicketStatus.query.all()
    if not statuses:
        return jsonify({"Error": "No ticket statuses found"}), 404
    return jsonify(statuses_schema.dump(statuses)), 200



"""
-> GET one ticket status by ID
# curl http://localhost:5000/ticket_statuses/<status_ticket_id>
"""
@ticket_status_bp.route('/ticket_statuses/<int:tic_status_id>', methods=['GET'])
def get_ticket_status(tic_status_id):
    status = TicketStatus.query.get(tic_status_id)
    if status:
        return jsonify(ticket_status_schema.dump(status)), 200
    else:
        return jsonify({"Error":"Ticket Status not found"}), 404


"""
-> POST new ticket status
curl -X POST http://localhost:5000/ticket_statuses \
    -H "Content-Type: application/json" \
    -d '{
            "tic_status_id": <status_ticket_id>,
            "description": "<status_ticket_description>"
        }'
"""
@ticket_status_bp.route('/ticket_statuses', methods=['POST'])
def add_ticket_status():
    data = request.json
    errors = ticket_status_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "Details": errors}), 400

    
    new_status = TicketStatus(
        tic_status_id=data['tic_status_id'],
        description=data['description']
    )
    db.session.add(new_status)
    db.session.commit()
    return jsonify(ticket_status_schema.dump(new_status)), 200


"""
-> PUT update ticket status
curl -X PUT http://localhost:5000/ticket_statuses/<status_ticket_id> \
    -H "Content-Type: application/json" \
    -d '{"description": "<status_ticket_description>"}'
"""
@ticket_status_bp.route('/ticket_statuses/<int:tic_status_id>', methods=['PUT'])
def update_ticket_status(tic_status_id):
    status = TicketStatus.query.get(tic_status_id)
    if not status:
        return jsonify({"Error": "Ticket Status not found"}), 404
    
    data = request.json
    if 'description' in data:
        status.description = data['description']
    db.session.commit()
    return jsonify(ticket_status_schema.dump(status)), 200


"""
-> DELETE ticket status
curl -X DELETE http://localhost:5000/ticket_statuses/<status_ticket_id>
"""
@ticket_status_bp.route('/ticket_statuses/<int:tic_status_id>', methods=['DELETE'])
def delete_ticket_status(tic_status_id):
    status = TicketStatus.query.get(tic_status_id)
    if not status:
        return jsonify({"Error": "Status not found"}), 404
    db.session.delete(status)
    db.session.commit()
    return jsonify({"Message": "Ticket status deleted"}), 200
