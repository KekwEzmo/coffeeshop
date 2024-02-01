from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    amount = Column(Integer)
    price = Column(Integer)

    def __repr__(self):
        return f'Product(id={self.id}, title={self.name}, amount={self.amount}, price={self.price})'