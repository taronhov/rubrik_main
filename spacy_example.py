from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path

import spacy

from spacy import displacy

from IPython.core.display import display, HTML

nlp = spacy.load('en')                       # load model with shortcut link "en"
# nlp = spacy.load('en_core_web_sm')           # load model package "en_core_web_sm"

# Linguistic Features
# A "Doc" object is returned, which comes with a variety of annotations. 

# Tokenization: https://spacy.io/api/token
doc = nlp(u'This is a sentence, where Google is looking at buying some startup for $1 million.')

# Part-of-speech tagging: https://spacy.io/api/annotation#pos-tagging
for token in doc:
    print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_,
          token.shape_, token.is_alpha, token.is_stop)

# Syntactic dependency parser

# Noun chunks
doc = nlp(u"Autonomous cars shift insurance liability toward manufacturers")
for chunk in doc.noun_chunks:
    print(chunk.text, chunk.root.text, chunk.root.dep_,
          chunk.root.head.text)

# Navigating the parse tree
# spaCy uses the terms "head" and "child" to describe the words connected by a single arc in the dependency tree
doc = nlp(u"Autonomous cars shift insurance liability toward manufacturers")
for token in doc:
    print(token.text, token.dep_, token.head.text, token.head.pos_,
          [child for child in token.children])

doc = nlp(u"Autonomous cars shift insurance liability toward manufacturers")

# Iterating around the local tree

doc = nlp(u"bright red apples on the tree")
print([token.text for token in doc[2].lefts])  # ['bright', 'red']
print([token.text for token in doc[2].rights])  # ['on']
print(doc[2].n_lefts)  # 2
print(doc[2].n_rights)  # 1

doc = nlp(u"Credit and mortgage account holders must submit their requests")

root = [token for token in doc if token.head == token][0]
subject = list(root.lefts)[0]
for descendant in subject.subtree:
    assert subject is descendant or subject.is_ancestor(descendant)
    print(descendant.text, descendant.dep_, descendant.n_lefts,
          descendant.n_rights,
          [ancestor.text for ancestor in descendant.ancestors])

doc = nlp(u"Credit and mortgage account holders must submit their requests")
span = doc[doc[4].left_edge.i : doc[4].right_edge.i+1]
span.merge()
for token in doc:
    print(token.text, token.pos_, token.dep_, token.head.text)

# Visualizing dependencies

nlp = spacy.load('en_core_web_sm')
doc = nlp(u"Autonomous cars shift insurance liability toward manufacturers")
# displacy.render(doc, style='dep', jupyter=True) 

# Visualizing the entity recognizer
doc = nlp(u"""But Google is starting from behind. The company made a late push 
into hardware an,d Apple's Siri, available on iPhones, and Amazon's Alexa 
software, which runs on its Echo and Dot devices, have clear leads in consumer adoption.""")
# displacy.serve(doc, style='ent')


html = displacy.render(doc, style='dep')
display(HTML(html))

doc1 = nlp(u'This is a sentence.')
doc2 = nlp(u'This is another sentence.')
html = displacy.render([doc1, doc2], style='dep', page=True)



# Training and updating
# Training with annotations

# training data

train_data = [
    ("Uber blew through $1 million a week", [(0, 4, 'ORG')]),
    ("Android Pay expands to Canada", [(0, 11, 'PRODUCT'), (23, 30, 'GPE')]),
    ("Spotify steps up Asia expansion", [(0, 8, "ORG"), (17, 21, "LOC")]),
    ("Google Maps launches location sharing", [(0, 11, "PRODUCT")]),
    ("Google rebrands its business apps", [(0, 6, "ORG")]),
    ("look what i found on google!", [(21, 27, "PRODUCT")])]

train_data_2 = [('Who is Chaka Khan?', [(7, 17, 'PERSON')]),
              ('I like London and Berlin.', [(7, 13, 'LOC'), (18, 24, 'LOC')])]

TRAIN_DATA = [
    ('Who is Shaka Khan?', {
        'entities': [(7, 17, 'PERSON')]
    }),
    ('I like London and Berlin.', {
        'entities': [(7, 13, 'LOC'), (18, 24, 'LOC')]
    })
]

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int))
def main(model=None, output_dir=None, n_iter=100):
    """Load the model, set up the pipeline and train the entity recognizer."""
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model '%s'" % model)
    else:
        nlp = spacy.blank('en')  # create blank Language class
        print("Created blank 'en' model")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if 'ner' not in nlp.pipe_names:
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe('ner')

    # add labels
    for _, annotations in TRAIN_DATA:
        for ent in annotations.get('entities'):
            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER
        optimizer = nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            for text, annotations in TRAIN_DATA:
                nlp.update(
                    [text],  # batch of texts
                    [annotations],  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorise data
                    sgd=optimizer,  # callable to update weights
                    losses=losses)
            print(losses)

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
        print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print('Entities', [(ent.text, ent.label_) for ent in doc.ents])
            print('Tokens', [(t.text, t.ent_type_, t.ent_iob) for t in doc])


if __name__ == '__main__':
    plac.call(main)

    # Expected output:
    # Entities [('Shaka Khan', 'PERSON')]
    # Tokens [('Who', '', 2), ('is', '', 2), ('Shaka', 'PERSON', 3),
    # ('Khan', 'PERSON', 1), ('?', '', 2)]
    # Entities [('London', 'LOC'), ('Berlin', 'LOC')]
    # Tokens [('I', '', 2), ('like', '', 2), ('London', 'LOC', 3),
    # ('and', '', 2), ('Berlin', 'LOC', 3), ('.', '', 2)]
