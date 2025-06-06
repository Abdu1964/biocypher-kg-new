import csv
import gzip
import json
import os
from biocypher_metta.adapters import Adapter
from biocypher_metta.adapters.helpers import build_variant_id, to_float, check_genomic_location
from biocypher._logger import logger


# Example TOPLD input data file:

# SNP1,SNP2,Uniq_ID_1,Uniq_ID_2,R2,Dprime,+/-corr
# 5031031,5032123,5031031:C:T,5032123:G:A,0.251,0.888,+
# 5031031,5063457,5031031:C:T,5063457:G:C,0.443,0.832,+



class TopLDAdapter(Adapter):
    INDEX = {'SNP1': 0, 'SNP2': 1, 'R2': 4, 'Dprime': 5, '+/-corr': 6}
    def __init__(self, filepath, dbsnp_pos_map, chr,
                 ancestry, write_properties, add_provenance,
                 start=None, end=None, cutoff=0.5):
        self.file_path = filepath
        self.dbsnp_pos_map = dbsnp_pos_map
        self.chr = chr
        self.ancestry = ancestry
        self.start = start
        self.end = end
        self.cutoff = cutoff
        self.label = "in_ld_with"
        self.source = "TopLD"
        self.source_url = "http://topld.genetics.unc.edu/"
        super(TopLDAdapter, self).__init__(write_properties, add_provenance)

    def get_edges(self):
        with gzip.open(self.file_path, 'rt') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                try:
                    var1_pos = int(row[TopLDAdapter.INDEX['SNP1']])
                    var2_pos = int(row[TopLDAdapter.INDEX['SNP2']])
                    if not check_genomic_location(self.chr, self.start, self.end, self.chr, var1_pos, var1_pos) or \
                            not check_genomic_location(self.chr, self.start, self.end, self.chr, var2_pos, var2_pos):
                        continue
                    rsid_1 = self.dbsnp_pos_map.get(f"{self.chr}_{var1_pos}", None)
                    rsid_2 = self.dbsnp_pos_map.get(f"{self.chr}_{var2_pos}", None)
                    if rsid_1 is None or rsid_2 is None:
                        logger.warning(f"Couldn't find rsid for position {var1_pos} or {var2_pos}")
                        continue

                    r2_score = to_float(f"{row[TopLDAdapter.INDEX['+/-corr']]}{row[TopLDAdapter.INDEX['R2']]}")
                    if abs(r2_score) < self.cutoff:
                        continue
                    props = {}
                    if self.write_properties:
                        props = {
                            'r2': to_float(r2_score),
                            'd_prime': to_float(row[TopLDAdapter.INDEX['Dprime']]),
                            'ancestry': self.ancestry
                        }
                        if self.add_provenance:
                            props['source'] = self.source
                            props['source_url'] = self.source_url

                    yield rsid_1, rsid_2, self.label, props

                except Exception as e:
                    logger.error(f"Error while processing line {row}, error: {e}, skipping...")
                    continue
