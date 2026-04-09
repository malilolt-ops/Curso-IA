# Curso-IA
# 🍳 Qué Cocino Hoy

Aplicación web desarrollada en Python con Streamlit que permite gestionar el inventario de cocina del hogar y sugerir recetas en base a los ingredientes disponibles.

## 🚀 Objetivo

El objetivo de esta aplicación es ayudar a las personas a:
- Reducir el desperdicio de alimentos
- Organizar su inventario de cocina
- Decidir qué cocinar con lo que ya tienen en casa

---

## 🧠 Funcionalidades

- 📦 Visualización del inventario actual (ingredientes, cantidades y unidades)
- ➕ Registro de nuevas compras (actualiza automáticamente el inventario)
- 🍝 Sugerencia de recetas disponibles según ingredientes
- ⚠️ Identificación de recetas incompletas indicando ingredientes faltantes
- 🔥 Función "Cocinar" que descuenta automáticamente los ingredientes utilizados
- 💾 Persistencia de datos mediante archivos JSON

---

## 🛠️ Tecnologías utilizadas

- Python
- Streamlit
- JSON

---

## 📂 Estructura del proyecto
├── app.py
├── inventario.json
├── recetas.json
├── requirements.txt
└── utils/
├── inventario.py
├── recetas.py
└── sugerencias.py
---

## ▶️ Cómo ejecutar la aplicación

1. Clonar o descargar el repositorio

2. Abrir una terminal en la carpeta del proyecto

3. Instalar dependencias:

pip install -r requirements.txt

4. Ejecutar la aplicación:

python -m streamlit run app.py

5. Abrir en el navegador:

http://localhost:8501
---

## 📌 Posibles mejoras futuras

- Filtro por tipo de comida (desayuno, almuerzo, cena)
- Lista de compras automática
- Recomendaciones según alimentos próximos a vencer
- Interfaz más avanzada
- Integración con base de datos

---

## 💡 Autor

Proyecto desarrollado como parte de un curso de Inteligencia Artificial.