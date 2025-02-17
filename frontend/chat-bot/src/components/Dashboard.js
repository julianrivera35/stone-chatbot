import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, PieChart, Pie, Cell } from 'recharts';
import './Dashboard.css';

const Dashboard = () => {
  const [products, setProducts] = useState([]);
  const [brands, setBrands] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/products/')
      .then(response => response.json())
      .then(data => setProducts(data))
      .catch(error => console.error('Error:', error));

    fetch('http://127.0.0.1:8000/api/brands/')
      .then(response => response.json())
      .then(data => setBrands(data))
      .catch(error => console.error('Error:', error));

    fetch('http://127.0.0.1:8000/api/categories/')
      .then(response => response.json())
      .then(data => setCategories(data))
      .catch(error => console.error('Error:', error));
  }, []);

  const productsByBrand = brands.map(brand => ({
    name: brand.name,
    count: products.filter(product => product.brand.id === brand.id).length
  }));

  const productsByCategory = categories.map(category => ({
    name: category.name,
    value: products.filter(product => product.category.id === category.id).length
  }));

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  return (
    <div className="dashboard">
      <h2>Dashboard</h2>
      <div className="chart-container">
        <h3>Número de productos por marca</h3>
        <br></br>
        <BarChart width={600} height={300} data={productsByBrand}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
      </div>

      <div className="chart-container">
        <h3>Porcentaje de productos por categoría</h3>
        <PieChart width={800} height={800}>
          <Pie
            data={productsByCategory}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={200}
            fill="#8884d8"
            dataKey="value"
          >
            {productsByCategory.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </div>

      <div className="table-container">
        <h3>Productos</h3>
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Stock</th>
              <th>Precio</th>
            </tr>
          </thead>
          <tbody>
            {products.map(product => (
              <tr key={product.id}>
                <td>{product.name}</td>
                <td>{product.stock}</td>
                <td>{product.price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
