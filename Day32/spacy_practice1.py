import spacy

nlp = spacy.blank("en")

doc = nlp("I like tree kangaroos and narwhals.")

tree_kangaroos = doc[2:4]
print(tree_kangaroos.text)

tree_kangaroos_and_narwhals = doc[2:6]
print(tree_kangaroos_and_narwhals.text)
