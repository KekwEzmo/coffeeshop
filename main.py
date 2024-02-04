from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from model.database import DBSession
from model import models
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import json
from datetime import datetime
from schema import CartItem
from typing import List

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
                amount=product.get('stock', 999),  # Initial stock amount
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
    
    # Get product information from db
    products = db.query(models.Product.name, models.Product.price, models.Product.description).all()
    products_data = [{"name": product.name, "description": product.description,"price": product.price} for product in products]

    db.close()
    return products_data


# API Endpoint to get current stock
@app.get('/api/stock')
async def checkout():
    db = DBSession()
    
    # Get product name and stock from db
    products = db.query(models.Product.name, models.Product.amount).all()
    products_data = [{"name": product.name, "amount": product.amount} for product in products]

    db.close()
    return products_data


# API Endpoint to generate a bill
@app.post('/api/checkout')
async def checkout(request: Request):
    # Parse JSON data from request body
    payload = await request.json()
    cart_items_data = payload.get('cartItems', [])

    # Validate cart items
    if not cart_items_data:
        raise HTTPException(status_code=400, detail="Cart items not provided")

    # Convert cart item data into CartItem objects
    cart_items = [CartItem(**item_data) for item_data in cart_items_data]

    db = DBSession()

    for item in cart_items:
        entry = db.query(models.Product).filter(models.Product.name == item.name).first()
        
        if entry:
            if entry.amount >= item.quantity:
                entry.amount = entry.amount - item.quantity
            else:
                raise HTTPException(status_code=403, detail="Not enough in stock!")

    db.commit()
    db.close()

    # Generate PDF
    pdf_output_file = "bill.pdf"
    generate_pdf(cart_items, pdf_output_file)

    return FileResponse(pdf_output_file, media_type="application/pdf", filename="bill.pdf")


# Function to generate a pdf file for the bill
def generate_pdf(cart_items: List[CartItem], output_file: str):
    doc = SimpleDocTemplate(output_file, pagesize=A4)

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = ParagraphStyle(name='Header', fontSize=12, textColor=colors.black, alignment=1) # Center alignment
    row_style = ParagraphStyle(name='Row', fontSize=10, textColor=colors.black)

    # Table Columns/Headers
    data = [["Name", "Price", "Quantity", "Subtotal"]]

    # Add Cart-items
    total_end_price = 0
    for item in cart_items:
        subtotal = item.price * item.quantity
        total_end_price += subtotal
        data.append([item.name, f"{item.price:.2f} €", str(item.quantity), f"{subtotal:.2f} €"])

    data.append(["Total End Price:", "", "", f"{total_end_price:.2f} €"])

    # initiate Table
    table = Table(data)

    # Table Design
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    title = Paragraph("Coffee-Bill", title_style)

    datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    datetime_paragraph = Paragraph(f"Date and Time: {datetime_str}", header_style)

    space = Spacer(1, 12)

    doc.build([title, Spacer(1, 36), datetime_paragraph, space, table]) 