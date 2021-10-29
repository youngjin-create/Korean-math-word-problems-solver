# %%
import pickle

dataset_json = []

# %%
print('loading dataset...', end=' ')

############# LOADING DATA from PICKLE ###############
with open('data.pickle', 'rb') as f:
    loaded_data = pickle.load(f)
dataset_sentences = loaded_data['dataset_sentences']
dataset_phrases = loaded_data['dataset_phrases']
dataset_test = loaded_data['dataset_test']

print('done.')
