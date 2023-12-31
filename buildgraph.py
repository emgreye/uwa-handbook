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

with open("units.json", encoding='utf-8') as file:
        u = json.load(file)

has_school = URIRef(ns['has_school'])
has_board = URIRef(ns['has_board'])
has_mode = URIRef(ns['has_mode'])
desc = URIRef(ns['desc'])
has_outcome = URIRef(ns['has_outcome'])
has_prereq = URIRef(ns['has_prereq'])
has_bridge = URIRef(ns['has_bridge'])
has_unit = URIRef(ns['has_unit'])
level = URIRef(ns['level'])
credit = URIRef(ns['credit'])
has_assessment = URIRef(ns['has_assessment'])
has_advisable = URIRef(ns['has_advisable'])
contacttype = URIRef(ns['contacttype'])
has_contact = URIRef(ns['has_contact'])
has_code = URIRef(ns['has_code'])
has_text = URIRef(ns['has_text'])
hours = URIRef(ns['hours'])
part_of_course = URIRef(ns['part_of_course'])
weeklyhours = URIRef(ns['weeklyhours'])
unit = URIRef(ns['unit'])
course = URIRef(ns['course'])
major = URIRef(ns['major'])
board = URIRef(ns['board'])
school = URIRef(ns['school'])
mode = URIRef(ns['mode'])
g.add((unit, RDF.type, RDFS.Class))
g.add((course, RDF.type, RDFS.Class))
g.add((major, RDF.type, RDFS.Class))
g.add((board, RDF.type, RDFS.Class))
g.add((mode, RDF.type, RDFS.Class))
g.add((school, RDF.type, RDFS.Class))


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
        for icourse in m[maj]['courses']:
                prereq_course = URIRef(ns[icourse.replace(" ","_")])
                g.add((imajor, part_of_course, prereq_course))
                g.add((prereq_course, RDF.type, course))
        for bridge in m[maj]['bridging']:
                prereq_course = URIRef(ns[bridge.replace(" ","_")])
                g.add((imajor, has_bridge, prereq_course))
                g.add((prereq_course, RDF.type, unit))
        for units in m[maj]['units']:
                prereq_course = URIRef(ns[units.replace(" ","_")])
                g.add((imajor, has_unit, prereq_course))
                g.add((prereq_course, RDF.type, unit))

for uniti in u:
        iunit = URIRef((ns[u[uniti]['code'].replace(" ","_")]))
        g.add((iunit, has_code, iunit))
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
                g.add((iunit, has_assessment, Literal(assess)))
        if ('text' in u[uniti] ):
                g.add((iunit, has_text, Literal(u[uniti]['text'])))
        if ('note' in u[uniti] ):
                g.add((iunit, has_prereq, Literal(u[uniti]['note'])))
        if ('prerequisites_text' in u[uniti] ):
                g.add((iunit, has_prereq, Literal(u[uniti]['prerequisites_text'])))
        if ('prerequisites_cnf' in u[uniti] ):
                for lis in u[uniti]['prerequisites_cnf']:
                        for un in lis:
                                uni = URIRef(ns[un])
                                g.add((iunit, has_prereq, uni))
        if ('advisable_prior_study' in u[uniti] ):
                for un in u[uniti]["advisable_prior_study"]:
                        uni = URIRef(ns[un])
                        g.add((iunit, has_advisable, uni))
        if ('contact' in u[uniti] ):
                totalhours = 0
                for entry in u[uniti]['contact']:
                        totalhours += int(u[uniti]['contact'][entry])
                        contact = BNode()
                        g.add((iunit, has_contact, contact))
                        g.add((contact, hours, Literal(int(u[uniti]['contact'][entry]))))
                        g.add((contact, contacttype, Literal(entry)))
                g.add((iunit, weeklyhours, Literal(totalhours)))

# print(g.serialize(format="turtle"))
g.serialize(destination = 'handbook.ttl', format="ttl")


