import nltk
nltk.download('cmudict')
nltk.download('gutenberg')
from nltk.corpus import cmudict
from nltk.corpus import gutenberg
import pyphen
import random
import collections
import re
import os

os.environ['NLTK_DATA'] = r'C:\Users\arash\OneDrive\Desktop\py\Random Word Generator\corpus_text'

# Initialize the CMU Pronouncing Dictionary
d = cmudict.dict()
# Initialize Pyphen
dic = pyphen.Pyphen(lang='en')

VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"
LETTER_COMBINATIONS = ["ch", "sh", "th", "qu", "ng", "tr", "st", "sl", "cl"]
COMMON_ONSETS = ["", "s", "c", "p", "t", "b", "d", "k", "g", "f", "v", "th", "sh", "ch", 
                 "m", "n", "r", "l", "h", "w", "y", "j", "qu", "wh", "ph", "gh", "kn", 
                 "wr", "sw", "st", "sp", "sk", "sm", "sn", "sl", "cl", "pl", "fl", "bl", 
                 "gl", "pr", "br", "tr", "dr", "cr", "gr", "tw", "dw", "cw", "gw", "sch", 
                 "scr", "shr", "sph", "spl", "spr", "squ", "str", "thr"]
COMMON_CODAS = ["", "t", "d", "k", "g", "f", "v", "th", "s", "z", "sh", "ch", "m", "n", 
                "ng", "r", "l", "w", "y", "x", "pt", "ct", "kt", "ft", "vt", "pht", "tch", 
                "ts", "dz", "cks", "x", "zz", "ss", "zz", "mm", "nn", "rr", "ll", "tt", 
                "dd", "rt", "rd", "lt", "ld", "nt", "nd", "rn", "rm", "rl", "rk", "rf", 
                "rv", "rp", "rb", "rg", "rc", "rk", "mp", "mb", "lp", "lb", "rp", "rb", 
                "sp", "st", "sk", "ft", "kt", "pt", "ct", "pht", "xt"]

def read_corpus():
    return ' '.join(gutenberg.words())

def count_syllables(word):
    return len([ph for ph in dic.inserted(word).split('-')])

def syllabify(word):
    return dic.inserted(word).split('-')

def split_syllable(syllable):
    onset = ""
    nucleus = ""
    coda = ""
    for i, letter in enumerate(syllable):
        if letter in VOWELS:
            nucleus = syllable[i:]
            break
        else:
            onset += letter
    for i, letter in reversed(list(enumerate(nucleus))):
        if letter not in VOWELS:
            coda = nucleus[i:]
            nucleus = nucleus[:i]
            break
    return onset, nucleus, coda

def calculate_onset_coda_frequency(corpus):
    words = re.findall(r'\b\w+\b', corpus)
    onsets = []
    codas = []
    for word in words:
        syllables = syllabify(word)  # You would need to implement this function
        for syllable in syllables:
            onset, nucleus, coda = split_syllable(syllable)  # You would need to implement this function
            onsets.append(onset)
            codas.append(coda)
    onset_frequency = collections.Counter(onsets)
    coda_frequency = collections.Counter(codas)
    return onset_frequency, coda_frequency

def calculate_letter_frequency(corpus):
    frequency = collections.defaultdict(lambda: 1)  # Default frequency is 1
    for i in range(len(corpus) - 1):
        pair = corpus[i:i+2].lower()  # Convert to lowercase
        if pair[1] not in " .'":  # Exclude spaces, periods, and single quotation marks
            frequency[pair] += 1
    total = sum(frequency.values())
    for pair in frequency:
        frequency[pair] /= total
    # Add a small constant to the frequency of each consonant and vowel
    for c in CONSONANTS + VOWELS:
        frequency[c] += 0.01
    return frequency

def calculate_syllable_frequency(corpus):
    common_words = ['a', 'an', 'of', 'the', 'and', 'in', 'is', 'on', 'as', 'I', 'be', 'or']
    words = re.findall(r'\b\w+\b', corpus)
    words = [word for word in words if word not in common_words]
    syllable_counts = [count_syllables(word) for word in words]
    frequency = collections.Counter(syllable_counts)
    total = sum(frequency.values())
    for count in frequency:
        frequency[count] /= total
    return frequency


def generate_syllable_length(frequency):   
    syllable_lengths = list(frequency.keys())
    # Limit the maximum number of syllables
    max_syllables = max(syllable_lengths)
    syllable_lengths = [length for length in syllable_lengths if length <= max_syllables]
    probabilities = [frequency[length] for length in syllable_lengths]
    length = random.choices(syllable_lengths, weights=probabilities, k=1)[0]
    return length

def generate_syllable(frequency, syllable_frequency, onset_frequency, coda_frequency):
    length = generate_syllable_length(syllable_frequency)
    syllable = ""
    for _ in range(length):
        onset = random.choices(
            list(onset_frequency.keys()),
            weights=[onset_frequency.get(c, 0) for c in onset_frequency],
            k=1
        )[0]
        nucleus = random.choices(
            VOWELS,
            weights=[frequency.get(v, 0) for v in VOWELS],
            k=1
        )[0]
        coda = random.choices(
            list(coda_frequency.keys()),
            weights=[coda_frequency.get(c, 0) for c in coda_frequency],
            k=1
        )[0]
        syllable += onset + nucleus + coda
    return syllable

def generate_word(frequency, syllable_frequency, onset_frequency, coda_frequency):
    # Generate a syllable length for the entire word
    syllables = generate_syllable_length(syllable_frequency)
    word = ""
    for _ in range(syllables):
        next_syllable = generate_syllable(frequency, syllable_frequency, onset_frequency, coda_frequency)
        # If the coda of the current syllable and the onset of the next syllable form an unpronounceable sequence, add a vowel
        if word and word[-1] + next_syllable[0] in ["dcd", "gj", "cb", "fp", "tv", "sz"]:
            word += random.choice(VOWELS)
        word += next_syllable
    return word

def generate_words(num_words):
    # Read corpus from a text file
    corpus = read_corpus()
    frequency = calculate_letter_frequency(corpus)
    syllable_frequency = calculate_syllable_frequency(corpus)
    onset_frequency, coda_frequency = calculate_onset_coda_frequency(corpus)
    words = []
    while len(words) < num_words:
        word = generate_word(frequency, syllable_frequency, onset_frequency, coda_frequency)
        if count_syllables(word) > 1:  # Skip one-syllable words
            words.append(word)
    return words

# The script ends with a call to the `generate_words` function to generate and print out 10 random words. The path to the corpus file is specified as an argument to this function.
words = generate_words(10)
for word in words:
    print(word)


# In this code, syllabify is a function that would split a word into syllables, and split_syllable is a function that would split a 
# syllable into its onset, nucleus, and coda. You would need to implement these functions based on the rules of English phonotactics.

# Please note that this is a simplified approach and may not cover all the complexities of English phonotactics. 
# For a more accurate model, you might want to consider using a machine learning approach or a more sophisticated linguistic model. 
# Also, the syllabify and split_syllable functions are placeholders and you would need to implement these based on the rules of 
# English phonotactics. Implementing these functions could be quite complex as English syllabification rules are not straightforward 
# and can depend on various factors such as stress, morpheme boundaries, and more. If you’re interested in this area, you might want 
# to look into more advanced techniques such as machine learning or linguistic models.

# English phonotactics is a complex subject and the rules for syllabification and onset-nucleus-coda splitting can vary depending on 
# the specific dialect and even individual speaker. The above implementation is a very basic one and may not work correctly for all English words. 
# For a more accurate implementation, you might want to use a specialized library such as nltk or pyphen. These libraries have more sophisticated 
# algorithms for syllabification and can handle a wider range of English words.

# There are a few areas where the script could be improved:
# 1- Syllabification and Phonotactics: The script currently assumes placeholder functions for syllabify and split_syllable, which are supposed to split a word into syllables and a syllable into its onset, nucleus, and coda, respectively. Implementing these functions could be quite complex as English syllabification rules are not straightforward and can depend on various factors such as stress, morpheme boundaries, and more. You might want to look into more advanced techniques such as machine learning or linguistic models for a more accurate model.
# 2- Unpronounceable Sequences: The script currently checks for a few specific unpronounceable sequences of consonants and adds a vowel if such a sequence is found. This is a very simplistic approach and might not cover all unpronounceable sequences in English. A more sophisticated model of English phonotactics would be needed to accurately predict which sequences of consonants are unpronounceable.
# 3- Letter Frequency Calculation: The script calculates the frequency of each pair of letters in the corpus. However, it does not take into account the position of the letters in the word (i.e., whether they are at the beginning, middle, or end of the word). This could potentially affect the accuracy of the generated words.
# 4- Syllable Length Generation: The script generates a random syllable length based on the frequency distribution of syllable lengths in the corpus. However, it does not take into account the fact that the syllable length of a word can be influenced by factors such as the word's stress pattern and morphological structure.
# 5- Error Handling: The script currently does not have any error handling. For example, it does not check whether the corpus file exists and can be read, or whether the number of words to generate is a positive integer.
# 6- Code Modularity: The script could be made more modular by encapsulating the entire word generation process in a class. This would make the code easier to read and maintain, and it would also make it easier to reuse the word generation functionality in other parts of a larger program.
# 7- Documentation: While the script has some comments explaining what each function does, it could benefit from more detailed documentation. For example, the expected inputs and outputs for each function could be documented, and the overall logic of the word generation process could be explained in more detail. This would make the script easier to understand for other developers.
# 8- Testing: The script currently does not have any tests. Adding tests would help ensure that the script works as expected and makes it easier to catch and fix bugs. Tests could be added for individual functions as well as for the overall word generation process.


#This code uses the nltk.corpus.cmudict module, which is a pronouncing dictionary for North American English. It uses the Carnegie Mellon University Pronouncing Dictionary format. The pyphen library is a pure Python module to hyphenate text using existing Hunspell hyphenation dictionaries.

#Please note that you need to install the nltk and pyphen libraries if you haven’t already. You can do this using pip:

#pip install nltk pyphen

#Also, you need to download the cmudict corpus for nltk. You can do this in Python:

#Python

#import nltk
#nltk.download('cmudict')