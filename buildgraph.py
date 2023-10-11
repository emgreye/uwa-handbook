from rdflib import Graph, Literal, RDF, URIRef, BNode, RDFS, Namespace
from rdflib.namespace import FOAF, RDFS, RDF
#from pyshacl import validate
import json

# Create a Graph
g = Graph()
url = "https://www.example.com/"
ns = Namespace(url)
g.bind("ns", ns)

with open("majors.json", encoding='utf-8') as file:
        m = json.load(file)

with open("units.json", encoding='utf-8') as file:
        u = json.load(file)

has_school = URIRef(ns['has_school'])
has_board = URIRef(ns['has_board'])
has_mode = URIRef(ns['has_mode'])
desc = URIRef(ns['desc'])
has_outcome = URIRef(ns['has_outcome'])
has_prereq = URIRef(ns['has_prereq'])
level = URIRef(ns['level'])
credit = URIRef(ns['credit'])
assessment_of = URIRef(ns['assessment_of'])
has_advisable = URIRef(ns['has_advisable'])
contacttype = URIRef(ns['contacttype'])
has_contact = URIRef(ns['has_contact'])
hours = URIRef(ns['hours'])
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
        g.add((imajor, has_school, school))
        board = URIRef(ns[m[maj]['board_of_examiners'].replace(" ","_")])
        g.add((imajor, has_board, board))
        mode = URIRef(ns[m[maj]['delivery_mode'].replace(" ","_")])
        g.add((imajor, has_mode, mode))
        g.add((imajor, desc, Literal(m[maj]['description'])))
        for outcome in m[maj]['outcomes']:
                g.add((imajor, has_outcome, Literal(outcome)))
        if ('prerequisites' in m[maj] ):
                g.add((imajor, has_prereq, Literal(m[maj]['prerequisites'])))
        for course in m[maj]['courses']:
                prereq_course = URIRef(ns[course.replace(" ","_")])
                g.add((imajor, has_prereq, prereq_course))
                g.add((prereq_course, RDF.type, RDFS.Class))
        for bridge in m[maj]['bridging']:
                prereq_course = URIRef(ns[bridge.replace(" ","_")])
                g.add((imajor, has_prereq, prereq_course))
                g.add((prereq_course, RDF.type, unit))
        for units in m[maj]['units']:
                prereq_course = URIRef(ns[units.replace(" ","_")])
                g.add((imajor, has_prereq, prereq_course))
                g.add((prereq_course, RDF.type, unit))

for uniti in u:
        iunit = URIRef((ns[u[uniti]['code'].replace(" ","_")]))
        g.add((iunit, RDF.type, unit))
        g.add((iunit, FOAF.name, Literal(u[uniti]['title'])))
        school = URIRef(ns[u[uniti]['school'].replace(" ","_")])
        g.add((iunit, has_school, school))
        board = URIRef(ns[u[uniti]['board_of_examiners'].replace(" ","_")])
        g.add((iunit, has_board, board))
        mode = URIRef(ns[u[uniti]['delivery_mode'].replace(" ","_")])
        g.add((iunit, has_mode, mode))
        g.add((iunit, level, Literal(int(u[uniti]['level']))))
        g.add((iunit, desc, Literal(u[uniti]['description'])))
        g.add((iunit, credit, Literal(int(u[uniti]['credit']))))
        if ('outcomes' in u[uniti] ):
                for outcome in u[uniti]['outcomes']:
                        g.add((iunit, has_outcome, Literal(outcome)))
        for assess in u[uniti]['assessment']:
                g.add((iunit, assessment_of, Literal(assess)))
        if ('prerequisites_text' in u[uniti] ):
                g.add((iunit, has_prereq, Literal(u[uniti]['prerequisites_text'])))
        if ('note' in u[uniti] ):
                g.add((iunit, has_prereq, Literal(u[uniti]['note'])))
        if ('text' in u[uniti] ):
                g.add((iunit, has_prereq, Literal(u[uniti]['text'])))
        if ('prerequisities_cnf' in u[uniti] ):
                for lis in u[uniti]['prerequisites_cnf']:
                        for un in lis:
                                uni = URIRef(ns[un])
                                g.add((iunit, has_prereq, uni))
                                g.add((uni, RDF.type, unit))
        if ('advisable_prior_study' in u[uniti] ):
                for un in u[uniti]["advisable_prior_study"]:
                        uni = URIRef(ns[un])
                        g.add((iunit, has_advisable, uni))
        if ('contact' in u[uniti] ):
                for entry in u[uniti]['contact']:
                        contact = BNode()
                        g.add((iunit, has_contact, contact))
                        g.add((contact, hours, Literal(int(u[uniti]['contact'][entry]))))
                        g.add((contact, contacttype, Literal(entry)))


# print(g.serialize(format="turtle"))
g.serialize(destination = 'handbook.ttl', format="ttl")

def pretty(uri): return uri.split("/")[-1]

# SPARQL Queries
# Find All Units with > 6 Outcomes.

units_6_or_more_outcomes = """
SELECT ?unit (COUNT(?o) AS ?c)
WHERE {
        ?unit ns:has_outcome ?o .
}
GROUP BY ?unit
HAVING (COUNT(?o) > 6)
"""
# for row in g.query(units_6_or_more_outcomes):
#         print(f"{row.unit} has {row.c} outcomes")

level_3_unit_no_exam_no_pre_req_exam = """
SELECT ?unit
WHERE {
        ?unit ns:level 3 .
        FILTER NOT EXISTS {
                SELECT ?unit ?assess
                WHERE {
                        ?unit ns:assessment_of ?assess .
                        FILTER (CONTAINS(?assess, "exam"))
                } 
        }
        OPTIONAL {
        ?unit ns:has_prereq ?ppp . 
				FILTER NOT EXISTS {
                SELECT ?unit ?pre ?p_assess
                WHERE {
                        ?unit ns:has_prereq ?pre .
                        ?pre ns:assessment_of ?p_assess .
                        FILTER (CONTAINS(?p_assess, "exam"))
                } 
        }
}

"""

level_3_not_quite = """
SELECT ?unit
WHERE {
        ?unit ns:level 3 .
        FILTER NOT EXISTS {
                SELECT ?unit ?assess
                WHERE {
                        ?unit ns:assessment_of ?assess .
                        FILTER (CONTAINS(?assess, "exam"))
                } 
        }
}

"""

test = """
SELECT ?unit ?pre
		WHERE {
                ?unit rdf:type ns:unit .
				?unit ns:has_prereq ?pre .
				?pre rdf:type ns:unit .
		}
"""
#the above doesn't work because some pre-requisites are not units

more_3_maj = """
SELECT ?unit (COUNT(?maj) AS ?c)
WHERE {
        ?maj ns:has_prereq ?unit .
        ?unit rdf:type ns:unit .
} GROUP BY ?unit
HAVING (COUNT(?maj) > 3)
"""

contains_env = """
SELECT ?unit
WHERE {
        ?unit ns:desc ?descr .
        ?unit ns:has_outcome ?out .
        ?unit rdf:type ns:unit .
        FILTER (CONTAINS(?descr, "environmental policy") || CONTAINS(?out, "environmental policy"))
} GROUP BY ?unit
"""

contains_keyword = """
SELECT ?unit ?value
WHERE {
        ?unit ns:desc ?descr .
        ?unit ns:has_outcome ?out .
        ?unit rdf:type ns:unit .
        FILTER (CONTAINS(?descr, "word") || CONTAINS(?out, "word"))
} GROUP BY ?unit
"""

for row in g.query(level_3_not_quite):
        print(f"{row.unit} has no exams")

#for row in g.query(more_3_maj):
#        print(f"{row.unit} is in {row.c} majors")

value = "people are"

for row in g.query(contains_keyword.replace("word", value)):
        print(f"{row.unit} contains the phrase {value}")