import re
import sys
from random import random
from math import log
from collections import defaultdict

tri_counts=defaultdict(int) # counts of all trigrams in input

# Hyperparameter
alpha = 0.001

# Preprocessing function
# given a string, returns a lowercase version of the string with all digits converted to 0,
# all other characters except [a-z. ] removed, while prepending "##" and appending "#"
# eg. "Hi, I'm a sample input!" --> "##hi im a sample input#"
def preprocess_line(line):
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

def generate_file(tri_probs):
    f = open("data/model-1.en", "w")
    for item in tri_probs:
        f.write(item + "\t" + str(tri_probs[item]) + "\n")
    f.close()

generate_file(tri_counts)

def generate_dict(model_file):
    result_dict = defaultdict(int)
    with open(model_file) as f:
        for line in f:
            result_dict[line.split("\t")[0]] = float(line.split("\t")[1][:-1])
    return result_dict

#new_dict = generate_dict("data/model-br.en")
en_dict = generate_dict("data/model-1.en")
#es_dict = generate_dict("data/model-1.es")
#de_dict = generate_dict("data/model-1.de")

# don't count starting #s as part of the character count, but count the ending # (1 char)
# (and don't display any #s when you print the generated sentences)
def generate_from_LM(tri_probs):
    result = "##"
    output = ""
    iterations = 300
    for j in range(0, iterations):
        two_prev = result[-2:]
        if two_prev != "##" and two_prev[1] == "#":
            iterations -= j
            result += "\n##"
            output += "\n"
            continue
        trigrams = []
        for tri in tri_probs:
            if tri[:2] == two_prev:
                trigrams.append(tri)
        random_num = random()
        # print(two_prev)
        # print(trigrams)
        i = 0
        next_prob = tri_probs[trigrams[i]]
        while random_num > next_prob:
            # print(random_num, next_prob)
            random_num -= next_prob
            i += 1
            next_prob = tri_probs[trigrams[i]]
        result += trigrams[i][2]
        if trigrams[i][2] != "#":
            output += trigrams[i][2]
    print(output)

#generate_from_LM(new_dict)
generate_from_LM(en_dict)
#generate_from_LM(es_dict)
#generate_from_LM(de_dict)

def calculate_perplexity(testing_file, prob_dict):
    prob_values = []
    with open(testing_file) as f:
        for line in f:
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

print("Perplexity: ", calculate_perplexity("data/test", en_dict))
                


