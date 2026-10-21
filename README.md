# Segmentación de clientes de un retailer en línea (RFM + K-Means)

Proyecto de minería de datos siguiendo la metodología CRISP-DM: ETL con SQL (SQLite), segmentación de clientes con RFM y K-Means, y despliegue en Streamlit.

## 1. Comprensión del negocio

**Contexto.** Retailer en línea del Reino Unido que vende artículos de regalo; muchos de sus clientes son mayoristas. Se dispone de sus transacciones entre diciembre de 2009 y diciembre de 2011.

**Problema.** La empresa no distingue entre sus clientes: no sabe cuáles son los más valiosos, cuáles compran de forma ocasional ni cuáles están dejando de comprar. Sin esa información, las acciones comerciales son las mismas para todos.

**Objetivo de negocio.** Identificar grupos de clientes con un comportamiento de compra similar para orientar acciones diferenciadas de fidelización, reactivación y retención.

**Preguntas de negocio**
- ¿Qué grupos de clientes existen según qué tan reciente, frecuente y alto es su gasto?
- ¿Qué parte de las ventas concentra cada grupo?
- ¿Qué clientes valiosos muestran señales de abandono?
- ¿Qué acción comercial conviene para cada grupo?

**Objetivo de minería de datos.** Segmentar a los clientes con un modelo no supervisado (K-Means) a partir de tres variables RFM: Recency (días desde la última compra), Frequency (número de compras) y Monetary (gasto total).

**Criterios de éxito**
- Negocio: segmentos interpretables, cada uno con una acción comercial concreta, y en un número manejable para un equipo de marketing (entre 3 y 6).
- Técnico: elegir el número de segmentos con el método del codo y el coeficiente silhouette, priorizando la interpretabilidad cuando ambos criterios no coincidan.

**Supuestos y limitaciones**
- Solo pueden segmentarse los clientes identificados; las ventas sin `Customer ID` (15.4 % del monto) quedan fuera.
- Monetary mide ingresos, no rentabilidad: el dataset no incluye costos ni márgenes.
- No hay datos demográficos; la segmentación se basa solo en el comportamiento de compra.
- Los datos terminan en diciembre de 2011; el análisis muestra el método, no la situación actual de la empresa.

## Dataset

[Online Retail II (UCI)](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci), publicado en Kaggle con licencia CC0 (dominio público). El archivo no se incluye en el repositorio; para reproducir el proyecto, descárgalo y colócalo en `data/raw/`.

> Las secciones de preparación, modelado, resultados y despliegue se completarán al terminar cada fase.