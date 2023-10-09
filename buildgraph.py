from rdflib import Graph, Literal, RDF, URIRef, BNode, RDFS, Namespace
from rdflib.namespace import FOAF, RDFS, RDF
from pyshacl import validate
import json

# Create a Graph
g = Graph()
url = "https://www.example.com/"
ns = Namespace(url)
g.bind("ns", ns)

with open("majors.json", encoding='utf-8') as file:
        m = json.load(file)

title_of = URIRef(ns['title_of'])
school_of = URIRef(ns['school_of'])
board_of = URIRef(ns['board_of'])
mode_of = URIRef(ns['mode_of'])
desc_of = URIRef(ns['desc_of'])
outcome_of = URIRef(ns['outcome_of'])
prereq_of = URIRef(ns['prereq_of'])
unit = URIRef(ns['unit'])
course = URIRef(ns['course'])
major = URIRef(ns['major'])
g.add((unit, RDF.type, RDFS.Class))
g.add((course, RDF.type, RDFS.Class))
g.add((major, RDF.type, RDFS.Class))

for maj in m:
        imajor = URIRef(ns[m[maj]['code'].replace(" ","_")])
        g.add((imajor, RDF.type, major))
        g.add((imajor, FOAF.name, Literal(m[maj]['title'])))
        school = URIRef(ns[m[maj]['school'].replace(" ","_")])
        g.add((imajor, school_of, school))
        board = URIRef(ns[m[maj]['board_of_examiners'].replace(" ","_")])
        g.add((imajor, board_of, board))
        mode = URIRef(ns[m[maj]['delivery_mode'].replace(" ","_")])
        g.add((imajor, mode_of, mode))
        g.add((imajor, desc_of, Literal(m[maj]['description'])))
        g.add((imajor, outcome_of, Literal(m[maj]['outcomes'])))
        if ('prerequisites' in m[maj] ):
                g.add((imajor, prereq_of, Literal(m[maj]['prerequisites'])))
        for course in m[maj]['courses']:
                prereq_course = URIRef(ns[course.replace(" ","_")])
                g.add((imajor, prereq_of, prereq_course))
                g.add((prereq_course, RDF.type, RDFS.Class))
        for bridge in m[maj]['bridging']:
                prereq_course = URIRef(ns[bridge.replace(" ","_")])
                g.add((imajor, prereq_of, prereq_course))
                g.add((prereq_course, RDF.type, unit))
        for units in m[maj]['units']:
                prereq_course = URIRef(ns[units.replace(" ","_")])
                g.add((imajor, prereq_of, prereq_course))
                g.add((prereq_course, RDF.type, unit))

print(g.serialize(format="turtle"))

# create nodes with x = URIref('URL')
# or x = BNode()