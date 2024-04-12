import "./checkout.css";
import { saveAs } from 'file-saver';
import React, { useEffect, useState } from 'react';

function CheckOut() {

    const [products, setProducts] = useState([]);
    const [credits, setCredits] = useState(0);

    useEffect(() => {
        fetch('/api/shopping_basket')
            .then(response => response.json())
            .then(data => setProducts(data))
            .catch(error => console.error('Error fetching products:', error))

            fetch('/api/credits')
            .then(response => response.json())
            .then(data => setCredits(data.credits))
            .catch(error => console.error('Error fetching products:', error))
    }, []);

    const handleCheckout = () => {
        fetch('/api/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.blob())
        .then(blob => {
            // Save the blob as a file using FileSaver.js
            saveAs(blob, 'bill.pdf');
    
            // Fetch shopping basket and credits after checkout
            fetch('/api/shopping_basket')
                .then(response => response.json())
                .then(data => setProducts(data))
                .catch(error => console.error('Error fetching products:', error));
    
            fetch('/api/credits')
                .then(response => response.json())
                .then(data => setCredits(data.credits))
                .catch(error => console.error('Error fetching credits:', error));
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
    
    
    const totalEndPrice = products.reduce((acc, item) => acc + item.quantity * item.price, 0);

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
                    {products.map((item, index) => (
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
                    <tr>
                        <td colSpan="3">Current Credits:</td>
                        <td>{credits.toFixed(2)}€</td>
                    </tr>
                    <button className="downloadBtn" onClick={handleCheckout}>Pay & Get Bill</button>
                </tfoot>
            </table>
        </div>
    );
}

export default CheckOut;
