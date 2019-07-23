
import nltk
from nltk.corpus import brown as words

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

try:
    word_list = words.words()
except LookupError:
    nltk.download("brown")  # The standard English corpus includes a lot of things I don't consider words, so I use the brown corpus instead.
    word_list = words.words()

word_set = set(map(str.lower, word_list))

word_set  = word_set - set(["b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"])
word_list = list(word_set)
