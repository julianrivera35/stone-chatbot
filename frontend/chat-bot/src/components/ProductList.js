import React, { useEffect, useState } from 'react';
import './ProductList.css';

const ProductList = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/products/')
      .then(response => response.json())
      .then(data => setProducts(data))
      .catch(error => console.error('Error:', error));
  }, []);

  return (
    <div>
      <h2>Lista de Productos</h2>
      <div className="product-grid">
        {products.map((product, index) => (
          <div className="product-card" key={index}>
            <img 
              src={product.image_url || 'logo192.png'} 
              alt={product.name} 
              className="product-image"
            />
            <h3>{product.name}</h3>
            <h3> <span class = 'price'> {product.price}$ </span></h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductList;
