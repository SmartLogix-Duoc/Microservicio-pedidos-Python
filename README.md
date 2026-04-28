# Microservicio-pedidos-Python
## Microservicio de Procesamiento de Pedidos

Este repositorio contiene el microservicio encargado de automatizar la validación, asignación y gestión del historial de pedidos para nuestra plataforma de e-commerce. 

Este servicio está desarrollado por **Maximiliano Olguin** y forma parte de un ecosistema mayor de microservicios (junto con Inventario en Spring Boot y Envíos en FastAPI).

### 1. Clonar el repositorio y crear el entorno virtual
```bash
git clone <URL-DEL-REPO>
cd MicroService-Pedidos
python -m venv venv

2. Activar el entorno virtual
Windows: venv\Scripts\activate

Mac/Linux: source venv/bin/activate

3. Instalar dependencias
Asegúrate de instalar todas las librerías necesarias ejecutando:
Hay un archivo incluido por mi mismo con todas las versiones de librerias y frameworks
Bash
pip install -r requirements.txt

4. Aplicar Migraciones Internas
Aunque nuestra lógica de negocio usa MongoDB sin tablas, Django requiere su base de datos interna (sqlite3) para gestionar configuraciones básicas y sesiones.

Bash
python manage.py migrate

5. Levantar el Servidor
Bash
python manage.py runserver