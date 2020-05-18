# --USAGE--
# -Retrieves data from intermine query and passes it to global variable as a
#  Pandas dataframe
# -Requires the following modifications of the intermine code
#  1. create lists to store each query parameter
#  2. change print() to list.append()
#  3. pass lists to Pandas DataFrame
#  4. store pd.DataFrame object as global variable in config file 

from __future__ import print_function
from intermine.webservice import Service
service = Service("https://www.flymine.org/flymine/service")
query = service.new_query("Gene")
query.add_view("goAnnotation.ontologyTerm.name", "primaryIdentifier")
query.add_constraint("goAnnotation.ontologyTerm.namespace", "=", "biological_process", code="B")

name = []
goAnnotation = []
primaryIdentifier = []
for row in query.rows():
    name.append(row["name"]), goAnnotation.append(row["goAnnotation.ontologyTerm.name"]), primaryIdentifier.append(row["primaryIdentifier"])

# local code
import pandas as pd
import config

def dataframe():
    query_df = pd.DataFrame(
        {'Flybase_ID': primaryIdentifier,
         'goAnnotation': goAnnotation
        })

    config.query_df = query_df.groupby('Flybase_ID')['goAnnotation'].apply(';'.join).reset_index()
dataframe()
