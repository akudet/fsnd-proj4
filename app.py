from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_db_setup import Category, Base, Item

app = Flask(__name__)

engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route("/")
@app.route("/catalog/")
def catalog():
    categories = session.query(Category).all()
    items = session.query(Item).limit(5).all()
    return render_template("catalog/index.html",
                           categories=categories, items=items)


@app.route("/catalog/<int:category_id>/")
@app.route("/catalog/<int:category_id>/items/")
def catalog_items(category_id):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template("catalog/index.html",
                           categories=categories, items=items, category=category)


@app.route("/catalog/new/")
def catalog_item_new():
    return render_template("item/new.html")


@app.route("/catalog/<category_id>/items/<id>/")
def catalog_item(category_id, id):
    return render_template("item/index.html")


@app.route("/catalog/<int:catalog_id>/items/<int:item_id>/edit")
def catalog_item_edit(catalog_id, item_id):
    return render_template("item/edit.html")


@app.route("/catalog/<int:catalog_id>/items/<int:item_id>/delete")
def catalog_item_delete(catalog_id, item_id):
    return render_template("item/delete.html")


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
