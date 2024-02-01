import "./footer.css";
import twitterIcon from './assets/twitter.png';
import facebookIcon from './assets/facebook.png';

function Footer() {

    return(
        <div className="footer">
            <div className="fsection">
                <ul className="flist">
                    <li>
                        <p>Email:<br/>info@coffee-shop.at</p>
                    </li>
                </ul>
            </div>
            <div className="fsection">
                <ul className="flist">
                </ul>
            </div>
            <div className="fsection">
                <ul className="flist">
                    <li>
                        <a href="https://facebook.com/"><img class="icon" src={facebookIcon} alt="Facebook"/></a>
                    </li>
                    <li>
                        <a href="https://twitter.com/"><img class="icon" src={twitterIcon} alt="Twitter"/></a>
                    </li>
                </ul>
            </div>
            <div className="fsection">
            <ul className="flist">
                    <li>
                        <p>© 2023 Coffee-Shop</p>
                    </li>
                </ul>
            </div>
        </div>
    );    
}

export default Footer;