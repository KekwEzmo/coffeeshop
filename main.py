from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from model.database import DBSession
from model import models
from fastapi.middleware.cors import CORSMiddleware
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import json, uuid
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

sessions = {}

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
async def products():
    db = DBSession()
    
    # Get product information from db
    products = db.query(models.Product.name, models.Product.price, models.Product.description).all()
    products_data = [{"name": product.name, "description": product.description,"price": product.price} for product in products]

    db.close()
    return products_data

@app.delete('/api/products')
async def remove_product(request: Request):
    cookie = request.cookies.get("SID")

@app.post('/api/products')
async def add_product(request: Request):
    cookie = request.cookies.get("SID")

    if cookie:
        payload = await request.json()
        product_name = payload.get('name')
        product_price = payload.get('price')
        product_quantity = payload.get('quantity')

        if product_price * product_quantity < sessions[cookie]['credits'] - sessions[cookie]['basket_value']:
            sessions[cookie]['basket_value'] += product_price * product_quantity
            
            if product_name not in sessions[cookie]['products']:
                sessions[cookie]['products'][product_name] = {
                    "name": product_name,
                    "quantity": 0,
                    "price": product_price
                }

            sessions[cookie]['products'][product_name]["quantity"] += product_quantity

            return {"message": "Product added to shopping basket"}

        else:
            return {"message": 'you are too poor!!!!!!!!!!!!!!!!!!!!!!!!!!!!'}
    else:
        return {"message": "Cookie not found"}


# API Endpoint to get current stock
@app.get('/api/stock')
async def checkout():
    db = DBSession()
    
    # Get product name and stock from db
    products = db.query(models.Product.name, models.Product.amount).all()
    products_data = [{"name": product.name, "amount": product.amount} for product in products]

    db.close()
    return products_data


@app.get('/api/session')
async def session(response: Response):
    cookie = str(uuid.uuid4())
    sessions[cookie] = {}
    sessions[cookie]['credits'] = 50
    sessions[cookie]['basket_value'] = 0
    sessions[cookie]['products'] = {}
    response.set_cookie(key='SID', value=cookie)

    return { 'cookie': cookie, 'message': 'Cookie returned!' }

@app.get('/api/shopping_basket')
async def shopping_basket(request: Request):
    cookie = request.cookies.get("SID")

    return [{ "name": sessions[cookie]['products'][product]['name'], "quantity": sessions[cookie]['products'][product]['quantity'], "price": sessions[cookie]['products'][product]['price']} for product in sessions[cookie]['products']]

@app.get('/api/credits')
async def creds(request: Request):
    cookie = request.cookies.get("SID")

    return { "credits": sessions[cookie]['credits'] }

# API Endpoint to generate a bill
@app.post('/api/checkout')
async def checkout(request: Request):
    cookie = request.cookies.get("SID")

    # Convert cart item data into CartItem objects
    cart_items = [{ "name": sessions[cookie]['products'][product]['name'], "amount": sessions[cookie]['products'][product]['quantity'], "price": sessions[cookie]['products'][product]['price']} for product in sessions[cookie]['products']]

    db = DBSession()

    for item in cart_items:
        entry = db.query(models.Product).filter(models.Product.name == item['name']).first()
        
        if entry:
            if entry.amount >= item['amount']:
                entry.amount = entry.amount - item['amount']
            else:
                raise HTTPException(status_code=403, detail="Not enough in stock!")

    db.commit()
    db.close()

    # Generate PDF
    pdf_output_file = "bill.pdf"
    generate_pdf(cart_items, pdf_output_file)

    sessions[cookie]['products'] = {}
    sessions[cookie]['credits'] = sessions[cookie]['credits'] - sessions[cookie]['basket_value']
    sessions[cookie]['basket_value'] = 0

    return FileResponse(pdf_output_file, media_type="application/pdf", filename="bill.pdf")


# Function to generate a pdf file for the bill
def generate_pdf(cart_items: List[CartItem], output_file: str):
    doc = SimpleDocTemplate(output_file, pagesize=A4)

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    header_style = ParagraphStyle(name='Header', fontSize=12, textColor=colors.black, alignment=1) # Center alignment

    # Table Columns/Headers
    data = [["Name", "Price", "Quantity", "Subtotal"]]

    # Add Cart-items
    total_end_price = 0
    for item in cart_items:
        subtotal = item['price'] * item['amount']
        total_end_price += subtotal
        data.append([item['name'], f"{item['price']:.2f} €", str(item['amount']), f"{subtotal:.2f} €"])

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

