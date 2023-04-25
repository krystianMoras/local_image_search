# import cozo
from pycozo.client import Client
import numpy as np

def start_client(db_path):
    client = Client('sqlite', db_path)
    return client

def get_embedding_for_face(client, face):
    pass

def get_faces_for_name(client, name):
    pass

def get_similarity_for_name(client, face, name):

    return np.random.rand()

def get_similarities_table(client, face, names):

    # get names
    # get faces for names
    # get embeddings for faces
    # get distances between positive pairs
    # get distances between negative pairs
    # get mean and std of distances
    # threshold_certain = mean + 1 * std
    # threshold_possible = mean + 2 * std


    similarities = []
    for name in names:
        similarities.append({"name":name,"similarity":get_similarity_for_name(client, face, name)})
    return similarities

    client.run('''
    ?[dist, k, v] := ~face_embeddings:similarity{ k, v |
            query: q,
            k : 10,
            ef: 2000,
            bind_distance: dist
        }, q = vec($q) 

    ''', {'q':represent[0]["embedding"]})

