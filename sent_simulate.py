## Generates the simulated data for each species' sentience proxies
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

parser = argparse.ArgumentParser(description='Generate probability of sentience ranges')
parser.add_argument('--species', type=str, help="What species do you want to simulate the probability of sentience of?")
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

SCENARIO_RANGES = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99]  # Generate printed output for these percentiles

judgments = pd.read_csv(os.path.join('input_data', 'Sentience Judgments.csv'))

hc_csv = os.path.join('input_data', 'Sentience High-Confidence Proxies.csv')
hc_proxies = set()
with open(hc_csv, newline='') as f:
    reader = csv.reader(f)
    hc_proxies_lists = list(reader)
for item in hc_proxies_lists:
    hc_proxies.add(item[0])

if WEIGHT_NO == "Yes":
    judgment_prob_map = {'likely no': {'lower': 0, 'upper': 0.25},
                    'lean no': {'lower': 0.25, 'upper': 0.50},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': UNKNOWN_PROB, 'yes': 1, 'na': 0}
else:
    judgment_prob_map = {'likely no': {'lower': 0, 'upper': 0},
                    'lean no': {'lower': 0, 'upper': 0},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': UNKNOWN_PROB, 'yes': 1, 'na': 0}

species_scores = judgments[["proxies", SPECIES]]

simulated_probs = {}
simulated_scores = {}

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
    bern_probs = []
    proxies_arr = []
    num_proxies = len(species_scores)
    judgements = species_scores[SPECIES]
    
    for ii in range(0,num_proxies):
        proxy = species_scores.proxies[ii]

        judgment = judgements[ii]
        judgment = judgment.lower()


        if judgment in {'unknown', 'yes', 'na'}:
            proxy_prob = judgment_prob_map[judgment]
        else:
            lower_prob = judgment_prob_map[judgment]['lower']
            upper_prob = judgment_prob_map[judgment]['upper']
            proxy_prob = random.uniform(lower_prob, upper_prob)
            
        bern_probs.append(proxy_prob)
        proxies_arr.append(proxy)

    #Obtain bernoulli draws         
    draws = stats.bernoulli.rvs(bern_probs,size=len(bern_probs))
    
    #Store bernoulli draw results        
    for ii in range(0,num_proxies):
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