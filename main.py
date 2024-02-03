from fastapi import FastAPI, HTTPException, Query
from model.database import DBSession
from model import models
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow requests from any origin (you may want to restrict this in production)
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Allow the specified HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Function to load stock into db on startup
def load_stock():
    try:
        db = DBSession()

        # Load products from file
        with open('products.json', 'r') as file:
            products = json.load(file)

        # Loop through products
        for product in products:
            product_name = product['name']
            existing_product = db.query(models.Product).filter_by(name=product_name).first()
            if existing_product:
                continue  # Skip adding the product if it already exists
            
            # If the product doesn't exist, add it to the database
            new_product = models.Product(
                name=product_name, 
                description=product.get('description', ''),  # If no description, pass as empty
                amount=999999,  # Initial stock amount
                price=float(product.get('price', 10))  # Convert price to float
            )
            db.add(new_product)
        
        db.commit()
        db.close()
    except:
        return
    
# Load products into db
load_stock()

# API Endpoint for fetching products
@app.get('/api/products')
def products():
    db = DBSession()
    
    products = db.query(models.Product.name, models.Product.price, models.Product.description).all()
    products_data = [{"name": product.name, "description": product.description,"price": product.price} for product in products]

    db.close()
    return products_data

# API Endpoint to generate a bill
@app.get('/api/pay')
def pay():
    return