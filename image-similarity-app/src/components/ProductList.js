import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import ProductCard from "./ProductCard";
import axios from "axios";

const ProductList = () => {
  const [products, setProducts] = useState([]);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50); // Размер страницы
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Загружаем продукты с сервера
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await axios.get(
          `http://127.0.0.1:8000/products?page=${page}&page_size=${pageSize}`
        );
        setProducts(response.data.products);
      } catch (error) {
        console.error("Error fetching products:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [page, pageSize]);

  if (loading) return <p>Loading products...</p>;

  return (
    <div>
      <h1>Product List</h1>
      <div style={{display: "flex", width: "90vw", flexWrap:"wrap"}}>
        {products.map((product) => (
          <div key={product.objectID}>
            <div>
              <ProductCard {...product} onClick={() =>
                  navigate(`/similar-products/${product.objectID}`)
                }/>
            </div>
          </div>
        ))}
      </div>

      <div>
        <button onClick={() => setPage((prev) => Math.max(prev - 1, 1))}>
          Previous
        </button>
        <button onClick={() => setPage((prev) => prev + 1)}>Next</button>
      </div>
    </div>
  );
};

export default ProductList;
