import json
import streamlit as st
import elasticsearch
import os

def connect_to_es():
	es_host = [os.environ.get("ELASTICSEARCH_URL", "localhost")]
	es_con = elasticsearch.Elasticsearch(es_host)
	try:
		es_info = es_con.info()
	except elasticsearch.exceptions.ConnectionError:
		raise ConnectionError("Cannot connect to ES. Check if your Docker ES is running")
	return es_con

def get_es_queries(file_name = "src/elasticsearch/es_queries.json"):
	with open(file_name) as f:
		data = json.load(f)
	return data


def filter_by_category(category):
    return [{"term": {"categories.keyword":  {'value': category}}}]

def filter_by_area(area):
    return [{"bool": {"should": [{"match_phrase": {"Area": area}}],"minimum_should_match": 1}}]
