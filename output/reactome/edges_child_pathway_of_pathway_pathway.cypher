
    CALL apoc.periodic.iterate(
        "LOAD CSV WITH HEADERS FROM 'file:////mnt/c/Users/AbduM/Desktop/Abdu/iCog/Bio-cypher-KG/biocypher-kg/output/reactome/edges_child_pathway_of_pathway_pathway.csv' AS row FIELDTERMINATOR '|' RETURN row",
        "MATCH (source:pathway {id: row.source_id})
        MATCH (target:pathway {id: row.target_id})
        MERGE (source)-[r:child_pathway_of]->(target)
        SET r += apoc.map.removeKeys(row, ['source_id', 'target_id', 'label', 'source_type', 'target_type'])",
        {batchSize:1000}
    )
    YIELD batches, total
    RETURN batches, total;
                