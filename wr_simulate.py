## Monte-Carlo Simulations
import os
import pickle
import random
import argparse
import csv

import numpy as np
import pandas as pd
import squigglepy as sq

from datetime import date
from email.policy import default
from scipy import stats
from pprint import pprint
from functools import partial
from collections import defaultdict

parser = argparse.ArgumentParser(description='Generate welfare ranges')
parser.add_argument('--species', type=str, help="What species do you want to simulate the welfare range of?")
parser.add_argument('--unknown_prob', type=float, help="What probability do you assign Unknown judgements for this species?", default=0)
parser.add_argument('--weight_no', type=str, help="Do you want to give non-zero probability to lean no and likely no?")
parser.add_argument('--hc_weight', type=float, help="What weight do high-confidence proxies get relative to other proxies?")
parser.add_argument('--scenarios', type=int, help='How many Monte Carlo simulations to run?', default=10000)
parser.add_argument('--csv', type=str, help='Define the relative path to the CSV with the species scores information')
parser.add_argument('--path', type=str, help='Define a custom path for the saved model outputs', default='')
parser.add_argument('--save', type=bool, help='Set to False to not save (overwrite) model outputs', default=True)
parser.add_argument('--update_every', type=int, help='How many steps to run before updating?', default=1000)
parser.add_argument('--verbose', type=bool, help='Set to True to get scenario-specific output', default=False)
args = parser.parse_args()

SPECIES = args.species
UNKNOWN_PROB = args.unknown_prob
WEIGHT_NO = args.weight_no
HC_WEIGHT = args.hc_weight
N_SCENARIOS = args.scenarios
VERBOSE = args.verbose
CSV = args.csv
SAVE = args.save
PATH = args.path
update_every = args.update_every

SENT_SPECIES = ['bees', 'cockroaches', 'fruit_flies', 'ants', \
            'c_elegans', 'crabs', 'crayfish', 'earthworms', \
            'sea_hares', 'moon_jellyfish', 'spiders', 'octopuses', \
            'plants', 'prokaryotes', 'protists', 'chickens', \
            'cows', 'humans', 'sometimes_operates', 'bsf', \
            'carp', 'salmon', 'silkworms', 'pigs']

SCENARIO_RANGES = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99]  # Generate printed output for these percentiles

judgements = pd.read_csv(os.path.join('input_data', 'WR Judgments.csv'))

hc_csv = os.path.join('input_data', 'WR High-Confidence Proxies.csv')
hc_proxies = set()
with open(hc_csv, newline='') as f:
    reader = csv.reader(f)
    hc_proxies_lists = list(reader)
for item in hc_proxies_lists:
    hc_proxies.add(item[0])

sent_hc_csv = os.path.join('input_data', 'Sentience High-Confidence Proxies.csv')
sent_hc_proxies = set()
with open(sent_hc_csv, newline='') as f:
    reader = csv.reader(f)
    sent_hc_proxies_lists = list(reader)
for item in sent_hc_proxies_lists:
    sent_hc_proxies.add(item[0])

overlap_csv = os.path.join('input_data', 'Proxy Overlap.csv')

overlap_dict = {}
with open(overlap_csv) as f:
    reader = csv.reader(f, delimiter=',')
    for idx, rec in enumerate(reader):
        if idx == 0:
            continue
        else:
            sent_proxy = rec[0].strip()
            in_both = rec[1].strip()
            corr_proxy = rec[2].strip()
            if in_both == "y":
                if corr_proxy not in overlap_dict:
                    overlap_dict[corr_proxy] = []
                overlap_dict[corr_proxy].append(sent_proxy)

if WEIGHT_NO == "Yes":
    judgment_prob_map = {'likely no': {'lower': 0, 'upper': 0.25},
                    'lean no': {'lower': 0.25, 'upper': 0.50},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': UNKNOWN_PROB}
else:
    judgment_prob_map = {'likely no': {'lower': 0, 'upper': 0},
                    'lean no': {'lower': 0, 'upper': 0},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': UNKNOWN_PROB}

species_scores = judgements[["proxies", SPECIES]]

simulated_probs = {}
simulated_scores = {}

if SPECIES in SENT_SPECIES:
    sent_scores = pickle.load(open('{}_simulated_scores.p'.format(os.path.join('output_data', "sent_{}".format(SPECIES))), 'rb'))

for proxy in species_scores["proxies"].to_list():
    simulated_probs[proxy] = []
    simulated_scores[proxy] = []

for s in range(N_SCENARIOS):
    if s % update_every == 0:
        if VERBOSE:
            print('-')
            print('### SCENARIO {} ###'.format(s + 1))
        else:
            print('... Completed {}/{}'.format(s + 1, N_SCENARIOS))

    #Set up for iteration over proxies
    num_proxies = len(species_scores)
    bern_probs = []
    proxies_arr = []
    judgements = species_scores[SPECIES]    
    
    #Iterate over proxies
    for ii in range(0,num_proxies):
        proxy = species_scores.proxies[ii]

        if SPECIES in SENT_SPECIES and proxy in overlap_dict.keys():
            sent_proxies = overlap_dict[proxy]
            a = 0
            count = 0
            for sent_proxy in sent_proxies:
                count += 1
                score = sent_scores[sent_proxy][s]     
                if proxy in hc_proxies:
                    if sent_proxy in sent_hc_proxies:
                        a += score
                    else:
                        a += score*HC_WEIGHT
                else:
                    if sent_proxy in sent_hc_proxies:
                        a += score/HC_WEIGHT
                    else:
                        a += score
            avg_score = a/count
            simulated_scores[proxy].append(avg_score)
        else:
            judgement = judgements[ii]

            if judgement == 'unknown':
                proxy_prob = judgment_prob_map[judgement]
            else:
                lower_prob = judgment_prob_map[judgement]['lower']
                upper_prob = judgment_prob_map[judgement]['upper']
                proxy_prob = random.uniform(lower_prob, upper_prob)
            bern_probs.append(proxy_prob)
            proxies_arr.append(proxy)
    
    #Obtain bernoulli draws 
    num_non_sent_proxies = len(bern_probs)
    draws = stats.bernoulli.rvs(bern_probs,size=num_non_sent_proxies)
    
    #Store bernoulli draw results
    for ii in range(0,num_non_sent_proxies):

        proxy = proxies_arr[ii]  
        has_proxy = draws[ii]
        if proxy in hc_proxies:
            score = HC_WEIGHT*has_proxy
        else:
            score = has_proxy
        simulated_probs[proxy].append(proxy_prob)
        simulated_scores[proxy].append(score)


if SAVE:
    print('... Saving 1/1')
    pickle.dump(simulated_scores, open('{}simulated_scores.p'.format(PATH), 'wb'))

    