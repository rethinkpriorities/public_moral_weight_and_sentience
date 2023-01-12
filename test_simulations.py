## tests for the sentience and welfare range simulations
import math
import scipy.stats 
import csv 
import os
import pandas as pd
import numpy as np
import pickle

SENT_SPECIES = ['bees', 'cockroaches', 'fruit_flies', 'ants', \
            'c_elegans', 'crabs', 'crayfish', 'earthworms', \
            'sea_hares', 'spiders', 'octopuses', 'chickens', \
            'cows', 'sometimes_operates', 'bsf', \
            'carp', 'salmon', 'silkworms', 'pigs']

WEIGHT_NOS = "Yes"

def test_sentience_scores(data, HC_WEIGHT, SPECIES):
    # set up
    judgments = pd.read_csv(os.path.join('input_data', 'Sentience Judgments.csv'))
    hc_csv = os.path.join('input_data', 'Sentience High-Confidence Proxies.csv')
    hc_proxies = set()
    with open(hc_csv, newline='') as f:
        reader = csv.reader(f)
        hc_proxies_lists = list(reader)
    for item in hc_proxies_lists:
        hc_proxies.add(item[0])
    if WEIGHT_NOS == "Yes":
        judgments_map = {'likely no': {'lower': 0, 'upper': 0.25},
                    'lean no': {'lower': 0.25, 'upper': 0.50},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': 0, 'yes': 1, 'na': 0} # unknown 0 by default but this changes by species
    else:
        judgments_map = {'likely no': {'lower': 0, 'upper': 0},
                    'lean no': {'lower': 0, 'upper': 0},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': 0, 'yes': 1, 'na': 0}
    pass_test = True
    count_uncertain_proxies = 0
    outside_int = 0
    for species in SPECIES:          
        judgments_dict = judgments[['proxies', species]]
        species_scores = data[species]["Scores"]
        lst_outside = []
        for idx, row in judgments_dict.iterrows():
            proxy = row['proxies']
            judgment = row[species]
            scores_lst = species_scores[proxy]
            if proxy in hc_proxies:
                mean_prob = np.mean(np.array(scores_lst))/HC_WEIGHT
            else:
                mean_prob = np.mean(np.array(scores_lst))
            unknown_prob = data[species]["Unknown Prob"]
            if unknown_prob != 0:
                if judgment in {"yes", "na"}:
                    if mean_prob != judgments_map[judgment]:
                        print("Expected prob: {}".format(judgments_map[judgment]))
                        print("Broke at proxy {} for species {}".format(proxy, species))
                        pass_test = False
                else:
                    count_uncertain_proxies += 1
                    if judgment == "unknown":
                        ev = unknown_prob
                        s = math.sqrt((1-ev)*ev/len(scores_lst))
                    else:
                        ev = (judgments_map[judgment]['lower']+judgments_map[judgment]['upper'])/2
                        s = math.sqrt((1-ev)*ev/len(scores_lst))
                    if mean_prob < ev - 1.96*s or mean_prob > ev + 1.96*s:
                        outside_int += 1
                        lst_outside.append((species, proxy, judgment, mean_prob, ev))
            else: 
                if judgment in {"unknown", "yes", "na"}:
                    if mean_prob != judgments_map[judgment]:
                        print("Expected prob: {}".format(judgments_map[judgment]))
                        print("Broke at proxy {} for species {}".format(proxy, species))
                        pass_test = False
                else:
                    count_uncertain_proxies += 1
                    ev = (judgments_map[judgment]['lower']+judgments_map[judgment]['upper'])/2
                    s = math.sqrt((1-ev)*ev/len(scores_lst))
                    if mean_prob < ev - 1.96*s or mean_prob > ev + 1.96*s:
                        outside_int += 1
                        lst_outside.append((species, proxy, judgment, mean_prob, ev))
    p_value = 1 - scipy.stats.binom.cdf(outside_int, count_uncertain_proxies, 0.05)
    if pass_test:
        print("All proxies with zero/one probabilities have scores equal to their expected values")
    print("Number proxies whose proportion was outside 95% CI: {}".format(outside_int))
    print("Proportion of total proxies whose mean score was outside of the 95% CI: {}".format(round(outside_int/count_uncertain_proxies, 3)))
    print("Probability of getting > {}/{} proxies outside of their 95% CI: {}".format(outside_int, count_uncertain_proxies, round(p_value, 3)))
    if p_value < 0.05:
        pass_test = False
    if not pass_test:
        for failure in lst_outside:
            species, proxy, judgment, mean_prob, lower, upper = failure
            print("Species: {}".format(species))
            print("Outside int for proxy: {}".format(proxy))
            print("Judgment: {}".format(judgment))
            print("Avg. score was {}").format(mean_prob)
            print("Expected to be between {} and {}".format(lower, upper))
    print("Pass Test: ")
    return pass_test

def test_wr_scores(data, overlap_dict, WR_HC_WEIGHT, SENT_HC_WEIGHT, SPECIES):
    # set up
    judgments = pd.read_csv(os.path.join('input_data', 'WR Judgments.csv'))
    wr_hc_csv = os.path.join('input_data', 'WR High-Confidence Proxies.csv')
    wr_hc_proxies = set()
    with open(wr_hc_csv, newline='') as f:
        reader = csv.reader(f)
        wr_hc_proxies_lists = list(reader)
    for item in wr_hc_proxies_lists:
        wr_hc_proxies.add(item[0])

    sent_hc_csv = os.path.join('input_data', 'Sentience High-Confidence Proxies.csv')
    sent_hc_proxies = set()
    with open(sent_hc_csv, newline='') as f:
        reader = csv.reader(f)
        sent_hc_proxies_lists = list(reader)
    for item in sent_hc_proxies_lists:
        sent_hc_proxies.add(item[0])

    if WEIGHT_NOS == "Yes":
        judgments_map = {'likely no': {'lower': 0, 'upper': 0.25},
                    'lean no': {'lower': 0.25, 'upper': 0.50},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': 0} # unknown 0 by default but this changes by species
    else:
        judgments_map = {'likely no': {'lower': 0, 'upper': 0},
                    'lean no': {'lower': 0, 'upper': 0},
                    'lean yes': {'lower': 0.50, 'upper': 0.75},
                    'likely yes': {'lower': 0.75, 'upper': 1.00},
                    'unknown': 0}
    pass_test = True
    count_uncertain_proxies = 0
    outside_int = 0
    lst_outside = []
    for species in SPECIES:
        if species == "shrimp":
            continue
        else:
            sent_scores = pickle.load(open('{}_simulated_scores.p'.format(os.path.join('output_data', "sent_{}".format(species))), 'rb'))
            judgments_dict = judgments[['proxies', species]]
            wr_scores = data[species]["Scores"]
            
            for idx, row in judgments_dict.iterrows():
                proxy = row['proxies']
                wr_scores_lst = wr_scores[proxy]
                if proxy in overlap_dict.keys():
                    corresponding_sent_proxies = overlap_dict[proxy]
                    for s in range(len(wr_scores_lst)):
                        count = 0
                        a = 0
                        for sent_proxy in corresponding_sent_proxies:
                            count += 1
                            score = sent_scores[sent_proxy][s]
                            if proxy in wr_hc_proxies:
                                if sent_proxy in sent_hc_proxies:
                                    a += score
                                else:
                                    a += score*WR_HC_WEIGHT
                            else:
                                if sent_proxy in sent_hc_proxies:
                                    a += score/SENT_HC_WEIGHT
                                else:
                                    a += score
                        avg_score_s = a/count
                        if avg_score_s != wr_scores_lst[s]:
                            pass_test = False
                            print("Species: {}".format(species))
                            print("Test broke at proxy {} because its simulated values diverged from the sentience list at {}".format(proxy, sent_proxy))
                            print("Avg score: {}".format(avg_score_s))
                            print("Simulated score: {}".format(wr_scores_lst[s]))
                else:
                    judgment = row[species]
                    if proxy in wr_hc_proxies:
                        mean_prob = np.mean(np.array(wr_scores_lst))/WR_HC_WEIGHT
                    else:
                        mean_prob = np.mean(np.array(wr_scores_lst))
                    unknown_prob = data[species]["Unknown Prob"]
                    if unknown_prob != 0:
                        if judgment in {"yes", "na"}:
                            if mean_prob != judgments_map[judgment]:
                                print("Species: {}".format(species))
                                print("Expected prob: {}".format(judgments_map[judgment]))
                                print("Broke at proxy {} for species {}".format(proxy, species))
                                pass_test = False
                        else:
                            count_uncertain_proxies += 1
                            if judgment == "unknown":
                                ev = unknown_prob
                                s = math.sqrt((1-ev)*ev/len(wr_scores_lst))
                            else:
                                ev = (judgments_map[judgment]['lower']+judgments_map[judgment]['upper'])/2
                                s = math.sqrt((1-ev)*ev/len(wr_scores_lst))
                            if mean_prob < ev - 1.96*s or mean_prob > ev + 1.96*s:
                                outside_int += 1
                                lst_outside.append((species, proxy, judgment, mean_prob, ev))
                    else: 
                        if judgment in {"unknown", "yes", "na"}:
                            if mean_prob != judgments_map[judgment]:
                                print("Species: {}".format(species))
                                print("Expected prob: {}".format(judgments_map[judgment]))
                                print("Broke at proxy {} for species {}".format(proxy, species))
                                pass_test = False
                        else:
                            count_uncertain_proxies += 1
                            ev = (judgments_map[judgment]['lower']+judgments_map[judgment]['upper'])/2
                            s = math.sqrt((1-ev)*ev/len(wr_scores_lst))
                            if mean_prob < ev - 1.96*s or mean_prob > ev + 1.96*s:
                                outside_int += 1
                                lst_outside.append((species, proxy, judgment, mean_prob, ev - 1.96*s, ev + 1.96*s))

    p_value = 1 - scipy.stats.binom.cdf(outside_int, count_uncertain_proxies, 0.05)
    if pass_test:
        print("All proxies with zero/one probabilities have scores equal to their expected values")
    print("Number proxies whose proportion was outside 95% CI: {}".format(outside_int))
    print("Proportion of total proxies whose mean score was outside of the 95% CI: {}".format(round(outside_int/count_uncertain_proxies, 3)))
    print("Probability of getting > {}/{} proxies outside of their 95% CI: {}".format(outside_int, count_uncertain_proxies, round(p_value, 3)))
    if p_value < 0.05:
        pass_test = False
        for failure in lst_outside:
            species, proxy, judgment, mean_prob, lower, upper  = failure
            print("Species: {}".format(species))
            print("Outside int for proxy: {}".format(proxy))
            print("Judgment: {}".format(judgment))
            print("Avg. score was {}").format(mean_prob)
            print("Expected to be between {} and {}".format(lower, upper))
    print("Pass Test:")
    return pass_test
