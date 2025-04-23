"""
neo4j_connector.py - Handles all Neo4j database operations
"""

from neo4j import GraphDatabase
from typing import Dict, List, Optional
from pathlib import Path
import yaml
from rich.console import Console

console = Console()

class Neo4jConnector:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Neo4j connection using configuration
        
        Args:
            config_path: Path to biocypher_config.yml or similar
        """
        self.driver = None
        self.config = self._load_config(config_path)
        self._connect()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load Neo4j configuration from YAML file"""
        default_config = {
            'uri': 'bolt://192.168.41.183:7687',
            'user': 'neo4j',
            'password': 'Abdu@123',
            'database': 'neo4j'
        }
        
        if not config_path:
            return default_config
            
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config.get('neo4j', default_config)
        except Exception as e:
            console.print(f"[red]Error loading config: {e}[/]")
            return default_config
    
    def _connect(self):
        """Establish connection to Neo4j"""
        try:
            self.driver = GraphDatabase.driver(
                self.config['uri'],
                auth=(
                    self.config['user'],
                    self.config['password']
                ),
                database=self.config['database']
            )
            # Verify connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            console.print("[green]✓ Successfully connected to Neo4j[/]")
        except Exception as e:
            console.print(f"[red]Failed to connect to Neo4j: {e}[/]")
            self.driver = None
    
    def store_knowledge_graph(self, kg_data: Dict):
        """
        Store knowledge graph data in Neo4j
        
        Args:
            kg_data: Dictionary containing nodes and relationships
        """
        if not self.driver:
            console.print("[red]No active Neo4j connection[/]")
            return False
            
        try:
            with self.driver.session() as session:
                # Example transaction - adapt to your actual data structure
                for node_type, nodes in kg_data.get('nodes', {}).items():
                    for node_id, properties in nodes.items():
                        query = (
                            f"MERGE (n:{node_type} {{id: $id}}) "
                            "SET n += $props"
                        )
                        session.run(query, id=node_id, props=properties)
                
                for rel_type, relationships in kg_data.get('relationships', {}).items():
                    for (source_id, target_id), properties in relationships.items():
                        query = (
                            f"MATCH (a) WHERE a.id = $source_id "
                            f"MATCH (b) WHERE b.id = $target_id "
                            f"MERGE (a)-[r:{rel_type}]->(b) "
                            "SET r += $props"
                        )
                        session.run(query, 
                                   source_id=source_id,
                                   target_id=target_id,
                                   props=properties)
            
            console.print("[green]✓ Knowledge graph stored in Neo4j[/]")
            return True
        except Exception as e:
            console.print(f"[red]Error storing knowledge graph: {e}[/]")
            return False
    
    def close(self):
        """Close the Neo4j connection"""
        if self.driver:
            self.driver.close()
            console.print("[yellow]Neo4j connection closed[/]")

# Helper functions for CLI integration
def get_neo4j_config_interactive() -> Dict:
    """Interactive prompt for Neo4j connection details"""
    from questionary import text
    
    console.print("\n[bold]Neo4j Connection Settings[/]")
    return {
        'uri': text(
            "Neo4j URI (e.g., bolt://localhost:7687):",
            default="bolt://192.168.41.183:7687"
        ).unsafe_ask(),
        'user': text(
            "Username:",
            default="neo4j"
        ).unsafe_ask(),
        'password': text(
            "Password:",
            default="Abdu@123"
        ).unsafe_ask(),
        'database': text(
            "Database (leave blank for default):",
            default="neo4j"
        ).unsafe_ask()
    }