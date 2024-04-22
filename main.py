import requests
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# #Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# #Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record

@app.route("/random")
def random_cafe():
    cafes = Cafe.query.all()
    cafe = random.choice(cafes)

    return jsonify(cafe.to_dict())
    # return jsonify(
    #     cafe={
    #         "can_take_calls": cafe.can_take_calls,
    #         "coffee_price": cafe.coffee_price,
    #         "has_sockets": cafe.has_sockets,
    #         "has_wifi": cafe.has_wifi,
    #         "has_toilet": cafe.has_toilet,
    #         "id": cafe.id,
    #         "location": cafe.location,
    #         "seats": cafe.seats,
    #         "img_url": cafe.img_url,
    #         "map_url": cafe.map_url,
    #         "name": cafe.name})


@app.route("/all")
def all_cafes():
    cafes = Cafe.query.all()
    list_of_dictionary_cafes = [cafe.to_dict() for cafe in cafes]
    print(list_of_dictionary_cafes)
    return jsonify(cafes=list_of_dictionary_cafes)


@app.route("/search")
def find_cafe():
    location = request.args.get('loc')
    cafes = Cafe.query.filter_by(location=location)
    cafes = [cafe.to_dict() for cafe in cafes]
    if cafes:
        return jsonify(cafe=cafes)
    else:
        return jsonify(error={
            "Not Found": "Sorry,we don't have a cafe at that location"
        })


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(name=request.form['name'],
                    map_url=request.form['map_url'],
                    img_url=request.form['img_url'],
                    location=request.form['location'],
                    seats=request.form['seats'],
                    has_toilet=request.form['has_toilet'],
                    has_wifi=request.form['has_wifi'],
                    has_sockets=request.form['has_sockets'],
                    can_take_calls=request.form[' can_take_calls'],
                    coffee_price=request.form['coffee_price'])
    db.session.add(new_cafe)
    db.session.commit()

    return jsonify(response={
        "success": "Successfully added a new cafe"
    })


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:id>", methods=["PATCH"])
def update_price(id):
    new_price = request.args.get('new-price')
    cafe_to_be_updated = Cafe.query.get(id)

    if cafe_to_be_updated:
        cafe_to_be_updated.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price")
    else:
        return jsonify(error={
            "Not Found": "Sorry a cafe with that id was not found in the database"
        }), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<int:id>")
def delete_cafe(id):
    cafe_to_be_deleted = Cafe.query.get(id)
    api_key = request.args.get('api_key')

    if cafe_to_be_deleted:
        if api_key == 'TopSecretAPIKey':
            db.session.delete(cafe_to_be_deleted)
            db.session.commit()
        else:
            return jsonify(error="Sorry,that's not allowed.Make sure you have the correct api_key."), 403

        return jsonify(success="The cafe has been successfully deleted")
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with  that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
