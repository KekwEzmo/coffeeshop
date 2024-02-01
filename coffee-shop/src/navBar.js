import "./navBar.css";

function NavBar() {
    return(
        <>
        <div className="navBar">
            <ul className="navList">
                <li className="centered">
                    <h1 href="/" className="home">Coffee-Shop</h1>
                </li>
            </ul>
        </div>
        </>
    );    
}

export default NavBar;