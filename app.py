import os

from flask import Flask, render_template, request, \
    redirect, url_for, jsonify, flash
from flask_dance.contrib.azure import make_azure_blueprint, azure
from flask_dance.contrib.github import make_github_blueprint, github
from flask_login import \
    LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from catalog_db_setup import Category, Base, Item, User

app = Flask(__name__)

engine = create_engine('sqlite:///item_catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# disable oauth2 https check
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app.secret_key = "supersekrit"
github_bp = make_github_blueprint(
    client_id="ff51fa522d0edcaa86c7",
    client_secret="01961dc18f0134f912bda65e6dd98f6ae5b07ef4",
    redirect_to="authorized_github"
)
app.register_blueprint(github_bp, url_prefix="/login")
azure_bp = make_azure_blueprint(
    client_id="0cd36578-7d2d-46ac-897a-d5edde683a7d",
    client_secret="wzTOHZ8391(ihinkJCI3~)^",
    redirect_to="authorized_azure"
)
app.register_blueprint(azure_bp, url_prefix="/login")


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
    return render_template("catalog/login.html")


@app.route("/authorized/github")
def authorized_github():
    """
    flask dance is configured to redirect here, if user is
    successfully authorized using github oauth2
    it will use the token to access user info, and login
    the corresponding user by it's email if find one, otherwise
    it will create a new user use info retrieved from github before login
    :return:
    """
    if github.authorized:
        resp = github.get("/user").json()
        user = get_user_by_email(resp["email"])
        if user is None:
            user = create_user(resp["name"], resp["email"])
        login_user(user)
        return redirect(url_for("catalog"))


@app.route("/authorized/azure")
def authorized_azure():
    if azure.authorized:
        resp = azure.get("/v1.0/me").json()
        name = resp["displayName"]
        email = resp["userPrincipalName"]
        user = get_user_by_email(email)
        if user is None:
            user = create_user(name, email)
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
    """
    catalog app home page, it will show all categories and latest items added
    :return:
    """
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(5).all()
    return render_template("catalog/index.html",
                           categories=categories, items=items)


@app.route("/catalog/<int:category_id>/")
@app.route("/catalog/<int:category_id>/items/")
def catalog_items_by_category_id(category_id):
    """
    catalog app home, showing a specific category item
    :param category_id:
    :return:
    """
    session = DBSession()
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template("catalog/index.html", categories=categories,
                           items=items, category=category)


@app.route("/catalog/items/new/", methods=["GET", "POST"])
@login_required
def catalog_item_new():
    """
    endpoint for get a view to create a new item and add item
    :return:
    """
    session = DBSession()
    if request.method == "POST":
        item = Item()
        if request.form['name']:
            item.name = request.form["name"]
        if request.form["detail"]:
            item.detail = request.form["detail"]
        if request.form["category_id"]:
            item.category_id = request.form["category_id"]
        item.owner_id = current_user.id
        session.add(item)
        session.commit()
        return redirect(url_for("catalog_item", id=item.id))
    else:
        categories = session.query(Category).all()
        return render_template("item/new.html", categories=categories)


@app.route("/catalog/items/<int:id>/")
def catalog_item(id):
    """
    view for individual item
    :param id: item_id of the item will be shown
    :return:
    """
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one_or_none()
    return render_template("item/index.html", item=item)


@app.route("/catalog/items/<int:id>/edit", methods=["GET", "POST"])
@login_required
def catalog_item_edit(id):
    """
    endpoint for a view to edit and update item
    :param id: item id to update
    :return:
    """
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one_or_none()
    print(item.owner_id, current_user.id)
    if item.owner_id != current_user.id:
        flash("You can only edit your own items!")
        return redirect(url_for("catalog_item", id=id))
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
        return render_template("item/edit.html", item=item,
                               categories=categories)


@app.route("/catalog/items/<int:id>/delete", methods=["GET", "POST"])
@login_required
def catalog_item_delete(id):
    """
    endpoint for a view of confirm delete of a item and delete item
    :param id: item id of the item want to delete
    :return:
    """
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one_or_none()
    if item.owner_id != current_user.id:
        flash("You can only delete your own items!")
        return redirect(url_for("catalog_item", id=id))
    if request.method == "POST":
        session.delete(item)
        session.commit()
        return redirect(url_for("catalog"))
    else:
        return render_template("item/delete.html", item=item)


@app.route("/api/v1/catalog/<int:category_id>/item")
def api_catalog_items_by_category_id(category_id):
    """
    json endpoint for obtains all items by it's category
    :param category_id:
    :return:
    """
    session = DBSession()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items=[item.serialize for item in items])


@app.route("/api/v1/catalog/items", methods=["GET", "POST"])
def api_items():
    """
    json endpoint for obtains all items, and create new item
    :return:
    """
    session = DBSession()
    if request.method == "GET":
        items = session.query(Item).all()
        return jsonify(items=[item.serialize for item in items])
    elif request.method == "POST":
        if current_user.is_authenticated:
            return login_manager.unauthorized()
        item = Item()
        item.name = request.args.get("name", "item name")
        item.detail = request.args.get("detail", "item detail")
        item.category_id = request.args.get("category_id", 0)
        category = session.query(Category) \
            .filter_by(id=item.category_id).one_or_none()
        if category is None:
            category = session.query(Category).one()
            item.category_id = category.id
        item.owner_id = current_user.id
        session.add(item)
        session.commit()


@app.route("/api/v1/catalog/items/<int:id>", methods=["GET", "PUT", "DELETE"])
def api_item(id):
    """
    json endpoint for get, update, delete an item
    :param id: item id of the item to operate
    :return:
    """
    session = DBSession()
    item = session.query(Item).filter_by(id=id).one()
    if request.method == "GET":
        return jsonify(item=item.serialize)
    elif request.method == "PUT":
        if current_user.is_authenticated:
            return login_manager.unauthorized()
        if item.owner_id != current_user.id:
            return "You can only edit your own items!"
        name = request.args.get("name")
        detail = request.args.get("detail")
        category_id = request.args.get("category_id")
        category = session.query(Category) \
            .filter_by(id=category_id).one_or_none()
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
        if current_user.is_authenticated:
            return login_manager.unauthorized()
        if item.owner_id != current_user.id:
            return "You can only delete your own items!"
        session.delete(item)
        session.commit()
        return "item deleted"


if __name__ == "__main__":
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
