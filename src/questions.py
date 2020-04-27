#Is gene expressed in NBs?
#Obvious transcriptional regulation?
#Obvious post-transcriptional regulation?
#Is data acceptable?

## FORMAT OF QUESTIONS FILE
##
##   The questions file is a python file with a QUESTIONS variable.
##   This QUESTIONS variable must be a list, of tuples with two
##   elements.  Each tuple defines an individual question.
##
##   The first element in the question tuple must be a string and is
##   the text for the actual question.  The second element in the
##   tuple specifies the answer type and its initial value: if it is a
##   string then the answer is a text box; if it is a tuple of strings
##   then it is a group of radio buttons.

QUESTIONS = [('RNA expressed?', ('no', 'progeny', 'NB', 'both')), ('Protein expressed?', ('no', 'progeny', 'NB', 'both')), ('Punctate?', ('no', 'yes')), ('Comments', '')]
