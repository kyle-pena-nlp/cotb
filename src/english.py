
import nltk
from nltk.corpus import brown as words
from distance import hamming

letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

try:
    word_list = words.words()
except LookupError:
    nltk.download("brown")  # The standard English corpus includes a lot of things I don't consider words, so I use the brown corpus instead.
    word_list = words.words()

word_set = set(map(str.lower, word_list))

word_set  = word_set - set(["b", "c", "d", "e", "f", "g", "h", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"])
word_list = list(word_set)

def string_distance(a, b):
    dif_len = abs(len(a) - len(b))
    min_len = min(len(a),  len(b))
    truncated_a = a[:min_len]
    truncated_b = b[:min_len]
    return hamming(truncated_a, truncated_b) + dif_len

def smallest_distance_to_any_english_word(string):
    return min(string_distance(string, word) for word in word_list)