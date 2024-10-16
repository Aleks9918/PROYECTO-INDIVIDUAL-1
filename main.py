from fastapi import FastAPI
import pandas as pd

# Instanciamos FastAPI
app = FastAPI()

df_games = pd.read_json('./data_limpia/output_steam_games_limpia.json', lines=True)
df_reviews = pd.read_json('./data_limpia/user_reviews.json', lines=True)
df_items = pd.read_json('./data_limpia/australian_user_items_limpia.json', lines=True)
#Consulta 1
#Esta consulta devuelve una tabla que indica la cantidad de items y porcentaje de contenido free por año según empresa desarrolladora 
@app.get('/developer/{desarrollador}')
def developer(desarrollador: str, games_df):
    """
    Función para analizar los juegos desarrollados por un desarrollador específico.
    
    Args:
        desarrollador (str): Nombre del desarrollador.
        games_df (DataFrame): DataFrame que contiene información de los juegos.
        
    Returns:
        DataFrame: DataFrame con el conteo de juegos lanzados por año y el porcentaje de juegos gratuitos.
    """
    games_df['release_date'] = pd.to_datetime(games_df['release_date'], errors='coerce')
    df_dev = games_df[games_df['developer'] == desarrollador]
    items_por_año = df_dev.groupby(df_dev['release_date'].dt.year).size().reset_index(name='Items')
    free_por_año = df_dev[df_dev['price'] == 0].groupby(df_dev['release_date'].dt.year).size().reset_index(name='freeitem')
    result_df = items_por_año.merge(free_por_año, on='release_date', how='left')
    result_df['freeitem'] = ((result_df['freeitem'].fillna(0) / result_df['Items']) * 100).round(2).astype(str) + '%'
    result_df.rename(columns={'release_date': 'Año'}, inplace=True)
    return result_df
dev = input("¿Nombre del desarrollador? ")
funcion1 = developer(dev, df_games)
print(funcion1)

#CONSULTA 2 
#Esta consulta devuelve un diccionario con cantidad de dinero gastado por el usuario, el porcentaje de recomendación en base a reviews.recommend y cantidad de items.
@app.get("/userdata/")
def get_user_data(User_id: str):
    df_items['user_id'] = df_items['user_id'].astype(str)
    df_reviews['user_id'] = df_reviews['user_id'].astype(str)

    user_items = df_items[df_items['user_id'] == User_id]

    df_games['price'] = pd.to_numeric(df_games['price'], errors='coerce')

    if not user_items.empty:
        money_spent = user_items.merge(df_games[['id', 'price']], left_on='item_id', right_on='id', how='left')['price'].sum()
    else:
        money_spent = 0.0

    total_items = user_items['items_count'].sum()

    user_reviews = df_reviews[df_reviews['user_id'] == User_id]

    if user_reviews.shape[0] > 0:
        recommendation_percentage = (user_reviews['recommend'].sum() / user_reviews.shape[0]) * 100
    else:
        recommendation_percentage = 0.0 

    result = {
        "Usuario": User_id,
        "Dinero gastado": f"{float(money_spent):.2f} USD",  
        "% de recomendación": f"{float(recommendation_percentage):.2f}%",
        "Cantidad de items": int(total_items)
    }

    return result

#CONSULTA 3 
#Devuelve el usuario que acumula más horas jugadas para el genero dado y una lista de la acumulación de horas jugadas por año de lanzamiento 
@app.get("/user-for-genre/")
def UserForGenre(genero: str, df_games: pd.DataFrame, df_items: pd.DataFrame):
    filtered_games = df_games[df_games['genres'].str.contains(genero, na=False)]

    if filtered_games.empty:
        return {"Usuario con más horas jugadas para Género": None, "Horas jugadas": []}
    filtered_items = df_items[df_items['item_id'].isin(filtered_games['id'])]
    filtered_items = filtered_items.merge(filtered_games[['id', 'release_date']], left_on='item_id', right_on='id')
    filtered_items['release_year'] = pd.to_datetime(filtered_items['release_date']).dt.year
    user_playtime = filtered_items.groupby('user_id')['playtime_forever'].sum().reset_index()
    top_user = user_playtime.loc[user_playtime['playtime_forever'].idxmax()]
    hours_per_year = filtered_items.groupby('release_year')['playtime_forever'].sum().reset_index()
    hours_list = hours_per_year.rename(columns={'release_year': 'Año', 'playtime_forever': 'Horas'}).to_dict(orient='records')

    return {
        "Usuario con más horas jugadas para Género": top_user['user_id'],
        "Horas jugadas": hours_list
    }
#CONSULTA 4.
#Devuelve el top 3 de desarrolladores con juegos MÁS recomendados por usuarios para el año dado.
@app.get("/best_developer_year/")
def best_developer_year(año: int):
    games_of_year = df_games[df_games['release_date'].dt.year == año]
    if games_of_year.empty:
        return JSONResponse(content={"error": "No se encontraron juegos para el año especificado."})
    game_ids = games_of_year['id'].tolist()
    reviews_of_year = df_reviews[df_reviews['item_id'].isin(game_ids) & (df_reviews['recommend'] == True)]
    developer_recommendations = reviews_of_year['user_id'].value_counts().reset_index()
    developer_recommendations.columns = ['developer', 'recommend_count']
    top_developers = (
        games_of_year[['developer', 'id']]
        .drop_duplicates(subset=['id'])
        .merge(developer_recommendations, left_on='id', right_on='developer', how='inner')
        .groupby('developer')['recommend_count']
        .sum()
        .reset_index()
        .sort_values(by='recommend_count', ascending=False)
    )
    top_3_developers = top_developers.head(3)
    result = [{f"Puesto {i+1}": row['developer']} for i, row in enumerate(top_3_developers.itertuples())]

    return result
#CONSULTA 5.
#Se devuelve un diccionario con el nombre del desarrollador como llave y una lista con la cantidad total de registros de reseñas de usuarios que se encuentren categorizados con un análisis de sentimiento como valor positivo o negativo.
@app.get("/developer_reviews_analysis/")
def developer_reviews_analysis(desarrolladora: str):
    developer_games = df_games[df_games['developer'].str.lower() == desarrolladora.lower()]
    if developer_games.empty:
        return JSONResponse(content={desarrolladora: "No se encontraron juegos para este desarrollador."})
    game_ids = developer_games['id'].tolist()
    developer_reviews = df_reviews[df_reviews['item_id'].isin(game_ids)]
    positive_count = developer_reviews[developer_reviews['sentiment_analysis'] == 2].shape[0]
    negative_count = developer_reviews[developer_reviews['sentiment_analysis'] == 0].shape[0]
    result = {
        desarrolladora: [
            {"Negative": negative_count},
            {"Positive": positive_count}
        ]
    }

    return result


#ENDPOINTS
@app.get("/developer/{desarrollador}")
def get_developer_info(desarrollador: str):
    result = developer(desarrollador, df_games)
    return result.to_dict(orient='records')

@app.get("/userdata/")
def get_user_data(User_id: str): 
    result = get_user_data(User_id,df_items,df_games,df_reviews)
    return result.to_dict(orient='records')

@app.get("/user-for-genre/")
def UserForGenre(genero: str, df_games: pd.DataFrame, df_items: pd.DataFrame):
    result = UserForGenre(genero,df_items,df_games)
    return result.to_dict(orient='records')

@app.get("/best_developer_year/")
def best_developer_year(año: int):
    result = best_developer_year(año,df_games,df_reviews)
    return result.to_dict(orient='records')

@app.get("/developer_reviews_analysis/")
def developer_reviews_analysis(desarrolladora: str):
    result = developer_reviews_analysis(desarrolladora,df_games,df_reviews)
    return result.to_dict(orient='records')

@app.get("/")
def index():
    return "Hola"