Proyecto MLOps: Sistema de Recomendación de Videojuegos para Usuarios en Steam
¡Bienvenidos al proyecto de Machine Learning Operations (MLOps) de Aleks Salaya!

Descripción del Problema
El objetivo de este proyecto es implementar un modelo de recomendación de videojuegos que funcione eficazmente en un entorno real. El ciclo de vida de un proyecto de Machine Learning incluye desde la recolección y procesamiento de datos hasta el entrenamiento y la supervisión del modelo.

Contexto y Rol a Desarrollar
Contexto
Nos encontramos trabajando en Steam, una plataforma global de videojuegos. Nuestra misión es desarrollar un sistema de recomendación para los usuarios de la plataforma.

Rol a Desarrollar
En este proyecto, asumimos los roles de Científico de Datos e Ingeniero de MLOps en Steam. Empezamos desde cero para convertir datos desestructurados en un sistema de recomendación eficaz.

Descripción del Proyecto:
Los conjuntos de datos utilizados incluyen:

australian_user_reviews
australian_users_items
output_steam_games
Proceso de ETL: Transformaciones
Desanidado: Algunas columnas contienen valores anidados, como diccionarios o listas. Desanidamos estos valores para facilitar las consultas API.

Eliminación de Columnas No Utilizadas:

De output_steam_games: 'publisher', 'url', 'reviews_url', 'specs', 'early_access', 'tags', 'title'.
De australian_user_reviews: 'user_url', 'funny', 'last_edited', 'helpful'.
De australian_users_items: 'user_url', 'playtime_2weeks', 'steam_id', 'items_count'.
Análisis y Tratamiento de Valores Nulos:
En esta fase, examinamos las columnas 'title' y 'app_name' para identificar valores nulos. Se eliminan las primeras 88.310 filas del DataFrame, ya que todas contienen valores nulos en sus columnas.

Cambio de Tipo de Datos:
Las fechas se convierten al formato datetime para facilitar la extracción del año.

Feature Engineering:
En el conjunto de datos user_reviews, se crea una nueva columna llamada 'sentiment_analysis', que reemplaza a la anterior, aplicando un análisis de sentimiento utilizando técnicas de procesamiento de lenguaje natural (NLP) con la siguiente escala: malo: '0', neutral: '1' y positivo: '2'.

Desarrollo de la API:
Se exponen los datos de la empresa a través del framework FastAPI, ofreciendo las siguientes consultas:

Cantidad de artículos y porcentaje de contenido gratuito por año según la empresa desarrolladora: def developer(desarrollador: str)
Dinero gastado por el usuario, porcentaje de recomendaciones basado en reviews.recommend y cantidad de artículos: def userdata(User_id: str)
Usuario con más horas jugadas en un género específico y una lista con la acumulación de horas jugadas por año de lanzamiento: def UserForGenre(genero: str)
Top 3 desarrolladores con los juegos más recomendados por los usuarios para un año específico: def best_developer_year(año: int)
Desarrollador y lista con el total de registros de reseñas de usuarios categorizados como positivos o negativos: def developer_reviews_analysis(desarrolladora: str)
Deployment:
Utilizamos el servicio de Render para que la API esté disponible en la web.

Análisis Exploratorio de Datos (EDA):
Durante el EDA, realizamos diversas etapas para comprender mejor la información contenida en este conjunto de datos y extraer conclusiones iniciales.

Modelo de Aprendizaje Automático:
Desarrollamos un modelo de recomendación item-item en un entorno de aprendizaje automático. Se seleccionó un subconjunto de datos (reduciendo la matriz a un 20% para su funcionamiento en la API). Calculamos una matriz de similitud del coseno para evaluar la similitud entre videojuegos, teniendo en cuenta características como la fecha de lanzamiento y los géneros. Implementamos una función recomendacion_juego_muestreado que, dado el ID de un juego, devuelve una lista de 5 juegos recomendados similares.

Requisitos:

fastapi
uvicorn
pandas
sqlalchemy
scikit-learn
pyarrow
fastparquet
numpy
Autor:
Aleks Salaya