#!/usr/bin/env python
import tqdm
import urllib3
from elasticsearch import Elasticsearch
from elasticsearch.helpers import streaming_bulk
import json

def read_mappings(file_name = "src/elasticsearch/index_mapping.json"):
	with open(file_name) as f:
		data = json.load(f)
	return data

RECIPE_FILE_NAME = "datasets/epirecipes/full_format_recipes.json"
INDEX_NAME = 'recipes'
INDEX_MAPPINGS = read_mappings()

def read_data(recipe_file_name):
	with open(recipe_file_name) as f:
		recipe_data = json.load(f)
	return recipe_data

def create_index(client):
	client.indices.create(
		index="recipes",
		body=INDEX_MAPPINGS,
		ignore=400,
	)

def generate_actions(recipe_data):
	for doc in recipe_data:
		if doc.get('calories'):
			doc['_id'] = doc['title']
			yield doc

def streaming_push(client, recipe_data):
	number_of_docs = len(recipe_data)
	progress, successes = tqdm.tqdm(unit="docs", total=number_of_docs), 0
	for ok, action in streaming_bulk(
		client=client,
		index=INDEX_NAME,
		actions=generate_actions(recipe_data)
	):
		progress.update(1)
		successes += ok
	print("Indexed %d/%d documents" % (successes, number_of_docs))

def main():
	recipe_data = read_data(RECIPE_FILE_NAME)
	client = Elasticsearch(['es01', 'localhost'], sniff_on_start=True, retry_on_timeout=True)
	print("Creating an index...")
	create_index(client)
	
	print("Indexing documents...")
	streaming_push(client, recipe_data)
	
if __name__ == "__main__":
	main()
