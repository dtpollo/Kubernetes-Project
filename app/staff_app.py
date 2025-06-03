# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields
from sqlalchemy import Column, Integer, String, ForeignKey
from supplier_app import Supplier

staff_bp = Blueprint('staff_bp', __name__)

# SQLAlchemy Model
class Staff(db.Model):
    __tablename__ = 'staff'
    stf_id = Column(Integer, primary_key=True)
    stf_name = Column(String(100), nullable=False)
    stf_last_name = Column(String(100), nullable=False)
    stf_tasks = Column(String(100), nullable=False)
    stf_role = Column(String(100), nullable=False)
    sup_id = Column(Integer, ForeignKey('supplier.sup_id', ondelete='CASCADE'), nullable=False)

# Marshmallow Schema
class StaffSchema(Schema):
    stf_id = fields.Int(dump_only=True)
    stf_name = fields.Str(required=True)
    stf_last_name = fields.Str(required=True)
    stf_tasks = fields.Str(required=True)
    stf_role = fields.Str(required=True)
    sup_id = fields.Int(required=True)

staff_schema = StaffSchema()
staffs_schema = StaffSchema(many=True)

# Endpoints (CRUD)
"""
-> GET all staff
curl http://localhost:5000/staff
"""
@staff_bp.route('/staff', methods=['GET'])
def get_staff():
    all_staff = Staff.query.all()
    if not all_staff:
        return jsonify({"Error": "No staff found"}), 404
    return jsonify(staffs_schema.dump(all_staff)), 200


"""
-> GET one staff member
# curl http://localhost:5000/staff/<staff_member_id>
"""
@staff_bp.route('/staff/<int:stf_id>', methods=['GET'])
def get_one_staff(stf_id):
    staff = Staff.query.get(stf_id)
    if staff:
        return jsonify(staff_schema.dump(staff)), 200
    else:
        return jsonify({"Error": "Staff not found"}), 404

"""
-> POST: Assign a new staff member to a supplier
curl -X POST http://localhost:5000/staff \
    -H "Content-Type: application/json" \
    -d '{
            "stf_name": "<staff_member_name>",
            "stf_last_name": "<staff_member_last_name>",
            "stf_tasks": "<staff_member_task>",
            "stf_role": "<staff_member_role>",
            "sup_id": <supplier_id>
        }'
"""
@staff_bp.route('/staff', methods=['POST'])
def add_staff():
    data = request.json
    errors = staff_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "Details": errors}), 400

    if not Supplier.query.get(data['sup_id']):
        return jsonify({"Error": "Supplier not found"}), 404
    
    else:
        new_staff = Staff(**data)
        db.session.add(new_staff)
        db.session.commit()
        return jsonify(staff_schema.dump(new_staff)), 201


"""
-> PUT update the staff task
curl -X PUT http://localhost:5000/staff/<staff_member_id> \
    -H "Content-Type: application/json" \
    -d '{"stf_tasks": "<staff_member_task>"}'
"""

@staff_bp.route('/staff/<int:stf_id>', methods=['PUT'])
def update_staff(stf_id):
    staff = Staff.query.get(stf_id)
    data = request.json
    errors = staff_schema.validate(data, partial=True)
    
    if not staff:
        return jsonify({"Error": "Staff not found"}), 404
    if errors:
        return jsonify({"Error": "Invalid data", "Details": errors}), 400
    
    if 'stf_name' in data:
        staff.stf_name = data['stf_name']
    if 'stf_last_name' in data:
        staff.stf_last_name = data['stf_last_name']
    if 'stf_tasks' in data:
        staff.stf_tasks = data['stf_tasks']
    if 'stf_role' in data:
        staff.stf_role = data['stf_role']
    if 'sup_id' in data:
        if not Supplier.query.get(data['sup_id']):
            return jsonify({"Error": "Supplier not found"}), 404
        staff.sup_id = data['sup_id']
    db.session.commit()
    return jsonify(staff_schema.dump(staff)), 200


"""
-> DELETE staff
curl -X DELETE http://localhost:5000/staff/<staff_member_id>
"""
@staff_bp.route('/staff/<int:stf_id>', methods=['DELETE'])
def delete_staff(stf_id):
    staff = Staff.query.get(stf_id)
    if not staff:
        return jsonify({"Error": "Staff not found"}), 404
    
    db.session.delete(staff)
    db.session.commit()
    return jsonify({"Message": "Staff Member deleted"}), 200
