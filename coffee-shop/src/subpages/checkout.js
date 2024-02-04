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
