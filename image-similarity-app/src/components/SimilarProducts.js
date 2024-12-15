import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import ProductCard from "./ProductCard";
import axios from "axios";

const SimilarProducts = () => {
  const { objectID } = useParams(); // Получаем ID из URL
  const [baseProduct, setBaseProduct] = useState(null);
  const [similarProducts, setSimilarProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchSimilarProducts = async () => {
      try {
        setLoading(true);
        const response = await axios.post("http://127.0.0.1:8000/recommend", {
          object_id: objectID,
          model_name: "resnet50",
        });
        setBaseProduct(response.data.base_product);
        setSimilarProducts(response.data.recommendations);
      } catch (error) {
        console.error("Error fetching similar products:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSimilarProducts();
  }, [objectID]);

  if (loading) return <p>Loading similar products...</p>;


  return (
    <div>
      <button onClick={() => navigate(-1)}>Назад</button>
      <h1>Base Product</h1>
      <div>
      <ProductCard {...baseProduct}/>
      </div>

      <h2>Similar Products</h2>
      <div style={{display: "flex", width: "90vw", flexWrap:"wrap"}}>
        {similarProducts.map((item, index) => (
          <div key={index}>
            <ProductCard {...item.product}/>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SimilarProducts;
