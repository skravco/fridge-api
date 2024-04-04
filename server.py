from flask import Flask, request, jsonify
from sqlite3 import Connection as Conn
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine import Engine
from sqlalchemy import event
from datetime import datetime

import linked_list

# app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///model.db"
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


# mods
class Cuisine(db.Model):
    __tablename__ = "cuisine"
    id = db.Column(db.Integer, primary_key=True)
    origins = db.Column(db.String(50))
    features = db.Column(db.String(150))
    allergens = db.Column(db.String(125))


class Recipe(db.Model):
    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    mealtime = db.Column(db.String(50))
    ingredients = db.Column(db.String(500))
    description = db.Column(db.String(500))
    date = db.Column(db.Date)
    cuisine_id = db.Column(db.Integer, db.ForeignKey("cuisine.id"), nullable=False)


@app.route("/cuisine", methods=["POST"])
def add_cuisine():
    data = request.get_json()
    c = Cuisine(
        origins=data["origins"], features=data["features"], allergens=data["allergens"]
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
def fetch_cuisine(cuisine_id):
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


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=0)
