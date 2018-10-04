from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    items = relationship("Item", backref="category", order_by="Item.name")


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    detail = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))


def add_fake_data():
    dessert = Category(name="Dessert")
    dessert.items.append(Item(name="Cakes"))
    dessert.items.append(Item(name="Cookies"))
    dessert.items.append(Item(name="Pies"))
    session.add(dessert)

    noodles = Category(name="Noodles")
    noodles.items.append(Item(name="Fried Noodles"))
    noodles.items.append(Item(name="Instant Noodles"))
    noodles.items.append(Item(name="Ramen"))
    noodles.items.append(Item(name="Paomo"))
    session.add(noodles)

    session.commit()


if __name__ == "__main__":
    engine = create_engine('sqlite:///item_catalog.db')
    Base.metadata.create_all(engine)
    session = Session(engine)
    add_fake_data()
    print(session.query(Category).all())
