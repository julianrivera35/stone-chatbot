# 🚀 Buy n Large Chatbot - Backend  

Este repositorio contiene el backend del chatbot para **Buy n Large**, desarrollado con **Django, PostgreSQL y Transformers de Hugging Face**.  

## 📌 **Requisitos Previos**  

Antes de comenzar, asegúrate de tener instalados los siguientes programas:  

- [Python 3.13](https://www.python.org/downloads/)  
- [PostgreSQL](https://www.postgresql.org/download/)  
- [pipenv](https://pipenv.pypa.io/en/latest/install/) (o usa `venv` si prefieres)  
- [Docker (opcional)](https://www.docker.com/) si deseas levantar PostgreSQL con un contenedor  

## 📂 **Configuración del Entorno**  

### 1️⃣ **Clona el repositorio**  
```bash
git clone https://github.com/tu_usuario/buy-n-large-chatbot.git
cd buy-n-large-chatbot/backend
```  

### 2️⃣ **Crea el entorno virtual e instala dependencias**  
Usando `pipenv` (recomendado):  
```bash
pipenv install --dev
pipenv shell
```  
O con `venv` y `pip`:  
```bash
python -m venv env
source env/bin/activate  # En Windows usa: env\Scripts\activate
pip install -r requirements.txt
```  

### 3️⃣ **Configura las variables de entorno**  
Crea un archivo `.env` en la carpeta raíz del backend y copia lo siguiente:  
```ini
DJANGO_SECRET_KEY=g3j0qfah5i8t3j&^2gwh^k#mt4m1t9^)21&er@q**p#rel*ka#
DJANGO_DEBUG=True
DB_NAME=buynlarge
DB_USER='tu_usuario'
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
```  

### 4️⃣ **Configura PostgreSQL**  
Si usas PostgreSQL localmente:  
```sql
CREATE DATABASE buynlarge;
CREATE USER 'tu_usuario' WITH PASSWORD 'tu_contraseña';
ALTER ROLE 'tu_usuario' SET client_encoding TO 'utf8';
ALTER ROLE 'tu_usuario' SET default_transaction_isolation TO 'read committed';
ALTER ROLE 'tu_usuario' SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE buynlarge TO 'tu_usuario';
```  

Si prefieres usar Docker:  
```bash
docker run --name buynlarge-db -e POSTGRES_DB=buynlarge -e POSTGRES_USER='tu_usuario' -e POSTGRES_PASSWORD=tu_contraseña -p 5432:5432 -d postgres
```  

### 5️⃣ **Aplica migraciones y carga datos iniciales**  
```bash
python manage.py migrate
python manage.py createsuperuser  # (Opcional, para acceder al admin de Django)
python manage.py loaddata initial_data.json  # (Si tienes un dump de datos)
```  

### 6️⃣ **Entrena el modelo NLP**  
```bash
python train_model.py
```  

### 7️⃣ **Ejecuta el servidor**  
```bash
python manage.py runserver
```  
El backend estará disponible en: [http://127.0.0.1:8000](http://127.0.0.1:8000)  

## 📡 **Endpoints Principales**  

- `POST /api/chatbot/` → Recibe mensajes del usuario y responde con información sobre productos.  
- `GET /api/products/` → Obtiene la lista de productos disponibles.  
- `GET /api/dashboard/` → Retorna métricas de stock y productos.
- Puedes acceder a la documentación de los endpoints en: http://127.0.0.1:8000/swagger/ o http://127.0.0.1:8000/redoc/

## 📜 **Licencia**  
Este proyecto está bajo la licencia MIT.  

## 🚀 Configuración del Frontend

### 📌 Requisitos previos
Antes de ejecutar el frontend, asegúrate de tener instalado:

- [Node.js](https://nodejs.org/) (Versión recomendada: 18+)
- [npm](https://www.npmjs.com/) o [yarn](https://yarnpkg.com/)

### 📥 Instalación

1. Navega a la carpeta del frontend:
   ```sh
   cd frontend/chat-bot

2. Instala las dependencias: npm install o yarn install

3. Ejecuta el proyecto: npm start o yarn start

Esto levantará el servidor en http://localhost:3000/ y actualizará automáticamente la página al realizar cambios en el código.

📦 Dependencias Clave
El proyecto usa las siguientes librerías:

- react@19.0.0 - Biblioteca principal para la interfaz de usuario.
- react-dom@19.0.0 - Integración de React con el DOM.
- react-scripts@5.0.1 - Scripts y configuración predeterminada de React.
- jwt-decode@4.0.0 - Para decodificar tokens JWT.
- recharts@2.15.1 - Librería para visualización de datos.
- @testing-library/react y jest-dom - Herramientas para testing.

Si tienes problemas al ejecutar el frontend, revisa que todas las dependencias estén correctamente instaladas o intenta eliminarlas y reinstalarlas con:

rm -rf node_modules package-lock.json
npm install

¡Listo! Ahora puedes comenzar a trabajar con el frontend. 🚀