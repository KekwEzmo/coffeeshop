from fastapi import FastAPI, HTTPException, Query
from model.database import DBSession
from model import models

app = FastAPI()

# Function to load stock into db on startup
def load_stock():
    try:
        db = DBSession()

        product_list = ['Verlängerter', 'Wiener Melange', 'Kleiner Brauner', 'Großer Brauner', 'Kapuziner', 'Franziskaner', 'Eiskaffee', 'Mokka']

        for product_name in product_list:
            # Check if the product with the same name already exists
            existing_product = db.query(models.Product).filter_by(name=product_name).first()
            if existing_product:
                continue  # Skip adding the product if it already exists
            
            # If the product doesn't exist, add it to the database
            new_product = models.Product( 
                name=product_name, amount=999999, price=5
            )
            db.add(new_product) # commit new product to db
        
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
    
    products = db.query(models.Product.name, models.Product.price).all()
    products_data = [{"name": product.name, "price": product.price} for product in products]

    db.close()
    return products_data
