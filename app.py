from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
@app.route("/catalog/")
def catalog():
    return render_template("catalog/index.html")


@app.route("/catalog/<int:catalog_id>/")
@app.route("/catalog/<int:catalog_id>/items/")
def catalog_items(catalog_id):
    return render_template("catalog/index.html")


@app.route("/catalog/<int:catalog_id>/items/<int:item_id>/new")
def catalog_item_new(catalog_id, item_id):
    return render_template("item/new.html")


@app.route("/catalog/<int:catalog_id>/items/<int:item_id>/")
def catalog_item(catalog_id, item_id):
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
