import os

from flask import Flask, request, jsonify
from sqlite3 import Connection as Conn
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from datetime import datetime

#from credentials import ADMIN_USERNAME, ADMIN_PASSWORDSE

import linked_list
import hash_table

#  init flask app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] =  os.environ.get("DATABASE_URL")
# postgres://open_fridge_api_user:e6V0sp7Scx6dWwBSR7dTMYzVSgGdxVPa@dpg-coaflbv79t8c73ehaidg-a.frankfurt-postgres.render.com/open_fridge_api
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = 0

# init sqlalchemy
db = SQLAlchemy(app)
timestamp = datetime.now()

# authenticate admin
def authenticate(admin, password):
    if admin == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        return True
    return False

# decorator | require admin authentication
def admin_required(fn):
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate(auth.username, auth.password):
            return jsonify({"message": "Authentication failed"}), 401
        return fn(*args, **kwargs)

    return wrapper


# define db models
class Cuisine(db.Model):
    __tablename__ = "cuisine"
    id = db.Column(db.Integer, primary_key=True)
    origins = db.Column(db.String(25))
    features = db.Column(db.String(125))
    allergens = db.Column(db.String(125))


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    mealtime = db.Column(db.String(50))
    ingredients = db.Column(db.String(250))
    source = db.Column(db.String(125))
    isVegetarian = db.Column(db.Boolean(False))
    date = db.Column(db.Date)
    cuisine_id = db.Column(
        db.Integer, db.ForeignKey("cuisine.id"), nullable=False
    )

# routes
@app.route("/admin/cuisine", methods=["POST"], endpoint="add_cuisine")
@admin_required
def add_cuisine():
    data = request.get_json()
    c = Cuisine(
        origins=data["origins"],
        features=data["features"],
        allergens=data["allergens"],
    )
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "cuisine added!"}), 200


@app.route("/cuisine/desc", methods=["GET"])
def retrieve_cuisines_desc():
    all_cuisines = Cuisine.query.all()
    ll = linked_list.LinkedList()

    for cuisine in all_cuisines:
        ll.insert_head(
            {
                "id": cuisine.id,
                "origins": cuisine.origins,
                "features": cuisine.features,
                "allergens": cuisine.allergens,
            }
        )
    return jsonify(ll.to_list()), 200


@app.route("/cuisine/asc", methods=["GET"])
def retrieve_cuisines_asc():
    all_cuisines = Cuisine.query.all()
    ll = linked_list.LinkedList()

    for cuisine in all_cuisines:
        ll.insert_tail(
            {
                "id": cuisine.id,
                "origins": cuisine.origins,
                "features": cuisine.features,
                "allergens": cuisine.allergens,
            }
        )
    return jsonify(ll.to_list()), 200


@app.route("/cuisine/<cuisine_id>", methods=["GET"])
def find_cuisine(cuisine_id):
    all_cuisines = Cuisine.query.all()
    ll = linked_list.LinkedList()

    for cuisine in all_cuisines:
        ll.insert_head(
            {
                "id": cuisine.id,
                "origins": cuisine.origins,
                "features": cuisine.features,
                "allergens": cuisine.allergens,
            }
        )

    cuisine = ll.get_single_node(cuisine_id)
    return jsonify(cuisine), 200


@app.route(
    "/admin/recipe/<cuisine_id>", methods=["POST"], endpoint="add_new_recipe"
)
@admin_required
def add_new_recipe(cuisine_id):
    data = request.get_json()

    cuisine = Cuisine.query.filter_by(id=cuisine_id).first()
    if not cuisine:
        return jsonify({"message": "cuisine does not exist."}), 400

    ht = hash_table.HashTable(10)

    ht.add_key_value("name", data["name"])
    ht.add_key_value("mealtime", data["mealtime"])
    ht.add_key_value("ingredients", data["ingredients"])
    ht.add_key_value("source", data["source"])
    ht.add_key_value("isVegetarian", data.get("isVegetarian", False))
    ht.add_key_value("date", timestamp)
    ht.add_key_value("cuisine_id", data["cuisine_id"])

    new_recipe = Recipe(
        name=ht.get_value("name"),
        mealtime=ht.get_value("mealtime"),
        ingredients=ht.get_value("ingredients"),
        description=ht.get_value("description"),
        isVegetarian=ht.get_value("isVegetarian"),
        date=ht.get_value("date"),
        cuisine_id=ht.get_value("cuisine_id"),
    )

    db.session.add(new_recipe)
    db.session.commit()
    return jsonify({"message": "new recipe added."})


#with app.app_context():
#   db.create_all()

if __name__ == "__main__":
    app.run(debug=0)
