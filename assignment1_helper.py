#Here are some libraries you're likely to use. You might want/need others as well.
import re
import sys
from random import random
from math import log
from collections import defaultdict

tri_counts=defaultdict(int) #counts of all trigrams in input

# Preprocessing function
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

alpha = 0.001

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

count = 0
sums = []

sorted_trigrams = sorted(tri_counts.keys())
for i in range(0, len(sorted_trigrams)):
    count += tri_counts[sorted_trigrams[i]]
    if (i+1) % 30 == 0:
        sums.append(count)
        count = 0

for i in range(0, len(sums)):
    for j in range(i*30, i*30 + 30):
        tri_counts[sorted_trigrams[j]] /= sums[i]


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
# for trigram in tri_counts.keys():
#     if trigram[:2] == "##":
#         print(trigram, ":", tri_counts[trigram])




# --- checking contents of tri_counts ---
# total = sum(tri_counts.values())
# print(total)

# t = 0
# for i in range(0, 30):
#     t += tri_counts[sorted_trigrams[i]]
#     print(sorted_trigrams[i], tri_counts[sorted_trigrams[i]])

# print(t)

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

new_dict = generate_dict("data/model-br.en")

def generate_from_LM(tri_probs):
    result = "##"
    iterations = 300
    for j in range(0, iterations):
        two_prev = result[-2:]
        if two_prev == ".#":
            iterations -= j
            result += "\n##"
            continue
        trigrams = []
        for tri in tri_probs:
            if tri[:2] == two_prev:
                trigrams.append(tri)
        random_num = random()
        print(two_prev)
        print(trigrams)
        i = 0
        next_prob = tri_probs[trigrams[i]]
        while random_num > next_prob:
            print(random_num, next_prob)
            random_num -= next_prob
            i += 1
            next_prob = tri_probs[trigrams[i]]
        result += trigrams[i][2]
    print(result)

generate_from_LM(new_dict)
    
    
