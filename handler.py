from rdflib import Graph, Literal, RDF, URIRef, BNode, RDFS, Namespace
from pyshacl import validate

def query1(graph):
	units_6_or_more_outcomes = """
	SELECT ?unit (COUNT(?o) AS ?c)
	WHERE {
			?unit ns:has_outcome ?o .
	}
	GROUP BY ?unit
	HAVING (COUNT(?o) > 6)
	"""
	for row in graph.query(units_6_or_more_outcomes):
			print(f"{row.unit} has {row.c} outcomes")
                        
def query2(graph):
	level_3_full = """
SELECT ?unit
WHERE {
    ?unit ns:level 3 .
    FILTER NOT EXISTS {
        SELECT ?unit ?assess
        WHERE {
            ?unit ns:has_assessment ?assess .
            FILTER (CONTAINS(?assess, "exam"))
        }
    }
    OPTIONAL {
        ?unit ns:has_prereq ?ppp . 
        FILTER NOT EXISTS {
            SELECT ?unit2 ?pre ?p_assess
            WHERE {
                ?unit2 ns:has_prereq ?pre .
                ?pre ns:has_assessment ?p_assess .
                FILTER (CONTAINS(?p_assess, "exam"))
            }
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
							?unit ns:has_assessment ?assess .
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

	for row in graph.query(level_3_full):
		print(f"{row.unit} has no exams")
                
def query3(graph):
	more_3_maj = """
	SELECT ?unit (COUNT(?maj) AS ?c)
	WHERE {
			?maj ns:has_unit ?unit .
			?unit rdf:type ns:unit .
	} GROUP BY ?unit
	HAVING (COUNT(?maj) > 3)
	"""
	for row in graph.query(more_3_maj):
		print(f"{row.unit} is a unit in more than three majors")
                
def query4(word, graph):
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


	#for row in g.query(more_3_maj):
	#        print(f"{row.unit} is in {row.c} majors")

	value = word

	for row in graph.query(contains_keyword.replace("word", value)):
			print(f"{row.unit} contains the phrase '{value}'.")


sg = Graph()
with open("shaclconstraints.ttl") as f:
    sg.parse(data=f.read(), format='ttl')
  
g = Graph()
with open("handbook copy.ttl", encoding="utf8") as f:
    g.parse(data=f.read(), format='ttl')

def check_constraints(graph, constraints):
	results = validate(
    graph,
    shacl_graph=constraints,
    data_graph_format="ttl",
    shacl_graph_format="ttl",
    inference="rdfs",
    serialize_report_graph="ttl",
    )
	conforms, report_graph, report_text = results
	return report_text

def update_graph():
	print("1")

def handle_query():
	print("Welcome to the query handler! Please select one of the following options:\n")
	print(">To add data/relations press 0 \n>To update existing data/relations press 1 \n>To remove data/relations press 2")

def input_handler(max):
	user_input = input()
	try:
		x = 0 <= int(user_input) and int(user_input) <= max
	except:
		x = str(user_input) == "q"
	while not x:
		print(f"Input out of bounds, please enter a number between 0 and {max}, or q")
		user_input = input()
	return user_input

def prompt_user():
	input = -1
	while input != "q":
		print("Welcome to the Hanbook Handler! Please select one of the following options:\n")
		print(">To make updates to the graph press 0 \n>To execute queries press 1 \n>To check constraints press 2 \n>To quit press q")
		input = input_handler(2)
		if input == "0":
			update_graph()
		elif(input == "1"):
			handle_query()
		elif(input == "2"):
			# Checking Constraints
			print("Checking Constraints...\n")
			report = check_constraints(g,sg)
			print("Here is your report!\n")
			print(report)
  
# Updating Graph
prompt_user()



