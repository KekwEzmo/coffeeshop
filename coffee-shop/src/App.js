import './App.css';
import { Route, Routes } from "react-router-dom";
import NavBar from './navBar';
import Footer from './footer';
import Home from './subpages/home';
import CheckOut from './subpages/checkout';

function App() {
  return (
    <div className="App">
      <NavBar />
      <Routes>
        <Route exact path="/" element={<Home/>} />
        <Route exact path="/checkout" element={<CheckOut/>} />
      </Routes>
      <Footer />
    </div>
  );
}

export default App;
