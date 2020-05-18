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

#QUESTIONS = [('Is RNA in test neuropil?', ('no', 'yes')), ('Is protein in neuropil?', ('no', 'yes')), ('Comments', '')]
QUESTIONS = [
           RadioQuestion('Level of expression',
                         ('none', 'low', 'high')),
           TextQuestion('What is the problem on this image?',
                        'This is the initial answer text'),
           CheckQuestion('How is the distribution?',
                         ('Punctate', 'Diffuse', 'Nuclear')),
       ]
