from neo4j import GraphDatabase

class RecomendadorNeo4j:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def cerrar(self):
        self.driver.close()

    def recomendar_por_contenido(self, idUsuario, topN=5):
        with self.driver.session() as session:
            query = """
            MATCH (u:Usuario {id: $idUsuario})-[:VIO]->(pV:Pelicula)-[:TIENE_GENERO]->(g:Genero)
            WITH u, g, COUNT(*) AS frecuencia
            MATCH (p2:Pelicula)-[:TIENE_GENERO]->(g)
            WHERE NOT (u)-[:VIO]->(p2)
            WITH p2, SUM(frecuencia) AS score
            RETURN DISTINCT p2.id AS idPelicula, p2.titulo AS titulo, p2.puntuacion AS puntuacion,
                            score * p2.puntuacion AS totalScore
            ORDER BY totalScore DESC
            LIMIT $topN
            """
            result = session.run(query, idUsuario=idUsuario, topN=topN)
            return [record.data() for record in result]
