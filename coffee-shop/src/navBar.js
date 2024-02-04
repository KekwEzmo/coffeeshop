import "./navBar.css";
import React from 'react';
import { Link } from 'react-router-dom';
import shoppingCartIcon from './assets/warenkorb.png';

function NavBar({ itemsInCart }) {
    return(
        <>
        <div className="navBar">
            <ul className="navList">
                <li className="centered">
                <Link to="/" style={{ textDecoration: 'none' }}>
                    <h1 className="home">Coffee-Shop</h1>
                </Link>
                </li>
            </ul>
            <div className="cartIcon">
                <Link to="/checkout">
                    <img src={shoppingCartIcon} alt="Shopping Cart" />
                </Link>
                {itemsInCart > 0 && <div className="dot">{itemsInCart}</div>}
            </div>
        </div>
        </>
    );    
}

export default NavBar;