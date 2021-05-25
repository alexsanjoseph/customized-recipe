#!/usr/bin/env python
from elasticsearch import helpers, Elasticsearch
import json
import csv
import os

def read_mappings(file_name = "src/elasticsearch/index_mapping_user_rating.json"):
	with open(file_name) as f:
		data = json.load(f)
	return data


RECIPE_FILE_NAME = "datasets/epirecipes/user_profile.csv"
INDEX_NAME = 'user-rating-index'
INDEX_MAPPINGS = read_mappings()


def create_index(client):
	client.indices.create(
		index=INDEX_NAME,
		body=INDEX_MAPPINGS,
	)


def main():
	client = Elasticsearch(['es01', 'localhost'], sniff_on_start=True, retry_on_timeout=True)
	print("Creating an index...")
	create_index(client)

	with open('datasets/epirecipes/user_profile.csv') as f:
		reader = csv.DictReader(f)
		helpers.bulk(client, reader, index=INDEX_NAME)


if __name__ == "__main__":
	main()
