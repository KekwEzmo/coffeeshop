import "./home.css";
import coffeeImg from '../assets/coffee1.avif'; 
import React, { useState, useEffect } from 'react';

function Home() {
    const [reqError, setReqError] = useState('');
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [quantity, setQuantity] = useState(1);

    useEffect(() => {
        fetch('/api/products')
            .then(response => response.json())
            .then(data => setProducts(data))
            .catch(error => console.error('Error fetching products:', error));
    }, []);

    useEffect(() => {
        if (selectedProduct !== null) {
            setQuantity(1);
        }
    }, [selectedProduct]);

    const addToBasket = () => {
        if (quantity <= 0 || quantity > 100) {
            alert('Please enter a valid quantity.');
            return;
        }

        fetch('/api/products', {
            method: 'POST',
            body: JSON.stringify({
                name: selectedProduct.name,
                price: selectedProduct.price,
                quantity: quantity
            }),
        })
        .then(response => response.json())
        .then(data => data.message != 'Insufficient Funds!' ? setSelectedProduct(null) : setReqError(data.message))
        .catch(error => console.error('Error adding product:', error));
    };

    return (
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
                        <button onClick={() => { setSelectedProduct(null); setReqError(''); }}>Close</button>
                        <h2 style={{ color: '#f00' }}>{reqError}</h2>
                    </div>
                </div>
            )}
        </div>
    );
}

export default Home;
