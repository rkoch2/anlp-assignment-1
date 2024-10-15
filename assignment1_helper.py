import re
import sys
from random import random
from math import log
from collections import defaultdict

tri_counts=defaultdict(int) # counts of all trigrams in input

# Hyperparameter
alpha = 0.001
alpha2 = 0.08

def preprocess_line(line):
    ''' preprocess_line takes in a string and returns a modified version of the string,
    where all digits are converted to 0, all characters except [a-z. ] are removed, and
    "##" is prepending to the beginning of the string while "#" is appended to the end
    of it. eg. "Hi, I'm a sample input!" --> "##hi im a sample input#"

    In addition to what was specified in the handout, we added the ## and # at the beginning
    and end of the resulting string, respectively. Since this prepending/appending of the
    #s was an additional modification process for each of the lines, it made the most sense
    to us to keep all of these modifications contained within one function (for organization)
    and not add the #s in other functions.
    '''
    line = line.lower()
    result = "##"
    regex = "[a-z0-9. ]"
    for char in line:
        if re.findall(regex, char) != []:
            if re.findall("[1-9]", char):
                char = "0"
            result += char
    result += "#"
    return result

#here we make sure the user provides a training filename when
#calling this program, otherwise exit with a usage error.
if len(sys.argv) != 2:
    print("Usage: ", sys.argv[0], "<training_file>")
    sys.exit(1)

infile = sys.argv[1] #get input argument: the training file
model_file = "data/model-br.en"

with open(model_file) as f:
    for line in f:
        token = line.split("\t")[0]
        tri_counts[token] += alpha

#This bit of code gives an example of how you might extract trigram counts
#from a file, line by line. If you plan to use or modify this code,
#please ensure you understand what it is actually doing, especially at the
#beginning and end of each line. Depending on how you write the rest of
#your program, you may need to modify this code.

with open(infile) as f:
    for line in f:
        line = preprocess_line(line)
        for j in range(len(line)-2):
            trigram = line[j:j+3]
            tri_counts[trigram] += 1

sums = {}
sorted_trigrams = sorted(tri_counts.keys())

for trigram in sorted_trigrams:
    first_two_chars = trigram[:2]
    if sums.get(first_two_chars) == None:
        sums[first_two_chars] = 0
    sums[first_two_chars] += tri_counts[trigram]

for trigram in sorted_trigrams:
    tri_counts[trigram] /= sums.get(trigram[:2])

#Some example code that prints out the counts. For small input files
#the counts are easy to look at but for larger files you can redirect
#to an output file (see Lab 1).
# print("Trigram counts in ", infile, ", sorted alphabetically:")
# for trigram in sorted(tri_counts.keys()):
#     print(trigram, ": ", tri_counts[trigram])
# print("Trigram counts in ", infile, ", sorted numerically:")
# for tri_count in sorted(tri_counts.items(), key=lambda x:x[1], reverse = True):
#     print(tri_count[0], ": ", str(tri_count[1]))
# c = 0
# for trigram in tri_counts.keys():
#     if trigram[:2] == "ng":
#         print(trigram, ":", tri_counts[trigram])
#         c += tri_counts[trigram]
# print(c)

def generate_file(tri_probs, filename):
    ''' generate_file takes in a defaultdict of trigrams mapped to their probability
    values and a filename (as a string), and writes the trigrams and their probabilities
    to that file, with each line containing a trigram and probability value separated
    by a [tab].
    '''
    f = open(filename, "w")
    for item in tri_probs:
        f.write(item + "\t" + str(tri_probs[item]) + "\n")
    f.close()

def generate_dict(model_file):
    ''' generate_dict takes in a filename for a model file (where each line is a trigram
    and probability value separated by a [tab]) and returns a defaultdict for that model
    file, where trigrams are mapped to their probability values.
    '''
    result_dict = defaultdict(int)
    with open(model_file) as f:
        for line in f:
            # for each line in the model file, get the trigram and probability
            # (split by \t) and add to the result_dict
            result_dict[line.split("\t")[0]] = float(line.split("\t")[1][:-1])
    return result_dict

generate_file(tri_counts, "data/model-1.en")

model_br_dict = generate_dict("data/model-br.en")
en_dict = generate_dict("data/model-1.en")
es_dict = generate_dict("data/model-1.es")
de_dict = generate_dict("data/model-1.de")

def generate_from_LM(tri_probs, iterations):
    ''' generate_from_LM takes in tri_probs, a defaultdict of trigrams mapped to 
    their probabilities, and iterations, the number of characters that should be
    generated. Based on the probabilities in tri_probs, generate_from_LM returns
    a string of generated text.
    '''
    # result and output are the same except that result has starting/ending #s, while
    # output is a "clean" version (without the #s) that can be displayed
    result = "##"
    output = ""
    for j in range(0, iterations):
        two_prev = result[-2:]
        if two_prev != "##" and two_prev[1] == "#": # detects end of line
            iterations -= j
            result += "\n##"
            output += "\n"
            continue # begin a new line
        trigrams = [] # a list of trigrams that start with the two previous chars
        for tri in tri_probs:
            if tri[:2] == two_prev:
                trigrams.append(tri)
        random_num = random() # a random number between 0 and 1
        i = 0
        next_prob = tri_probs[trigrams[i]]
        while random_num > next_prob:
            # subtract the probability values from random_num until the next probability
            # value is greater than random_num. The trigram associated with the next probability
            # value is the "selected" trigram (from which the thrid char will be appended to result)
            random_num -= next_prob
            i += 1
            next_prob = tri_probs[trigrams[i]]
        result += trigrams[i][2] # append the third character of the selected trigram to result
        if trigrams[i][2] != "#": # append the third character to output if it is not a #
            output += trigrams[i][2]
    return output

phrase = " generated from model_br_dict "
print(f"{phrase:-^64}")
print(generate_from_LM(model_br_dict, 300))
phrase = " generated from en_dict "
print(f"\n{phrase:-^64}")
print(generate_from_LM(en_dict, 300))
#print("-------------------- generated from es_dict --------------------")
#print(generate_from_LM(es_dict, 300))
#print("-------------------- generated from de_dict --------------------")
#print(generate_from_LM(de_dict, 300))


def calculate_perplexity(testing_file, prob_dict):
    ''' calculate_perplexity takes in testing_file, a filename for a testing file,
    and prob_dict, a defaultdict of trigrams mapped to their probabilities. Using
    these probability values, calculate_perplexity returns a float representing
    the perplexity of the model represented by the prob_dict given the testing_file
    '''
    prob_values = [] # a list of probability values for each trigram in the testing file
    with open(testing_file) as f:
        for line in f: # filling the prob_values list with probabilities
            line = preprocess_line(line)
            for j in range(len(line)-2):
                trigram = line[j:j+3]
                if prob_dict[trigram]:
                    prob_values.append(prob_dict[trigram])
                else:
                    print("probability not found for trigram ", trigram)
    perplexity = 1
    for prob in prob_values:
        perplexity *= (prob ** (-1 / len(prob_values)))
    return perplexity

phrase = " calculating perplexity "
print(f"\n{phrase:-^64}")
testing_file = "data/test"
print("Perplexity using model_br_dict: ", calculate_perplexity(testing_file, model_br_dict))
print("Perplexity using en_dict: ", calculate_perplexity(testing_file, en_dict))
print("Perplexity using es_dict: ", calculate_perplexity(testing_file, es_dict))
print("Perplexity using de_dict: ", calculate_perplexity(testing_file, de_dict))


tri_counts=defaultdict(int)

model_file = "data/model-br.en"

with open(model_file) as f:
    for line in f:
        token = line.split("\t")[0]
        tri_counts[token] += alpha2

infile = "data/training2.en"
with open(infile) as f:
    for line in f:
        line = preprocess_line(line)
        for j in range(len(line)-2):
            trigram = line[j:j+3]
            tri_counts[trigram] += 1

sums = {}
sorted_trigrams = sorted(tri_counts.keys())

for trigram in sorted_trigrams:
    first_two_chars = trigram[:2]
    if sums.get(first_two_chars) == None:
        sums[first_two_chars] = 0
    sums[first_two_chars] += tri_counts[trigram]

for trigram in sorted_trigrams:
    tri_counts[trigram] /= sums.get(trigram[:2])

generate_file(tri_counts, "data/model-2.en")

en_dict2 = generate_dict("data/model-2.en")

testing_file = "data/devset.en"
phrase = " calculating perplexity of devset "
print(f"\n{phrase:-^64}")
print("Perplexity of devset using en_dict2: ", calculate_perplexity(testing_file, en_dict2))

testing_file = "data/test"
phrase = " calculating perplexity of test with adjusted alpha "
print(f"\n{phrase:-^64}")
print("Perplexity of test set using en_dict2: ", calculate_perplexity(testing_file, en_dict2))