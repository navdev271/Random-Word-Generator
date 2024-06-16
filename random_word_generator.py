import random
import collections
import re

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

# The function `read_corpus(file_path)` opens a file at the given path and reads its content. 
# It's used to load the corpus of text that the script uses to calculate letter and syllable frequencies.
def read_corpus(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# The function `count_syllables(word)` takes a word as input and returns the number of syllables in that word. 
# It uses a simple algorithm that counts the number of vowel sequences in the word, with some adjustments for special cases like words ending in "e".
def count_syllables(word):
    word = word.lower()
    vowels = "aeiouy"
    count = 0
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if count == 0:
        count += 1
    return count

# The function `calculate_letter_frequency(corpus)` takes a corpus of text as input and returns a dictionary where the keys are pairs of letters 
# and the values are their relative frequencies in the corpus. It's used to calculate the probability of each letter pair occurring in the generated words.
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

# The function `calculate_syllable_frequency(corpus)` takes a corpus of text as input and returns a dictionary where the keys are syllable counts and the 
# values are their relative frequencies in the corpus. It's used to calculate the probability of each syllable count occurring in the generated words.
def calculate_syllable_frequency(corpus):
    words = re.findall(r'\b\w+\b', corpus)
    syllable_counts = [count_syllables(word) for word in words]
    frequency = collections.Counter(syllable_counts)
    total = sum(frequency.values())
    for count in frequency:
        frequency[count] /= total
    return frequency

# The function `generate_syllable_length(frequency)` takes a frequency distribution of syllable lengths as input and returns a random syllable length 
# based on that distribution. It's used to decide how many syllables each generated word should have.
def generate_syllable_length(frequency):
    syllable_lengths = list(frequency.keys())
    # Limit the maximum number of syllables
    max_syllables = max(syllable_lengths)
    syllable_lengths = [length for length in syllable_lengths if length <= max_syllables]
    probabilities = [frequency[length] for length in syllable_lengths]
    length = random.choices(syllable_lengths, weights=probabilities, k=1)[0]
    return length

# The function `generate_syllable(frequency, syllable_frequency)` takes two frequency distributions as input: one for letter pairs and one for syllable
# lengths. It returns a randomly generated syllable based on these distributions. The syllable is composed of an onset, a nucleus (vowel), and a coda, 
# chosen based on the frequency distributions.
def generate_syllable(frequency, syllable_frequency):
    length = generate_syllable_length(syllable_frequency)
    syllable = ""
    for _ in range(length):
        onset = random.choices(
            COMMON_ONSETS,
            weights=[frequency.get(c, 0) for c in COMMON_ONSETS],
            k=1
        )[0]
        nucleus = random.choices(
            VOWELS,
            weights=[frequency.get(v, 0) for v in VOWELS],
            k=1
        )[0]
        coda = random.choices(
            COMMON_CODAS,
            weights=[frequency.get(c, 0) for c in COMMON_CODAS],
            k=1
        )[0]
        syllable += onset + nucleus + coda
    return syllable

# The function `generate_word(frequency, syllable_frequency)` takes two frequency distributions as input: one for letter pairs and one for syllable lengths. 
# It returns a randomly generated word based on these distributions. The word is composed of one or more syllables, each generated by the `generate_syllable` function.
def generate_word(frequency, syllable_frequency):
    # Generate a syllable length for the entire word
    syllables = generate_syllable_length(syllable_frequency)
    word = ""
    for _ in range(syllables):
        next_syllable = generate_syllable(frequency, syllable_frequency)
        # If the coda of the current syllable and the onset of the next syllable form an unpronounceable sequence, add a vowel
        if word and word[-1] + next_syllable[0] in ["dcd", "gj", "cb", "fp", "tv", "sz"]:
            word += random.choice(VOWELS)
        word += next_syllable
    return word

# The function `generate_words(num_words, file_path)` takes the number of words to generate and the path to the corpus file as input. 
# It reads the corpus, calculates the frequency distributions, and generates the specified number of words. Each word is generated by the `generate_word` function. 
# The function returns a list of the generated words.
def generate_words(num_words, file_path):
    # Read corpus from a text file
    corpus = read_corpus(file_path)
    frequency = calculate_letter_frequency(corpus)
    syllable_frequency = calculate_syllable_frequency(corpus)
    return [generate_word(frequency, syllable_frequency) for _ in range(num_words)]

# The script ends with a call to the `generate_words` function to generate and print out 10 random words. The path to the corpus file is specified as an argument to this function.
words = generate_words(10, r"C:\Users\arash\OneDrive\Desktop\py\Random Word Generator\corpus_text")
for word in words:
    print(word)