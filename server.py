import os 

from flask import Flask, request, jsonify
from sqlite3 import Connection as Conn
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from datetime import datetime


import linked_list
import hash_table


postgres_database = os.environ.get("POSTGRES_DATABASE")
sqlalchemy_uri = f"postgresql://{postgres_database}"

admin_username = os.environ.get("API_ADMIN_USERNAME")
admin_password = os.environ.get("API_ADMIN_PASSWORD")

# app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_uri 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = 0


# sqlite3 to enforce foreign key constrains
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, Conn):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


db = SQLAlchemy(app)
timestamp = datetime.now()


def authenticate(admin, password):
    if admin == admin_username and password == admin_password:
        return True
    return False


def admin_required(fn):
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if not auth or not authenticate(auth.username, auth.password):
            return jsonify({"message": "Authentication failed"}), 401
        return fn(*args, **kwargs)

    return wrapper


# mods
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
    isVegetarian = db.Column(db.Boolean, default=False)
    date = db.Column(db.Date)
    cuisine_id = db.Column(
        db.Integer, db.ForeignKey("cuisine.id"), nullable=False
    )


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
#    db.create_all()

if __name__ == "__main__":
    app.run()#(debug=0)
