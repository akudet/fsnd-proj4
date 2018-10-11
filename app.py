import os

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from catalog_db_setup import Category, Base, Item, User

app = Flask(__name__)

engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

login_manager = LoginManager()
login_manager.init_app(app)

# disable oauth2 https check
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app.secret_key = "supersekrit"
blueprint = make_github_blueprint(
    client_id="ff51fa522d0edcaa86c7",
    client_secret="01961dc18f0134f912bda65e6dd98f6ae5b07ef4",
    redirect_to="login_github"
)
app.register_blueprint(blueprint, url_prefix="/login")


@login_manager.user_loader
def get_user_by_id(user_id):
    session = DBSession()
    return session.query(User).filter_by(id=int(user_id)).one_or_none()


def get_user_by_email(email):
    session = DBSession()
    return session.query(User).filter_by(email=email).one_or_none()


def create_user(name, email):
    session = DBSession()
    user = User()
    user.name = name
    user.email = email
    session.add(user)
    session.commit()
    return user


@app.route("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("catalog"))
    # use github by default
    return redirect(url_for("github.login"))


@app.route("/authorized/github")
def login_github():
    if github.authorized:
        resp = github.get("/user").json()
        user = get_user_by_email(resp["email"])
        if user is None:
            user = create_user(resp["name"], resp["email"])
        login_user(user)
        return redirect(url_for("catalog"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("catalog"))


@app.route("/")
@app.route("/catalog/")
def catalog():
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(5).all()
    return render_template("catalog/index.html",
                           categories=categories, items=items)


@app.route("/catalog/<int:category_id>/")
@app.route("/catalog/<int:category_id>/items/")
def catalog_items_by_category_id(category_id):
    session = DBSession()
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template("catalog/index.html",
                           categories=categories, items=items, category=category)


@app.route("/catalog/items/new/", methods=["GET", "POST"])
def catalog_item_new():
    session = DBSession()
    if request.method == "POST":
        item = Item()
        if request.form['name']:
            item.name = request.form["name"]
        if request.form["detail"]:
            item.detail = request.form["detail"]
        if request.form["category_id"]:
            item.category_id = request.form["category_id"]
        session.add(item)
        session.commit()
        return redirect(url_for("catalog_item", id=item.id))
    else:
        categories = session.query(Category).all()
        return render_template("item/new.html", categories=categories)


@app.route("/catalog/items/<int:id>/")
def catalog_item(id):
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one_or_none()
    return render_template("item/index.html", item=item)


@app.route("/catalog/items/<int:id>/edit", methods=["GET", "POST"])
def catalog_item_edit(id):
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one_or_none()
    if request.method == "POST":
        if request.form['name']:
            item.name = request.form["name"]
        if request.form["detail"]:
            item.detail = request.form["detail"]
        if request.form["category_id"]:
            item.category_id = request.form["category_id"]
        session.add(item)
        session.commit()
        return redirect(url_for("catalog_item", id=item.id))
    else:
        categories = session.query(Category).all()
        return render_template("item/edit.html", item=item, categories=categories)


@app.route("/catalog/items/<int:id>/delete", methods=["GET", "POST"])
def catalog_item_delete(id):
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one_or_none()
    if request.method == "POST":
        session.delete(item)
        session.commit()
        return redirect(url_for("catalog"))
    else:
        return render_template("item/delete.html", item=item)


@app.route("/api/v1/catalog/<int:category_id>/item")
def api_catalog_items_by_category_id(category_id):
    session = DBSession()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items=[item.serialize for item in items])


@app.route("/api/v1/catalog/items", methods=["GET", "POST"])
def api_items():
    session = DBSession()
    if request.method == "GET":
        items = session.query(Item).all()
        return jsonify(items=[item.serialize for item in items])
    elif request.method == "POST":
        item = Item()
        item.name = request.args.get("name", "item name")
        item.detail = request.args.get("detail", "item detail")
        item.category_id = request.args.get("category_id", 0)
        category = session.query(Category).filter_by(id=item.category_id).one_or_none()
        if category is None:
            category = session.query(Category).one()
            item.category_id = category.id
        session.add(item)
        session.commit()


@app.route("/api/v1/catalog/items/<int:id>", methods=["GET", "PUT", "DELETE"])
def api_item(id):
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one()
    if request.method == "GET":
        return jsonify(item=item.serialize)
    elif request.method == "PUT":
        name = request.args.get("name")
        detail = request.args.get("detail")
        category_id = request.args.get("category_id")
        category = session.query(Category).filter_by(id=category_id).one_or_none()
        if name:
            item.name = name
        if detail:
            item.detail = detail
        if category:
            item.category_id = category_id
        session.add(item)
        session.commit()
        return jsonify(item=item.serialize)
    elif request.method == "DELETE":
        session.delete(item)
        session.commit()
        return "item deleted"


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
