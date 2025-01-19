from collections import Counter, defaultdict
import json
import csv
from biocypher._logger import logger
from pathlib import Path
import rdflib

class Neo4jCSVWriter:
    def __init__(self, schema_config, biocypher_config, output_dir):
        self.csv_delimiter = '|'
        self.array_delimiter = ';'
        self.output_path = Path(output_dir)
        self.create_edge_types(schema_config)
        self.translation_table = str.maketrans({self.csv_delimiter: '', self.array_delimiter: ' ', "'": "", '"': ""})
        self.ontologies = {'go', 'bto', 'efo', 'cl', 'clo', 'uberon'}

    def create_edge_types(self, schema_config):
        self.edge_node_types = {}
        for k, v in schema_config.items():
            if v["represented_as"] == "edge":
                label = self.convert_input_labels(v["input_label"][0] if isinstance(v["input_label"], list) else v["input_label"])
                source = self.convert_input_labels(v["source"][0] if isinstance(v["source"], list) else v["source"])
                target = self.convert_input_labels(v["target"][0] if isinstance(v["target"], list) else v["target"])
                self.edge_node_types[label.lower()] = {"source": source.lower(), "target": target.lower()}

    def preprocess_value(self, value):
        if isinstance(value, list):
            return json.dumps([self.preprocess_value(item) for item in value])
        if isinstance(value, (rdflib.term.Literal, str)):
            return str(value).translate(self.translation_table)
        return value

    def preprocess_id(self, prev_id):
        return prev_id.lower().strip().translate(str.maketrans({' ': '_', ':': '_'}))

    def write_chunk(self, chunk, headers, file_path):
        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=self.csv_delimiter)
            for row in chunk:
                processed_row = [self.preprocess_value(row.get(header, '')) for header in headers]
                writer.writerow(processed_row)

    def write_to_csv(self, data, file_path, chunk_size=1000):
        headers = sorted({key for entry in data for key in entry.keys()})
        headers = ['id'] + [h for h in headers if h != 'id']
        
        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=self.csv_delimiter)
            writer.writerow(headers)
        
        for i in range(0, len(data), chunk_size):
            self.write_chunk(data[i:i + chunk_size], headers, file_path)

    def write_nodes(self, nodes, path_prefix=""):
        output_dir = self.output_path / path_prefix
        output_dir.mkdir(parents=True, exist_ok=True)

        node_groups = defaultdict(list)
        for node in nodes:
            id, label, properties = node
            label = label.split('.')[-1].lower()
            node_groups[label].append({'id': self.preprocess_id(id), **properties})

        for label, node_data in node_groups.items():
            file_path = output_dir / f"nodes_{label}.csv"
            self.write_to_csv(node_data, file_path)

    def write_edges(self, edges, path_prefix=""):
        output_dir = self.output_path / path_prefix
        output_dir.mkdir(parents=True, exist_ok=True)

        edge_groups = defaultdict(list)
        for edge in edges:
            source_id, target_id, label, properties = edge
            label = label.lower()
            edge_groups[label].append({
                'source_id': self.preprocess_id(source_id),
                'target_id': self.preprocess_id(target_id),
                **properties
            })

        for label, edge_data in edge_groups.items():
            file_path = output_dir / f"edges_{label}.csv"
            self.write_to_csv(edge_data, file_path)
