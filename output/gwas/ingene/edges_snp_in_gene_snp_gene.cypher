
    CALL apoc.periodic.iterate(
        "LOAD CSV WITH HEADERS FROM 'file:////mnt/c/Users/AbduM/Desktop/Abdu/iCog/Bio-cypher-KG/biocypher-kg/output/gwas/ingene/edges_snp_in_gene_snp_gene.csv' AS row FIELDTERMINATOR '|' RETURN row",
        "MATCH (source:snp {id: row.source_id})
        MATCH (target:gene {id: row.target_id})
        MERGE (source)-[r:snp_in_gene]->(target)
        SET r += apoc.map.removeKeys(row, ['source_id', 'target_id', 'label', 'source_type', 'target_type'])",
        {batchSize:1000}
    )
    YIELD batches, total
    RETURN batches, total;
            