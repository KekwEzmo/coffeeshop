# CoffeeShop

> [!NOTE]
> This containerized application encapsulates a cozy coffee shop.

## Documentation

The application consists of 3 different containers. <br/>
```yml
version: '3.9'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile_Backend
    restart: always
    hostname: fastapi
    environment:
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PW: ${DB_PW}
  
  frontend:
    build: 
      context: ./coffee-shop
      dockerfile: Dockerfile_Frontend
    restart: always
    command: sh -c "sleep 5 && nginx -g 'daemon off;'"
    ports:
      - "80:80"
  
  db:
    image: mariadb:latest
    hostname: db
    restart: always
    environment:
      MARIADB_ROOT_PASSWORD: 2U3Qps4cDZHJJT8LgnJR
      MARIADB_DATABASE: ${DB_NAME}
      MARIADB_USER: ${DB_USER}
      MARIADB_PASSWORD: ${DB_PW}
```

In the `docker-compose.yml` file I defined the three different containers. <br/>
- `DB` - Database to store products, and information about them such as `name`, `price`, `description`, `amount`. For this purpose I used `MariaDB`.
- `Backend` - Backend to act as interface between frontend and the rest of the application, built with `FastAPI`.
- `Frontend` - Frontend container to act as proxy for docker network and UI for user interaction, built with `REACT`.

### Backend

For this container I simply used the latest python docker image and installed the needed dependencies. <br/>
```txt
fastapi==0.109.0
sqlalchemy==2.0.21
uvicorn==0.23.2
pymysql==1.1.0
reportlab==4.0.0
pydantic==2.6.0
typing==3.7.4.3
```

Connection to database with `SQL-Alchemy`, the credentials are read from env-vars whic hare being passed during docker build. <br/>
```py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PW")
db_name = os.environ.get("DB_NAME")

SQLALCHEMY_DB_URL = f'mysql+pymysql://{db_user}:{db_password}@db:3306/{db_name}'

engine = create_engine(SQLALCHEMY_DB_URL, echo=True)
DBSession = sessionmaker(engine, autoflush=False)
```

Database table initiated with `SQL-Alchemy` on startup to store current products. <br/>
```py
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
```

On container startup I loaded a `json` file to get the products and their properties. <br/>
```py
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
```

The `products.json` looks like the `json` snippet below. <br/>
```json
[
	{
		"name": "Verlängerter",
		"description": "A long black coffee made by adding hot water to espresso.",
		"price": 5.50,
		"stock": 999
	},
	{
		"name": "Wiener Melange",
		"description": "A Viennese specialty coffee similar to a cappuccino, topped with whipped cream and cocoa powder.",
		"price": 6.30,
		"stock": 370
	},
	{
		"name": "Kleiner Brauner",
		"description": "A small black coffee served with a small amount of milk or cream.",
		"price": 5.40,
		"stock": 288
	}
]
```

The API endpoint `/api/products` fetches the products straight from the database. <br/>
```py
@app.get('/api/products')
def products():
    db = DBSession()
    
    # Get product information from db
    products = db.query(models.Product.name, models.Product.price, models.Product.description).all()
    products_data = [{"name": product.name, "description": product.description,"price": product.price} for product in products]

    db.close()
    return products_data
```

The API endpoint `/api/stock` fetches the products and how many are still in stock. <br/>
```py
@app.get('/api/stock')
async def checkout():
    db = DBSession()
    
    # Get product name and stock from db
    products = db.query(models.Product.name, models.Product.amount).all()
    products_data = [{"name": product.name, "amount": product.amount} for product in products]

    db.close()
    return products_data
```

The API endpoint `/api/checkout` takes the products the user chose and checks if there are enough products available. If that is the case it creates a bill in `PDF` format and passes it in the response. <br/>
```py
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
```

The function `generate_pdf()` leverages the library `reportlab` to convert the products and their properties to an actual bill in table format. <br/>
```py
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
```

### Frontend

For this container I used a `node.js` docker image to host the `REACT` app and nginx proxy. <br/>
```docker
FROM node:14 as build-stage

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

RUN npm run build

FROM nginx:latest

COPY nginx.conf /etc/nginx/conf.d/default.conf

COPY --from=build-stage /app/build /usr/share/nginx/html

CMD ["nginx", "-g", "daemon off;"]
```

The `nginx.conf` below acts as a proxy and redirects every request sent to `/api` to the backend container, every other request is being redirected to the local `REACT` app. <br/>
```conf
server {
    listen       80;
    listen  [::]:80;
    server_name  localhost;

    location / {
        root   /usr/share/nginx/html;
        index  index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://fastapi:5000;
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
```

In the `REACT` app I used `Routes` from the library `react-router-dom` to expose the webpages. <br/>
```js
import './App.css';
import { Route, Routes } from "react-router-dom";
import NavBar from './navBar';
import Footer from './footer';
import Home from './subpages/home';
import CheckOut from './subpages/checkout';
import { CartProvider } from './cart';
import Overview from './subpages/overview';

function App() {
  return (
    <div className="App">
      <CartProvider>
      <NavBar />
      <Routes>
        <Route exact path="/" element={<Home/>} />
        <Route exact path="/checkout" element={<CheckOut/>} />
        <Route exact path="/overview" element={<Overview/>} />
      </Routes>
      <Footer />
      </CartProvider> 
    </div>
  );
}

export default App;
```

In the homepage I fetch the products from the backend and display those on the website with a `responsive` design using display `flex`. <br/>
```js
import "./home.css";
import coffeeImg from '../assets/coffee1.avif'; 
import React, { useState, useEffect } from 'react';
import { useCart } from '../cart';

function Home() {

    const { addToCart } = useCart();
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [quantity, setQuantity] = useState(1);
  
    useEffect(() => {
      fetch('/api/products')
        .then(response => response.json())
        .then(data => setProducts(data))
        .catch(error => console.error('Error fetching products:', error));
    }, []);
  
    const addToBasket = () => {
        if (quantity <= 0 && quantity > 100) {
          alert('Please enter a valid quantity.');
          return;
        }

        setQuantity(1);
        addToCart({ name: selectedProduct.name, price: selectedProduct.price, quantity: quantity });
      };

    return(
        <>
        <div className="mainsection">
        <div className="product-container">
        {products.map(product => (
          <div key={product.name} className="product-box">
            <div className="upperHalf">
                <h3>{product.name}</h3>
                <p>Price: {product.price}0€</p>
            </div>
            <div className="lowerHalf" style={{backgroundImage: `url(${coffeeImg})`}}>
                <button className="popup-button" onClick={() => setSelectedProduct(product)}>Inspect</button>
            </div>
          </div>
        ))}
      </div>
      {selectedProduct && (
        <div className="popup">
          <div className="popup-content">
            <h2>{selectedProduct.name}</h2>
            <p>{selectedProduct.description}</p>
            <p>Price: {selectedProduct.price}0€</p>
            <input
              type="number"
              value={quantity}
              onChange={e => setQuantity(Math.max(1, parseInt(e.target.value)))} // Ensure minimum value is 1
            />
            <button onClick={addToBasket}>Add to Basket</button>
            <button onClick={() => setSelectedProduct(null)}>Close</button>
          </div>
        </div>
      )}
        </div>
        </>
    )
}
  
export default Home;
```

Rendering that looks like this.
![grafik](https://github.com/Aryt3/coffeeshop/assets/110562298/12623695-2601-42c7-b6d8-2f1e6a019bb8)

Inspecting a product opens a popup which lets you add a certain amount of the product to your `shopping-cart`.
![grafik](https://github.com/Aryt3/coffeeshop/assets/110562298/81250338-d0f1-42b5-9d13-8b70b0b8b0b2)

Navigating to `/checkout` lets you see your current content of the `shopping-cart`.
```js
import "./checkout.css";
import { useCart } from '../cart';
import { saveAs } from 'file-saver';

function CheckOut() {
    const { cartItems } = useCart();

    // Calculate total end price
    const totalEndPrice = cartItems.reduce((total, item) => total + (item.quantity * item.price), 0);

    const handleCheckout = () => {
        fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ cartItems }), // send cartItems array as JSON string
        })
        .then(response => response.blob())
        .then(blob => {
            // Save the blob as a file using FileSaver.js
            saveAs(blob, 'bill.pdf');
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
    
    return (
        <div className="mainsection">
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Price</th>
                        <th>Quantity</th>
                        <th>Subtotal</th>
                    </tr>
                </thead>
                <tbody>
                    {cartItems.map((item, index) => (
                        <tr key={index}>
                            <td>{item.name}</td>
                            <td>{item.price}0€</td>
                            <td>{item.quantity}</td>
                            <td>{(item.quantity * item.price).toFixed(2)}€</td> {/* Display subtotal */}
                        </tr>
                    ))}
                </tbody>
                <tfoot className="endPrice">
                    <tr>
                        <td colSpan="3">Total End Price:</td>
                        <td>{totalEndPrice.toFixed(2)}€</td> {/* Display total end price */}
                    </tr>
                    <button className="downloadBtn" onClick={handleCheckout}>Pay & Get Bill</button>
                </tfoot>
            </table>
        </div>
    );
}

export default CheckOut;
```

![grafik](https://github.com/Aryt3/coffeeshop/assets/110562298/f8fea1f4-a77e-4a0a-9282-b8aa0361a35e)

If you want to pay you can press the button and receive a `PDF` with the bill printed on it. <br/>
![grafik](https://github.com/Aryt3/coffeeshop/assets/110562298/ab8f98f7-e093-4323-b85f-95db02e92356)

To inspect the current amount of products I have in stock I made another webpage called `overview`. <br/>
```js
import React, { useState, useEffect } from 'react';

function Overview() {

    const [products, setProducts] = useState([]);

    useEffect(() => {
        fetch('/api/stock')
          .then(response => response.json())
          .then(data => setProducts(data))
          .catch(error => console.error('Error fetching products:', error));
      }, []);
    
    return (
        <div className="mainsection">
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>In Stock</th>
                    </tr>
                </thead>
                <tbody>
                    {products.map((item, index) => (
                        <tr key={index}>
                            <td>{item.name}</td>
                            <td>{item.amount}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Overview;
```

This will fetch the latest results from the database. <br/>
![grafik](https://github.com/Aryt3/coffeeshop/assets/110562298/eaa22f5e-bbb5-4d37-9cf7-0700a8e10fae)






