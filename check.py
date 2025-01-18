import pickle

# Load the data from the txt files
def load_data_from_txt(rsids_file, pos_file):
    with open(rsids_file, 'r') as rsids:
        rsids_lines = rsids.readlines()[1:]  # Skip header
        rsids_data = {line.split(',')[0]: line.strip().split(',')[1:] for line in rsids_lines}

    with open(pos_file, 'r') as pos:
        pos_lines = pos.readlines()[1:]  # Skip header
        pos_data = {line.split(',')[0]: line.strip().split(',')[1] for line in pos_lines}

    return rsids_data, pos_data

# File paths
rsids_file = 'data/dbsnp_rsids_map.txt'
pos_file = 'data/dbsnp_pos_map.txt'

# Get the data
rsids_data, pos_data = load_data_from_txt(rsids_file, pos_file)

# Pickle the data
with open('data/dbsnp_rsids_map.pickle', 'wb') as rsids_pickle:
    pickle.dump(rsids_data, rsids_pickle)

with open('data/dbsnp_pos_map.pickle', 'wb') as pos_pickle:
    pickle.dump(pos_data, pos_pickle)

print("Pickle files created successfully!")
