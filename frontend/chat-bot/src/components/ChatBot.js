import React, { useState } from 'react';
import './ChatBot.css';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(false);

  const sendMessage = () => {
    if (input.trim() === '') return;

    const message = { id: messages.length, text: input };
    setMessages([...messages, message]);

    fetch('http://127.0.0.1:8000/api/chatbot/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ session_id: null, input_text: input })
    })
      .then(response => response.json())
      .then(data => {
        console.log(data);

        if (data && data.response_text) {
          let responseMessage;

          if (typeof data.response_text === 'string') {
            responseMessage = {
              id: messages.length + 1,
              text: data.response_text
            };
          } else if (Array.isArray(data.response_text)) {
            responseMessage = {
              id: messages.length + 1,
              text: data.response_text.map(item => (
                `Producto: ${item.name}, Precio: ${item.price}`
              )).join('\n')
            };
          } else if (data.response_text.products && Array.isArray(data.response_text.products)) {
            responseMessage = {
              id: messages.length + 1,
              text: data.response_text.products.map(product => (
                `Producto: ${product.name}, Precio: ${product.price}, Descripción: ${product.description}`
              )).join('\n')
            };
          } else if (data.response_text.message && data.response_text.product) {
            responseMessage = {
              id: messages.length + 1,
              text: `${data.response_text.message}\nProducto: ${data.response_text.product.name}, Precio: ${data.response_text.product.price}, Descripción: ${data.response_text.product.description}`
            };
          } else {
            responseMessage = {
              id: messages.length + 1,
              text: 'Error: Formato de respuesta desconocido.'
            };
          }
          setMessages([...messages, responseMessage]);
        } else {
          const errorMessage = {
            id: messages.length + 1,
            text: 'Error: La respuesta del servidor no tiene el formato esperado.'
          };
          setMessages([...messages, errorMessage]);
        }
      })
      .catch(error => {
        console.error('Error:', error);
        const errorMessage = {
          id: messages.length + 1,
          text: 'Error: No se pudo comunicar con el servidor.'
        };
        setMessages([...messages, errorMessage]);
      });

    setInput('');
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div>
      {!isOpen && (
        <button className="chat-toggle-button" onClick={toggleChat}>
          Abrir Chat
        </button>
      )}
      {isOpen && (
        <div className="box">
          <button className="close-button" onClick={toggleChat}>
            &times;
          </button>
          <h2 className="title">Chatbot</h2>
          <div className="inner-box">
            {messages.map(message => (
              <div key={message.id} className="message">{message.text}</div>
            ))}
          </div>
          <input
            className="form"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <br />
          <button className="sent-button" onClick={sendMessage}>Enviar</button>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
