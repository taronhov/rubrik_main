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

