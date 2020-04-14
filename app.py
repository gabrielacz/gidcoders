from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Topping(db.Model):
    name = db.Column(db.String(200), nullable=False, primary_key=True)

    @classmethod
    def get_or_create(cls, name):
        entity = Topping.query.get(name)
        if entity:
            return entity
        return Topping.create(name)

    @classmethod
    def create(cls, name):
        entity = cls(
            name=name,
        )
        db.session.add(entity)
        db.session.commit()
        return entity


class PizzaTopping(db.Model):
    topping_id = db.Column('topping_id', db.Integer, db.ForeignKey('topping.name'), primary_key=True)
    pizza_id = db.Column('pizza_id', db.Integer, db.ForeignKey('pizza.name'), primary_key=True)
    amount = db.Column('amount', db.Float, default=1.0)

    @classmethod
    def get_or_create(cls, topping_id, pizza_id, amount=1.0):
        entity = PizzaTopping.query.get({'topping_id' : topping_id, 'pizza_id' : pizza_id})
        if entity:
            return entity
        return PizzaTopping.create(topping_id, pizza_id, amount=amount)

    @classmethod
    def create(cls, topping_id, pizza_id, amount=1.0):
        entity = cls(
            topping_id=topping_id,
            pizza_id=pizza_id,
            amount=amount
        )
        db.session.add(entity)
        db.session.commit()
        return entity

    def serialize(self):
        return {"topping": self.topping_id, "amount": self.amount}


class Pizza(db.Model):
    name = db.Column(db.String(200), nullable=False, primary_key=True)
    points = db.Column(db.Integer, default=0, nullable=False)

    def serialize(self):
        return {
            "name": self.name,
            "points": self.points,
            "toppings": [t.serialize() for t in self.toppings]
        }

    def vote(self):
        self.points += 1
        db.session.commit()
        return self

    @classmethod
    def get_or_create(cls, name, toppings=None):
        if not toppings: toppings = []
        entity = Pizza.query.get(name)  # TODO search by toppings
        if entity:
            return entity
        return Pizza.create(name, toppings)

    @classmethod
    def list(cls):
        return Pizza.query.all()

    @classmethod
    def create(cls, name, toppings=None):
        if not toppings: toppings = []
        topp = []
        for topping in toppings:
            PizzaTopping.get_or_create(topping_id=topping, pizza_id=name, amount=2.0)
        entity = cls(
            name=name,
            points=0,
        )
        entity.toppings.extend(topp)
        db.session.add(entity)
        db.session.commit()
        return entity


Pizza.toppings = relationship("PizzaTopping")


@app.route('/list/', methods=['GET'])
def list():
    return jsonify(pizzas=[p.serialize() for p in Pizza.list()])


@app.route('/vote/', methods=['POST'])
def vote():
    Pizza.get_or_create(request.json.get('name')).vote()
    return ('', 204)


@app.route('/start', methods=['GET'])
def startup():
    db.create_all(app=app)
    Pizza.create(name="Hawaii", toppings=['cheese', 'pinapple'])
    Pizza.create(name="Pepperoni", toppings=['cheese', 'pepperonni'])
    Pizza.create(name="Margaritta", toppings=['cheese'])
    return ('', 204)


if __name__ == "__main__":
    db.create_all(app=app)
    app.run(debug=True)
