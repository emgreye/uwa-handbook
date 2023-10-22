from owlready2 import *
import json

onto = get_ontology("http://www.example.org/handbook.owl")

with onto:
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
    domain =[Unit | Major]
    range = [Board]

  class has_prereq(ObjectProperty, TransitiveProperty):
    domain = [Unit | Major]
    range = [Unit | Course]

  class level(DataProperty, FunctionalProperty):
    range = [int]

  class credit(DataProperty, FunctionalProperty):
    range = [int]

  class has_school(ObjectProperty, FunctionalProperty):
    domain = [Unit | Major]
    range = [School]

  class has_mode(ObjectProperty):
    domain = [Unit | Major]
    range = [Mode]

  class desc(DataProperty, FunctionalProperty):
    range = [str]

  class has_text(DataProperty):
    range = [str]

  class has_outcome(DataProperty):
    domain = [Unit | Major]
    range = [str]

  class has_bridge(ObjectProperty):
    domain = [Major]
    range = [Unit]  

  class has_unit(ObjectProperty):
    domain = [Major]
    range = [Unit] 

  #class has_unit_outcome(DataProperty):
  #  domain = [Major]
  #  range = [str]
  #  chain = [has_unit,has_outcome]

  #class has_unit_text(PropertyChain([has_unit, [has_text]])):
  #  pass

  class has_assessment(DataProperty):
    range = [str]

  class has_advisable(ObjectProperty, TransitiveProperty):
    domain = [Unit]
    range = [Unit]
    #chain = [has_prereq, has_advisable]

  class contacttype(FunctionalProperty, DataProperty):
    range = [str]

  class hour(FunctionalProperty, DataProperty):
    range = [int]

  with open("units.json", encoding='utf-8') as file:
        u = json.load(file)

  with open("majors.json", encoding='utf-8') as file:
        m = json.load(file)



  for uniti in u:
    unit = Unit(uniti, namespace = onto)
    if ('outcomes' in u[uniti] ):
      for outcome in u[uniti]['outcomes']:
        unit.has_outcome.append(outcome)
    if ('prerequisites_cnf' in u[uniti] ):
      for prer in u[uniti]['prerequisites_cnf']:
        for pre in prer:
          unit.has_prereq.append(Unit(pre, namespace = onto))
    if ('assessment' in u[uniti] ):
      for assess in u[uniti]['assessment']:
        unit.has_assessment.append(assess)
    if ('text' in u[uniti] ):
      for text in u[uniti]['text']:
        unit.has_text.append(text)

  for majori in m:
    major = Major(majori, namespace = onto)
    for unit in m[majori]['units']:
      unitv = Unit(unit, namespace = onto)
      for outcome in unitv.has_outcome:
        # manually add unit outcome because chain property doesn't work
        major.has_outcome.append(outcome)
      for text in unitv.has_text:
        # manually add unit text because chain property doesn't work
        major.has_text.append(text)
      major.has_unit.append(Unit(unit, namespace = onto))
    if ('outcomes' in m[majori] ):
      for outcome in m[majori]['outcomes']:
        major.has_outcome.append(outcome)

  sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True)


onto.save(file = "handbook.owl", format = "owl")