from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Pizza(db.Model):
    name = db.Column(db.String(200), nullable=False, primary_key=True)
    points = db.Column(db.Integer, default=0, nullable=False)

    def serialize(self):
        return {
            "name": self.name,
            "points": self.points
        }

    def vote(self):
        self.points += 1
        db.session.commit()
        return self

    @classmethod
    def get_or_create(cls, name):
        entity = Pizza.query.get(name)
        if entity:
            return entity
        return Pizza.create(name)

    @classmethod
    def list(cls):
        return Pizza.query.all()

    @classmethod
    def create(cls, name):
        entity = cls(
            name=name,
            points=0
        )
        db.session.add(entity)
        return entity


@app.route('/list/', methods=['GET'])
def list():

    return jsonify(pizzas=[p.serialize() for p in Pizza.list()])


@app.route('/vote/', methods=['POST'])
def vote():
    Pizza.get_or_create(request.json.get('name')).vote()
    return ('', 204)


def startup():
    db.create_all(app=app)
    Pizza.create(name="Hawaii")
    Pizza.create(name="Pepperoni")
    Pizza.create(name="Margaritta")


if __name__ == "__main__":
    startup()
    app.run(debug=True)
