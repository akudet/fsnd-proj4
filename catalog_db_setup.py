from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    items = relationship("Item", backref="category", order_by="Item.name")

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    detail = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    owner_id = Column(Integer, ForeignKey("user.id"))
    owner = relationship("User", )

    @property
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "detail": self.detail,
        }


def add_fake_data():
    admin = User()
    admin.name = "Administrator"
    admin.email = "admin@localhost"
    session.add(admin)

    dessert = Category(name="Dessert")
    dessert.items.append(Item(name="Cakes", owner=admin))
    dessert.items.append(Item(name="Cookies", owner=admin))
    dessert.items.append(Item(name="Pies", owner=admin))
    session.add(dessert)

    noodles = Category(name="Noodles")
    noodles.items.append(Item(name="Fried Noodles", owner=admin))
    noodles.items.append(Item(name="Instant Noodles", owner=admin))
    noodles.items.append(Item(name="Ramen", owner=admin))
    noodles.items.append(Item(name="Paomo", owner=admin))
    session.add(noodles)

    session.commit()


if __name__ == "__main__":
    engine = create_engine('sqlite:///item_catalog.db')
    Base.metadata.create_all(engine)
    session = Session(engine)
    add_fake_data()
    print(session.query(Category).all())
