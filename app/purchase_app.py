# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields, validate
from sqlalchemy import Column, Integer, String, Date
from attendee_app import Attendee
from ticket_app import Ticket

purchase_bp = Blueprint('purchase_bp', __name__)

# SQLAlchemy Model
class Purchase(db.Model):
    __tablename__ = 'purchase'
    __table_args__ = (db.PrimaryKeyConstraint('att_id', 'tic_id'),)


    att_id = Column(Integer, primary_key=True)
    tic_id = Column(Integer, primary_key=True)
    purchase_date = Column(Date, nullable=False)
    purchase_type = Column(String(20), nullable=False)

# Marshmallow Schema
class PurchaseSchema(Schema):
    att_id = fields.Int(required=True)
    tic_id = fields.Int(required=True)
    purchase_date = fields.Date(required=True)
    purchase_type = fields.Str(
        required=True,
        validate=validate.OneOf(["Online", "Mobile App", "Box Office"])
    )

purchase_schema = PurchaseSchema()
purchases_schema = PurchaseSchema(many=True)

#Endpoints (CRUD)
"""
-> GET all purchases
curl http://localhost:5000/purchases
"""
@purchase_bp.route('/purchases', methods=['GET'])
def get_purchases():
    all_purchases = Purchase.query.all()
    if not all_purchases:
        return jsonify({"Error": "Purchases not found"}), 404
    return jsonify(purchases_schema.dump(all_purchases)), 200


"""
-> GET single purchase
curl http://localhost:5000/purchases/<attendee_id>/<ticket_id>
"""
@purchase_bp.route('/purchases/<int:att_id>/<int:tic_id>', methods=['GET'])
def get_purchase(att_id, tic_id):
    purchase = Purchase.query.get((att_id, tic_id))
    if not purchase:
        return jsonify({"Error": "Purchase not found"}), 404
    return jsonify(purchase_schema.dump(purchase)), 200


"""
First we should create the ticket
-> POST new purchase
curl -X POST http://localhost:5000/purchases \
    -H "Content-Type: application/json" \
    -d '{
            "att_id": <attendee_id>,
            "tic_id": <ticket_id>,
            "purchase_date": "year-month-day>",
            "purchase_type": "<type_of_purchase>"
        }'
"""
@purchase_bp.route('/purchases', methods=['POST'])
def add_purchase():
    data = request.json
    errors = purchase_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400
    
    existing = Purchase.query.get((data['att_id'], data['tic_id']))
    if existing:
        return jsonify({"Error": "Purchase already exists"}), 409

    if not Attendee.query.get(data['att_id']):
        return jsonify({"Error": "Attendee not found"}), 404
    if not Ticket.query.get(data['tic_id']):
        return jsonify({"Error": "Ticket not found"}), 404

    new_purchase = Purchase(
        att_id=data['att_id'],
        tic_id=data['tic_id'],
        purchase_date=data['purchase_date'],
        purchase_type=data['purchase_type']
    )
    db.session.add(new_purchase)
    db.session.commit()
    return jsonify(purchase_schema.dump(new_purchase)), 201


"""
-> PUT update purchase
curl -X PUT http://localhost:5000/purchases/<attendee_id>/<ticket_id> \
    -H "Content-Type: application/json" \
    -d '{"purchase_type": "<type_of_purchase>"}'
"""
@purchase_bp.route('/purchases/<int:att_id>/<int:tic_id>', methods=['PUT'])
def update_purchase(att_id, tic_id):
    purchase = Purchase.query.get((att_id, tic_id))
    if not purchase:
        return jsonify({"Error": "Purchase not found"}), 404
    
    data = request.json
    errors = purchase_schema.validate(data, partial=True)
    if errors:
        return jsonify({"Error": "Invalid data", "details": errors}), 400
    
    if 'purchase_date' in data:
        purchase.purchase_date = data['purchase_date']
    if 'purchase_type' in data:
        purchase.purchase_type = data['purchase_type']
    db.session.commit()
    return jsonify(purchase_schema.dump(purchase)), 200


"""
-> DELETE purchase
curl -X DELETE http://localhost:5000/purchases/<attendee_id>/<ticket_id>
"""
@purchase_bp.route('/purchases/<int:att_id>/<int:tic_id>', methods=['DELETE'])
def delete_purchase(att_id, tic_id):
    purchase = Purchase.query.get((att_id, tic_id))
    if not purchase:
        return jsonify({"Error": "Purchase not found"}), 404
    
    db.session.delete(purchase)
    db.session.commit()
    return jsonify({"Message": "Purchase deleted"}), 200
