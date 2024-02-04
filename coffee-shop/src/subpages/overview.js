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
