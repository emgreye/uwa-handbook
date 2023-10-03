from rdflib import Graph, Literal, RDF, URIRef, BNode, RDFS
from rdflib.namespace import FOAF, RDFS, RDF
from pyshacl import validate
from rdflib import Graph


# Create a Graph
g = Graph()

# create nodes with x = URIref('URL')
# or x = BNode()