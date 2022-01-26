# MKT
# purpose: query Flymine database to retrieve data of interest for genes and add to Josh's screen spreadsheet
# notes: Before running this script you will need to install intermine (!), see below
#
#     sudo easy_install intermine
#
# For further documentation you can visit:
#     http://intermine.readthedocs.org/en/latest/web-services/
#
# --USAGE--
# 1) Automatically executed afer questionnaire.py is completed.
# 2) Standalone
#   > python buildZegamiDatabase.py
#

from intermine.webservice import Service
service = Service("http://www.flymine.org/flymine/service")
import config
import importlib
import pandas as pd
import os
import sys

# link to location of the file mapping Bangalor or CPTI # to FBg #
flyline_file='Flyline_FBg_whole_genome.csv'

# add OMERO.Figure link and image ID to Zegami.tsv
zegami_df = pd.read_csv('figure_id_reference.csv')
zegami_df["OMEROFigurelink"]=str('https://omero1.bioch.ox.ac.uk/figure/file/')+zegami_df["figure_id"].astype(str)
zegami_df["image"]=zegami_df["figure_id"].astype(str)+str('.png')

# add whole genome of Flybase_ID to zegami.tsv
right = pd.read_csv('Flyline_FBg_whole_genome.csv')
zegami_df = pd.merge(zegami_df, right, how='outer', on=['Collection'])

# add questionnaire results to zegami.tsv
intDatasets = [os.path.join(root, name)
    for root, dirs, files in os.walk('answers')
    for name in files
    if name.endswith(".csv")]
intDatasets.append('answers/questionnaire_results.csv')

for x in intDatasets:
    print ('adding', x, 'to zegami.tsv file')
    right = pd.read_csv(x)
    zegami_df=pd.merge(zegami_df, right, how='left', on=['figure_id'])

    #get rid of extraneous data and notes
    for x in list(zegami_df.columns):
        try:
            if 'Unnamed' in x or 'Comments' in x:
                zegami_df = zegami_df.drop([x], axis = 1)
        except:
            pass

# add other datasets to zegami.tsv
extDatasets = [os.path.join('datasets/externalDatasets', x) for x in os.listdir('datasets/externalDatasets') if x.endswith('.csv') if not x.startswith('.')]

for x in extDatasets:
    print ('adding', x, 'to Zegami.tsv file')
    #left = zegami_df
    right = pd.read_csv(x)
    zegami_df = pd.merge(zegami_df, right, how='left', on=['Flybase_ID'])

# add intermine queries
queries = [os.path.join('datasets/testQueries', q) for q in os.listdir('datasets/testQueries') if q.endswith('.txt')]

for q in queries:
    print('performing query:', q)
    exec(open(q).read(), globals(), locals())
    zegami_df = pd.merge(zegami_df, config.query_df, how='left', on=['Flybase_ID'])

zegami_df.to_csv('zegami.tsv', sep='\t', index=False)
