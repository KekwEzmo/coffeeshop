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
