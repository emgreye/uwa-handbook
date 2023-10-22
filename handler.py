from rdflib import Graph, Literal, RDF, URIRef, BNode, RDFS, Namespace
from pyshacl import validate
from rdflib import namespace
import re

class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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

def string_input_handler(count):
	user_input = input()
	while (user_input.count(', ') != count-1):
		print(f"Please enter a string with {count} comma-space-seperated values")
		user_input = input()
	new_input = re.sub(r'[^a-zA-Z0-9, ]', '', user_input)
	return new_input

def query(graph):
	invalid = True
	while invalid:
		string = string_input_handler(1)
		if string != 'q':
			try:
				for row in graph.query(string):
					print(row)
				invalid = False
			except:
				print(f"Invalid query! Fix your query and type it again or {bcolours.BOLD}enter q{bcolours.ENDC} to quit.")
		else:
			invalid = False

def queryfile(graph):
	invalid = True
	while invalid:
		filename = string_input_handler(1)
		if filename != 'q':
			try:
				with open(filename, encoding='utf-8') as string:
					try:
						for row in graph.query(string):
							print(row)
					except:
						print("Invalid syntax in file. Rewrite the file.")
				invalid = False
			except:
				print(f"Invalid directory! Type it correctly or {bcolours.BOLD}enter q{bcolours.ENDC} to quit.")
		else:
			invalid = False

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
                
def query4(graph, word):
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

def addnewdata(graph, subj, pred, obj):
	query = f"""
	INSERT DATA {{
		ns:{subj} ns:{pred} ns:{obj} .
	}}
	"""
	graph.update(query)
	
	find = f"""
	SELECT ?s
	WHERE {{
		?s ns:{pred} ns:{obj} .
	}}
	"""
	print(f"{bcolours.OKGREEN}({subj},{pred},{obj}) has been added.{bcolours.ENDC}")

def deleteentity(graph, entity):
	delete = f"""
	DELETE
	WHERE {{
		ns:{entity} ?pred ?obj . 
	}}
	"""
	delete2 = f"""
	DELETE
	WHERE {{
		?subj ?pred {entity} . 
	}}
	"""
	graph.query(delete)
	graph.query(delete2)
	print(f"{entity} has been deleted.")

def deletepredicate(graph, pred):
	delete = f"""
	DELETE
	WHERE {{
		?subj ns:{pred} ?obj . 
	}}
	"""
	graph.query(delete)
	print(f"{pred} has been deleted.")

def deleterelation(graph, subj, pred, obj):
	delete = f"""
	DELETE DATA {{
		ns:{subj} ns:{pred} ns:{obj} . 
	}}
	"""
	graph.query(delete)
	print(f"({subj},{pred},{obj}) has been deleted.")

def readentity(graph, entity):
	read = f"""
	SELECT ?pred ?obj
	WHERE {{
		ns:{entity} ?pred ?obj . 
	}}
	"""
	read2 = f"""
	SELECT ?pred ?obj
	WHERE {{
		?subj ?pred {entity} . 
	}}
	"""
	
	for row in graph.query(read):
		print(f"{entity}, {row.pred}, {row.obj}")
	for row in graph.query(read2):
		print(f"{row.subj}, {row.pred}, {entity}")

def readpredicate(graph, pred):
	read = f"""
	SELECT ?subj ?obj
	WHERE {{
		?subj ns:{pred} ?obj . 
	}}
	"""
	for row in graph.query(read):
		print(f"{row.subj}, {pred}, {row.obj}")

def readrelation(graph, subj, pred, obj):
	read = f"""
	SELECT *
	WHERE {{
		ns:{subj} ns:{pred} ns:{obj} . 
	}}
	"""
	if len(graph.query(read)) > 0:
		print(f"({subj}, {pred}, {obj}) exists.")
	else:
		print(f"({subj}, {pred}, {obj}) does not exist.")

sg = Graph()
with open("shaclconstraints.ttl") as f:
    sg.parse(data=f.read(), format='ttl')
  
g = Graph()
with open("handbook copy.ttl", encoding="utf8") as f:
    g.parse(data=f.read(), format='ttl')
url = "https://www.example.com/"
ns = Namespace(url)
g.bind("ns", ns)

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
	input = -1
	visited_update = False
	while (input != 'q'):
		if not visited_update:
			print(f"{bcolours.UNDERLINE}Welcome to the graph updater!{bcolours.ENDC} Please select one of the following options:\n")
			visited_update = True
		else:
			print(f"{bcolours.UNDERLINE}Welcome back to the graph updater!{bcolours.ENDC} Please select one of the following options:\n")
		print(f">To add new data {bcolours.BOLD}enter 0{bcolours.ENDC} \n>To read data {bcolours.BOLD}enter 1{bcolours.ENDC} \n>To update data {bcolours.BOLD}enter 2{bcolours.ENDC} \n>To delete data {bcolours.BOLD}enter 3{bcolours.ENDC}\n>To quit {bcolours.BOLD}enter q{bcolours.ENDC}")
		input = input_handler(3)
		if input == '0':
			print("Please specify the triple you'd like to add using the following format:")
			print(f"{bcolours.OKCYAN}subject, predicate, object{bcolours.ENDC}")
			triple = string_input_handler(3).split(", ")
			addnewdata(g, triple[0], triple[1], triple[2])
		elif input == '1':
			print("Please select one of the following options:\n")
			print(f">To read a relation {bcolours.BOLD}enter 0{bcolours.ENDC} \n>To read all relations of an entity {bcolours.BOLD}enter 1{bcolours.ENDC}\n>To read all relations of a predicate {bcolours.BOLD}enter 2{bcolours.ENDC}\n>To quit {bcolours.BOLD}enter q{bcolours.ENDC}")
			readinput = input_handler(2)
			if readinput == '0':
				print("Please specify the triple you'd like to delete using the following format:")
				print(f"{bcolours.OKCYAN}subject, predicate, object{bcolours.ENDC}")
				triple = string_input_handler(3).split(", ")
				readrelation(g, triple[0], triple[1], triple[2])
			elif readinput == '1':
				print("Please specify the entity you'd like to delete")
				readentity(string_input_handler(1))
			elif readinput == '2':
				print("Please specify the predicate you'd like to delete")
				readpredicate(string_input_handler(1))
		elif input == '3':
			print("Please select one of the following options:\n")
			print(f">To delete a relation {bcolours.BOLD}enter 0{bcolours.ENDC} \n>To delete an entity {bcolours.BOLD}enter 1{bcolours.ENDC} \n>To delete a predicate {bcolours.BOLD}enter 2{bcolours.ENDC} \n>To quit {bcolours.BOLD}enter q{bcolours.ENDC}")
			deleteinput = input_handler(2)
			if deleteinput == '0':
				print("Please specify the triple you'd like to delete using the following format:")
				print(f"{bcolours.OKCYAN}subject, predicate, object{bcolours.ENDC}")
				triple = string_input_handler(3).split(", ")
				deleterelation(g, triple[0], triple[1], triple[2])
			elif deleteinput == '1':
				print("Please specify the entity you'd like to delete")
				deleteentity(string_input_handler(1))
			elif deleteinput == '2':
				print("Please specify the predicate you'd like to delete")
				deletepredicate(string_input_handler(1))

def handle_query():
	input = -1
	visited_query = False
	while (input != 'q'):
		if not visited_query:
			print(f"{bcolours.UNDERLINE}Welcome to the query handler!{bcolours.ENDC} Please select one of the following options:\n")
			visited_query = True
		else:
			print(f"{bcolours.UNDERLINE}Welcome back to the query handler!{bcolours.ENDC} Please select one of the following options:\n")
		print(f">To run a pre-made query {bcolours.BOLD}enter 0{bcolours.ENDC} \n>To run a query from the terminal {bcolours.BOLD}enter 1{bcolours.ENDC} \n>To run a query from a text file {bcolours.BOLD}enter 2{bcolours.ENDC}\n>To quit {bcolours.BOLD}enter q{bcolours.ENDC}")
		input = input_handler(2)
		if input == "0":
			queryinput = -1
			while (queryinput != 'q'):
				print("Please choose a query by entering its number:")
				print("0. Print all units with more than 6 outcomes.")
				print("1. Print all units with no exams.")
				print("2. Print all units in more than 3 majors.")
				print("3. Print all units which include a specified phrase.")
				print(f"Or {bcolours.BOLD}enter q{bcolours.ENDC} to quit")
				queryinput = input_handler(3)
				if queryinput == '0':
					query1(g)
				elif queryinput == '1':
					query2(g)
				elif queryinput == '2':
					query3(g)
				elif queryinput == '3':
					print("Please specify which phrase you want to search for.")
					query4(g, string_input_handler(1))
		elif input == "1":
			print("Please write your query in SPARQL syntax.")
			query(g)
		elif input == "2":
			print("Please enter the directory to your txt file.")
			queryfile(g)
		
def prompt_user():
	input = -1
	visited = False
	while input != "q":
		if (not visited):
			print(f"{bcolours.UNDERLINE}Welcome to the Hanbook Handler!{bcolours.ENDC} Please select one of the following options:\n")
			visited = True
		else:
			print(f"{bcolours.UNDERLINE}Welcome back to the Hanbook Handler!{bcolours.ENDC} Please select one of the following options:\n")
		print(f">To make updates to the graph {bcolours.BOLD}enter 0{bcolours.ENDC} \n>To execute queries {bcolours.BOLD}enter 1 {bcolours.ENDC}\n>To check constraints {bcolours.BOLD}enter 2 {bcolours.ENDC}\n>To quit {bcolours.BOLD}enter q{bcolours.ENDC}")
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

prompt_user()



