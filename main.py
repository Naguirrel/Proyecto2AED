from recomendador import RecomendadorNeo4j

# Reemplaza estos valores con los tuyos de Neo4j Aura
uri = "neo4j+s://d4b1e994.databases.neo4j.io"
user = "neo4j"
password = "<tu-contraseña>"

reco = RecomendadorNeo4j(uri, user, password)

# Prueba con un ID de usuario que exista en la base de datos
recomendaciones = reco.recomendar_por_contenido("U1", topN=5)

for r in recomendaciones:
    print(f"{r['titulo']} (Puntaje: {r['totalScore']})")

reco.cerrar()