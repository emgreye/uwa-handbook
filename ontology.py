from owlready2 import *
onto = get_ontology("http://www.example.org/my_ontology.owl")

graph = default_world.as_rdflib_graph()

with onto:
  class Shape(Thing):
    pass
  class Unit(Thing):
    pass
  class Major(Thing):
    pass
  class Board(Thing):
    pass
  class School(Thing):
    pass
  class Mode(Thing):
    pass
  class Course(Thing):
    pass

  class has_board(ObjectProperty, FunctionalProperty):
    domain = [Unit, Major]
    range = [Board]

  class has_prereq(ObjectProperty, TransitiveProperty, AsymmetricProperty):
    domain = [Unit, Major]
    range = [Unit, Course]

  class level(DataProperty, FunctionalProperty):
    range = [int]

  class credit(DataProperty, FunctionalProperty):
    range = [int]

  class has_school(ObjectProperty, FunctionalProperty):
    domain = [Unit, Major]
    range = [School]

  class has_mode(ObjectProperty):
    domain = [Unit, Major]
    range = [Mode]

  class desc(DataProperty, FunctionalProperty):
    range = [str]

  class has_text(DataProperty):
    range = [str]

  class has_outcome(DataProperty):
    range = [str]

  class has_bridge(ObjectProperty):
    domain = [Major]
    range = [Unit]  

  class has_unit(ObjectProperty):
    domain = [Major]
    range = [Unit]  

  class has_unit_outcome(PropertyChain):
    chain = [has_unit, has_outcome]

  class has_unit_text(PropertyChain):
    chain = [has_unit, has_text]

  class assessment_of(DataProperty):
    range = [str]

  class has_advisable(ObjectProperty, TransitiveProperty, AsymmetricProperty):
    domain = [Unit]
    range = [Unit]
    #chain = [has_prereq, has_advisable]

  class contacttype(FunctionalProperty, DataProperty):
    range = [str]

  class hour(FunctionalProperty, DataProperty):
    range = [int]


onto.save(file = "handbook.owl", format = "rdfxml")