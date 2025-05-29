from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import networkx as nx

app = Flask(__name__)
CORS(app)

# Rutas a los archivos
datos_path = 'nombres_simulado.csv'
peliculas_path = 'peliculas_reales.csv'
criterios_path = 'criterios_usuarios.csv'

datos_df = pd.read_csv(datos_path, encoding='latin1')
peliculas_df = pd.read_csv(peliculas_path, encoding='latin1')

# Limpiar nombres de columnas
peliculas_df.columns = peliculas_df.columns.str.strip()
datos_df.columns = datos_df.columns.str.strip()

# Crear grafo
G = nx.Graph()

for _, row in datos_df.iterrows():
    persona = f"persona_{row['Nombre']}"
    G.add_node(persona, tipo='persona')
    gustos = [g.strip().lower() for g in str(row['Peliculas que les gusta']).split(',')]
    for genero in gustos:
        G.add_node(genero, tipo='genero')
        G.add_edge(persona, genero)

for _, row in peliculas_df.iterrows():
    if not (1980 <= int(row['Año']) <= 2023):
        continue
    pelicula = f"pelicula_{row['Titulo']}"
    G.add_node(pelicula, tipo='pelicula')
    generos = [g.strip().lower() for g in str(row['Genero']).split(',')]
    for genero in generos:
        G.add_node(genero, tipo='genero')
        G.add_edge(pelicula, genero)

# Recomendador usando grafos
def recomendar_peliculas(nombre_usuario):
    nodo_usuario = f"persona_{nombre_usuario}"
    if nodo_usuario not in G:
        return []
    generos_usuario = set(G.neighbors(nodo_usuario))
    posibles_peliculas = set()
    for genero in generos_usuario:
        vecinos = G.neighbors(genero)
        for vecino in vecinos:
            if str(vecino).startswith("pelicula_"):
                posibles_peliculas.add(vecino.replace("pelicula_", ""))
    return list(posibles_peliculas)[:5]

@app.route('/recomendar', methods=['POST'])
def recomendar():
    data = request.json
    nombre = data.get('nombre')
    edad = data.get('edad')
    carrera = data.get('carrera')
    criterios = data.get('criterios')
    generos = data.get('generos')
    modo = data.get('modo')
    acomp = data.get('acompanantes')

    nueva_fila = {
        'Nombre': nombre,
        'Peliculas que les gusta': generos
    }
    global datos_df
    datos_df = pd.concat([datos_df, pd.DataFrame([nueva_fila])], ignore_index=True)
    datos_df.to_csv(datos_path, index=False, encoding='latin1')

    # Guardar criterios en nuevo archivo
    criterios_fila = {
        'Nombre': nombre,
        'Edad': edad,
        'Carrera': carrera,
        'Criterios': criterios,
        'Modo': modo,
        'Acompañantes': acomp
    }
    try:
        criterios_df = pd.read_csv(criterios_path, encoding='latin1')
        criterios_df = pd.concat([criterios_df, pd.DataFrame([criterios_fila])], ignore_index=True)
    except FileNotFoundError:
        criterios_df = pd.DataFrame([criterios_fila])
    criterios_df.to_csv(criterios_path, index=False, encoding='latin1')

    recomendaciones = recomendar_peliculas(nombre)
    return jsonify({"recomendaciones": recomendaciones})

@app.route('/usuarios', methods=['GET'])
def listar_recomendaciones():
    resultados = []
    for _, row in datos_df.iterrows():
        nombre = row['Nombre']
        rec = recomendar_peliculas(nombre)
        resultados.append({"nombre": nombre, "recomendaciones": rec})
    return jsonify(resultados)

app.run(debug=True)

cd "C:\Users\norma\OneDrive\Escritorio\Norman\2025\Semestre 3\Estructuras de datos\Proyecto2\Proyecto2AED\app.py"