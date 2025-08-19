#
import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI") # e.g., "neo4j+s://your-neo4j-instance.databases.neo4j.io"
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

class GraphService:
    def __init__(self):
        self._driver = None
        if NEO4J_URI and NEO4J_USER and NEO4J_PASSWORD:
            try:
                self._driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
                print("✅ Neo4j Graph Database driver initialized.")
            except Exception as e:
                print(f"❌ Failed to initialize Neo4j driver: {e}")
        else:
            print("Neo4j credentials not configured. Graph features will be disabled.")

    def close(self):
        if self._driver is not None:
            self._driver.close()

    def add_threat_to_graph(self, threat_log):
        if not self._driver:
            return
        with self._driver.session() as session:
            session.execute_write(self._create_threat_nodes_and_relationships, threat_log)
    
    @staticmethod
    def _create_threat_nodes_and_relationships(tx, threat_log):
        # This function creates nodes for the IP, the Threat, and the Source, and links them.
        query = (
            "MERGE (ip:IP {address: $ip}) "
            "MERGE (threat:Threat {description: $threat_description}) "
            "MERGE (source:Source {name: $source_name}) "
            "CREATE (log:ThreatLog {id: $log_id, timestamp: datetime($timestamp)}) "
            "MERGE (ip)-[:PERFORMED]->(log) "
            "MERGE (log)-[:IS_A]->(threat) "
            "MERGE (log)-[:REPORTED_BY]->(source)"
        )
        tx.run(query, ip=threat_log.ip, threat_description=threat_log.threat,
               source_name=threat_log.source, log_id=threat_log.id,
               timestamp=threat_log.timestamp.isoformat() if threat_log.timestamp else None)

    def get_attack_storyline(self, threat_log_id: int):
        if not self._driver:
            return []
        with self._driver.session() as session:
            return session.execute_read(self._get_storyline_by_threat_id, threat_log_id)

    @staticmethod
    def _get_storyline_by_threat_id(tx, threat_log_id):
        # This query finds all other logs performed by the same IP address.
        query = (
            "MATCH (start_log:ThreatLog {id: $threat_log_id})<-[:PERFORMED]-(ip:IP) "
            "MATCH (ip)-[:PERFORMED]->(other_log:ThreatLog) "
            "MATCH (other_log)-[:IS_A]->(threat:Threat) "
            "RETURN other_log.id AS id, other_log.timestamp AS timestamp, threat.description AS threat "
            "ORDER BY timestamp"
        )
        results = tx.run(query, threat_log_id=threat_log_id)
        return [{"id": record["id"], "timestamp": record["timestamp"].iso_format(), "threat": record["threat"]} for record in results]