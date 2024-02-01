import './App.css';
import { Route, Routes } from "react-router-dom";
import NavBar from './navBar';
import Footer from './footer';
import Home from './subpages/home';

function App() {
  return (
    <div className="App">
      <NavBar />
      <Routes>
        <Route exact path="/" element={<Home/>} />
      </Routes>
      <Footer />
    </div>
  );
}

export default App;
