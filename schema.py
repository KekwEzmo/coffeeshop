from pydantic import BaseModel

class CartItem(BaseModel):
    name: str
    price: float
    quantity: int