from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):

    __tablename__ = "products"

    name = Column(String(length=255), primary_key=True)
    description = Column(String(length=2000))
    amount = Column(Integer)
    price = Column(Float)

    def __repr__(self):
        return f'Product(name={self.name}, description={self.description}, amount={self.amount}, price={self.price})'