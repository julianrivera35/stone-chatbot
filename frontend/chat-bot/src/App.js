import React, { useState } from 'react';
import ProductList from './components/ProductList';
import Chatbot from './components/ChatBot';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import {jwtDecode} from 'jwt-decode'; // Importación correcta
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);

  const handleLogin = async (email, password) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/token/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();
      if (response.ok) {
        // Guardar el token en localStorage
        localStorage.setItem('token', data.access);
        const decodedToken = jwtDecode(data.access); // Usar jwtDecode en lugar de jwt_decode
        setIsLoggedIn(true);
        setIsAdmin(decodedToken.role === 'admin'); // Verifica si el usuario es admin
        alert('Inicio de sesión exitoso');
      } else {
        alert('Error al iniciar sesión: ' + data.detail);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleRegister = () => {
    setShowRegister(true);
  };

  const handleCancel = () => {
    setShowRegister(false);
    setShowDashboard(false);
  };

  const handleShowDashboard = () => {
    setShowDashboard(true);
  };

  return (
    <div className="App">
      <header className="App-header">
        <nav className="navbar">
          <h1 className="app-title">Mi Aplicación</h1>
          <div className="nav-buttons">
            {!isLoggedIn && (
              <>
                <button className="nav-button" onClick={handleRegister}>Registrarse</button>
                <button className="nav-button" onClick={() => {
                  const email = prompt('Email:');
                  const password = prompt('Password:');
                  handleLogin(email, password);
                }}>Iniciar sesión</button>
              </>
            )}
            {isLoggedIn && (
              <>
                {isAdmin && <button className="nav-button" onClick={handleShowDashboard}>Dashboard</button>}
                <button className="nav-button" onClick={() => {
                  setIsLoggedIn(false);
                  setIsAdmin(false);
                  setShowDashboard(false);
                }}>Cerrar sesión</button>
              </>
            )}
          </div>
        </nav>
      </header>
      <main>
        {showRegister ? (
          <Register onCancel={handleCancel} />
        ) : showDashboard ? (
          <Dashboard />
        ) : (
          <>
            <ProductList />
            <Chatbot />
          </>
        )}
      </main>
    </div>
  );
}

export default App;
