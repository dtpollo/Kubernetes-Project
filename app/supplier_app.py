# Header
from flask import Blueprint, request, jsonify
from use_db import db
from marshmallow import Schema, fields, validate
from sqlalchemy import Column, Integer, String

supplier_bp = Blueprint('supplier_bp', __name__)

# SQLAlchemy Model
class Supplier(db.Model):
    __tablename__ = 'supplier'
    sup_id = Column(Integer, primary_key=True)
    sup_company_name = Column(String(100), nullable=False)
    sup_contact_number = Column(String(10), nullable=False)
    sup_service_type = Column(String(100), nullable=False)

# Marshmallow Schema
class SupplierSchema(Schema):
    sup_id = fields.Int(dump_only=True)
    sup_company_name = fields.Str(required=True)
    sup_contact_number = fields.Str(
        required=True,
        validate=validate.Regexp(
            r'^09[0-9]{8}$',
            error="Phone must start with 09 and have 10 digits"
        )
    )
    sup_service_type = fields.Str(required=True)


supplier_schema = SupplierSchema()
suppliers_schema = SupplierSchema(many=True)

# Endpoints (CRUD)
"""
-> GET all suppliers
curl http://localhost:5000/suppliers
"""
@supplier_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    all_suppliers = Supplier.query.all()
    if all_suppliers:
        return jsonify(suppliers_schema.dump(all_suppliers)), 200
    else:
        return jsonify({"Error": "Supplier not found"}), 404


"""
-> GET one supplier
# curl http://localhost:5000/suppliers/<supplier_id>
"""
@supplier_bp.route('/suppliers/<int:sup_id>', methods=['GET'])
def get_supplier(sup_id):
    supplier = Supplier.query.get(sup_id)
    if supplier: 
        return jsonify(supplier_schema.dump(supplier)), 200
    else:
        return jsonify({"Error": "Supplier not found"}), 404


"""
-> POST new supplier
curl -X POST http://localhost:5000/suppliers \
    -H "Content-Type: application/json" \
    -d '{
            "sup_company_name": "<supplier_name>", 
            "sup_contact_number": "<supplier_contact>",
            "sup_service_type": "<supplier_service>"
        }'
"""
@supplier_bp.route('/suppliers', methods=['POST'])
def add_supplier():
    data = request.json
    errors = supplier_schema.validate(data)
    if errors:
        return jsonify({"Error": "Invalid data", "Details": errors}), 400

    elif Supplier.query.filter_by(sup_company_name=data['sup_company_name']).first():
        return jsonify({"Error": "Company already exist"}), 409
    
    else:
        new_supplier = Supplier(
            sup_company_name=data['sup_company_name'],
            sup_contact_number=data['sup_contact_number'],
            sup_service_type=data['sup_service_type']
        )
        db.session.add(new_supplier)
        db.session.commit()
        return jsonify(supplier_schema.dump(new_supplier)), 201


"""
-> PUT update supplier info
curl -X PUT http://localhost:5000/suppliers/<supplier_id> \
    -H "Content-Type: application/json" \
    -d '{"sup_company_name": "<supplier_name>"}'
"""
@supplier_bp.route('/suppliers/<int:sup_id>', methods=['PUT'])
def update_supplier(sup_id):
    supplier = Supplier.query.get(sup_id)
    if not supplier:
        return jsonify({"Error": "Supplier not found"}), 404

    data = request.json
    errors = supplier_schema.validate(data, partial=True)

    if errors:
        return jsonify({"Error": "Invalid data", "Details": errors}), 400

    if 'sup_company_name' in data:
        supplier.sup_company_name = data['sup_company_name']

    if 'sup_contact_number' in data:
        supplier.sup_contact_number = data['sup_contact_number']

    if 'sup_service_type' in data:
        supplier.sup_service_type = data['sup_service_type']

    db.session.commit()
    return jsonify(supplier_schema.dump(supplier)), 200



"""
-> DELETE supplier
curl -X DELETE http://localhost:5000/suppliers/<supplier_id>
"""
@supplier_bp.route('/suppliers/<int:sup_id>', methods=['DELETE'])
def delete_supplier(sup_id):
    supplier = Supplier.query.get(sup_id)
    if not supplier:
        return jsonify({"Error": "Supplier not found"}), 404
    
    db.session.delete(supplier)
    db.session.commit()
    return jsonify({"Message": "Supplier deleted"}), 200
