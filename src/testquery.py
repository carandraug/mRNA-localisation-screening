#!/usr/bin/env python
from __future__ import print_function
from intermine.webservice import Service
service = Service("https://www.flymine.org/flymine/service")
query = service.new_query("Gene")
query.add_view("name", "goAnnotation.ontologyTerm.name")
query.add_constraint("goAnnotation.ontologyTerm.namespace", "=", "biological_process", code="B")

for row in query.rows():
    print(row["name"], row["goAnnotation.ontologyTerm.name"])
