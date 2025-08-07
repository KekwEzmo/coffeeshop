import './App.css';
import { Route, Routes } from "react-router-dom";
import NavBar from './navBar';
import Footer from './footer';
import Home from './subpages/home';
import CheckOut from './subpages/checkout';
import Overview from './subpages/overview';
import NotFoundPage from './error_404_page'; 
import { Cookies } from './cookies';

function App() {
  return (
    <div className="App">
      <NavBar/>
      <Routes>
        <Route exact path="/" element={<Home/>} />
        <Route exact path="/checkout" element={<CheckOut/>} />
        <Route exact path="/overview" element={<Overview/>} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
      <Cookies/>
      <Footer/>
    </div>
  );
}

export default App;
