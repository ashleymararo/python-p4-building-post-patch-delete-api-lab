#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# --- BAKERIES ROUTES ---

@app.route('/bakeries', methods=['GET'])
def get_bakeries():
    bakeries = Bakery.query.all()
    # Returns a list of JSON objects for all bakeries
    return make_response(jsonify([b.to_dict() for b in bakeries]), 200)

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.filter_by(id=id).first()
    
    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    if request.method == 'GET':
        # Returns a single bakery with baked goods nested (handled by to_dict logic)
        return make_response(jsonify(bakery.to_dict()), 200)

    elif request.method == 'PATCH':
        # Updates the name of the bakery using form data
        for attr in request.form:
            setattr(bakery, attr, request.form.get(attr))
        
        db.session.add(bakery)
        db.session.commit()
        return make_response(jsonify(bakery.to_dict()), 200)

# --- BAKED GOODS ROUTES ---

@app.route('/baked_goods', methods=['POST'])
def post_baked_good():
    # Creates a new baked good from form data
    try:
        new_item = BakedGood(
            name=request.form.get('name'),
            price=float(request.form.get('price')),
            bakery_id=int(request.form.get('bakery_id'))
        )
        db.session.add(new_item)
        db.session.commit()
        return make_response(jsonify(new_item.to_dict()), 201)
    except Exception as e:
        return make_response(jsonify({"errors": [str(e)]}), 400)

@app.route('/baked_goods/by_price', methods=['GET'])
def get_baked_goods_by_price():
    # Returns list sorted by price descending
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    return make_response(jsonify([bg.to_dict() for bg in baked_goods]), 200)

@app.route('/baked_goods/most_expensive', methods=['GET'])
def get_most_expensive():
    # Returns the single most expensive baked good
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    return make_response(jsonify(most_expensive.to_dict()), 200)

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    # Deletes a baked good by ID
    item = BakedGood.query.filter_by(id=id).first()
    
    if not item:
        return make_response(jsonify({"error": "Baked good not found"}), 404)
    
    db.session.delete(item)
    db.session.commit()
    return make_response(jsonify({"message": "Record successfully deleted"}), 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)