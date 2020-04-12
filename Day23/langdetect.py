import nltk
import pycountry
from nltk.stem import SnowballStemmer

phrase_one = "good morning"
phrase_two = "goeie more"

tc = nltk.classify.textcat.TextCat() 
guess_one = tc.guess_language(phrase_one)
guess_two = tc.guess_language(phrase_two)

guess_one_name = pycountry.languages.get(alpha_3=guess_one).name
guess_two_name = pycountry.languages.get(alpha_3=guess_two).name
print(guess_one_name)
print(guess_two_name)

stemmer = SnowballStemmer(guess_one_name.lower())
s1 = "walking"
print(stemmer.stem(s1))

guess_example = tc.guess_language("hello")
print(pycountry.languages.get(alpha_3=guess_example).name)
