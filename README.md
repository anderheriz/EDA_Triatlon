# EDA Triatlón: distancia olímpica vs Ironman 🏊🚴🏃

Proyecto de análisis exploratorio de datos sobre rendimiento en triatlón élite internacional. El objetivo es comparar cómo cambia el rendimiento entre la distancia olímpica y la distancia Ironman en pruebas profesionales.

## 📖 Tema

Comparativa entre resultados profesionales de:

- Ironman World Championship Kona: distancia Ironman.
- Juegos Olímpicos y finales WTCS: distancia olímpica.

El análisis final se centra en atletas profesionales y en las primeras 40 posiciones por carrera y género, para comparar ambas modalidades con un criterio competitivo similar.

## 📊 Fuentes de datos

- Resultados Ironman obtenidos desde endpoints públicos de Ironman/Competitor.
- Resultados de distancia olímpica obtenidos desde endpoints públicos de World Triathlon.
- Los CSV utilizados están dentro de la carpeta `data`.

## 📋 Hipótesis

1. El segmento de bicicleta tiene mayor peso sobre el tiempo total en Ironman que en distancia olímpica.
2. La carrera a pie está más relacionada con la posición final en distancia olímpica que en Ironman.
3. La variabilidad de tiempos es mayor en Ironman que en distancia olímpica.
4. La diferencia porcentual de rendimiento entre hombres y mujeres varía según la modalidad y el segmento.

## 📑 Archivos principales
- codigo/API.py: descarga los resultados desde los endpoints públicos y guarda los CSV en data. Si un CSV ya existe, no lo duplica.
notebook/recopilacion_limpieza_datos.ipynb: une CSVs, filtra profesionales, homogeneiza columnas y genera data/triatlon_clean.csv.
codigo/visualizacion.py: contiene funciones auxiliares para preparar datos y crear gráficos.
- memoria.ipynb: memoria principal del proyecto, con introducción, limpieza, análisis, visualizaciones e interpretación de hipótesis.
- Eda_triatlon_presentación.pptx: presentación final de resultados.

## Cómo ejecutar el proyecto
Ejecutar codigo/API.py si se quieren descargar de nuevo los datos originales.
Ejecutar notebook/recopilacion_limpieza_datos.ipynb para regenerar los CSV combinados y el dataset limpio.
Abrir memoria.ipynb para consultar el análisis final y las conclusiones.

## 📉 **Dataset final**

El dataset final utilizado en la memoria es:
- data/triatlon_clean.csv

Contiene 1.634 registros con resultados profesionales y primeras 40 posiciones por carrera y género.

## 💻 Tecnologías utilizadas
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Requests
- Jupyter Notebook
