import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import ProductList from "./components/ProductList";
import SimilarProducts from "./components/SimilarProducts";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ProductList />} />
        <Route path="/similar-products/:objectID" element={<SimilarProducts />} />
      </Routes>
    </Router>
  );
}

export default App;
