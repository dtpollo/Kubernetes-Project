# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields, validate
from sqlalchemy import Column, Integer, String, ForeignKey
from event_app import Event
from ticket_status_app import TicketStatus

ticket_bp = Blueprint('ticket_bp', __name__)

# SQLAlchemy Model
class Ticket(db.Model):
    __tablename__ = 'ticket'
    tic_id = Column(Integer, primary_key=True)
    tic_type = Column(String(10), nullable=False)
    tic_status_id = Column(Integer, ForeignKey('ticket_status.tic_status_id', onupdate='CASCADE'), nullable=False)
    ev_id = Column(Integer, ForeignKey('event.ev_id', ondelete='CASCADE'), nullable=False)

# Marshmallow Schema
class TicketSchema(Schema):
    tic_id = fields.Int(dump_only=True)
    tic_type = fields.Str(
        required=True,
        validate=validate.OneOf(['VIP', 'General', 'Premium'])
    )
    tic_status_id = fields.Int(required=True)
    ev_id = fields.Int(required=True)

ticket_schema = TicketSchema()
tickets_schema = TicketSchema(many=True)

# Endpoints (CRUD)
"""
-> GET all tickets
curl http://localhost:5000/tickets
"""
@ticket_bp.route('/tickets', methods=['GET'])
def get_tickets():
    all_tickets = Ticket.query.all()
    if not all_tickets:
        return jsonify({"Error": "Tickets not found"}), 404
    return jsonify(tickets_schema.dump(all_tickets)), 200


"""
-> GET one ticket
# curl http://localhost:5000/tickets/<ticket_id>
"""
@ticket_bp.route('/tickets/<int:tic_id>', methods=['GET'])
def get_ticket(tic_id):
    ticket = Ticket.query.get(tic_id)
    if not ticket:
        return jsonify({"Error": "Ticket not found"}), 404
    return jsonify(ticket_schema.dump(ticket)), 200


"""
-> POST new ticket
curl -X POST http://localhost:5000/tickets \
    -H "Content-Type: application/json" \
    -d '{
            "tic_type": "<ticket_type>",
            "tic_status_id": <status_ticket>,
            "ev_id": <event_id>
        }'
"""
@ticket_bp.route('/tickets', methods=['POST'])
def add_ticket():
    data = request.json
    errors = ticket_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400
    
    if not Event.query.get(data['ev_id']):
        return jsonify({"Error": "Event not found"}), 404
    if not TicketStatus.query.get(data['tic_status_id']):
        return jsonify({"Error": "Ticket status not found"}), 404
    
    new_ticket = Ticket(
        tic_type=data['tic_type'],
        tic_status_id=data['tic_status_id'],
        ev_id=data['ev_id']
    )
    db.session.add(new_ticket)
    db.session.commit()
    return jsonify(ticket_schema.dump(new_ticket)), 201


"""
-> PUT update ticket status or type
curl -X PUT http://localhost:5000/tickets/<ticket_id> \
    -H "Content-Type: application/json" \
    -d '{"tic_type": "<ticket_type>"}'
"""
@ticket_bp.route('/tickets/<int:tic_id>', methods=['PUT'])
def update_ticket(tic_id):
    ticket = Ticket.query.get(tic_id)
    data = request.json
    errors = ticket_schema.validate(data, partial=True)

    if not ticket:
        return jsonify({"Error": "Ticket not found"}), 404
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400
    
    if 'tic_type' in data:
        ticket.tic_type = data['tic_type']
    if 'tic_status_id' in data:
        if not TicketStatus.query.get(data['tic_status_id']):
            return jsonify({"Error": "Ticket status not found"}), 404
        ticket.tic_status_id = data['tic_status_id']
        
    db.session.commit()
    return jsonify(ticket_schema.dump(ticket)), 200


"""
-> DELETE ticket
curl -X DELETE http://localhost:5000/tickets/<ticket_id>
"""
@ticket_bp.route('/tickets/<int:tic_id>', methods=['DELETE'])
def delete_ticket(tic_id):
    ticket = Ticket.query.get(tic_id)
    if not ticket:
        return jsonify({"Error": "Ticket not found"}), 404
    
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"Message": "Ticket deleted"}), 200