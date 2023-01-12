# Run Program to Make & Store Simulations
import os
import csv
import platform
import pandas as pd
import warnings
import user_inputs
import pickle

warnings.filterwarnings('ignore')

WR_SPECIES = ['pigs', 'chickens', 'carp', 'salmon', 'octopuses', 'shrimp', 'crabs', 'crayfish', 'bees', 'bsf', 'silkworms']

SENT_SPECIES = ['bees', 'cockroaches', 'fruit_flies', 'ants', \
            'c_elegans', 'crabs', 'crayfish', 'earthworms', \
            'sea_hares',  'spiders', 'octopuses', 'chickens', \
            'cows', 'sometimes_operates', 'bsf', \
            'carp', 'salmon', 'silkworms', 'pigs']

wr_default_unknowns = {'pigs': 0, 'chickens': 0, 'carp': 0, 'salmon': 0, 
                            'octopuses': 0, 'shrimp': 0, 'crabs': 0, 'crayfish': 0, 'bees': 0,
                            'bsf': 0, 'silkworms': 0}

sent_default_unknowns = {'bees': 0, 'cockroaches': 0, 'fruit_flies': 0, 'ants':0, \
            'c_elegans': 0, 'crabs': 0, 'crayfish': 0, 'earthworms': 0, \
            'sea_hares': 0, 'spiders': 0, 'octopuses': 0, 'chickens': 0, \
            'cows': 0, 'sometimes_operates': 0, 'bsf': 0, \
            'carp': 0, 'salmon': 0, 'silkworms': 0, 'pigs': 0}

## Sentience 
print("For the PROBABILITY OF SENTIENCE...")
s_unknowns = user_inputs.assign_unknowns(SENT_SPECIES, sent_default_unknowns)
s_weight_nos = user_inputs.choose_nonzero_nos("sentience")
s_hc_weight = user_inputs.choose_hc_weight("sentience")

S_PARAMS = {'N_SCENARIOS': 10000, 'UPDATE_EVERY': 1000, "WEIGHT_NOS": s_weight_nos, "HC_WEIGHT": s_hc_weight}

## Welfare Ranges 
print("For the WELFARE RANGES...")
wr_unknowns = user_inputs.assign_unknowns(WR_SPECIES, wr_default_unknowns)
wr_weight_nos = user_inputs.choose_nonzero_nos("welfare ranges")
wr_hc_weight = user_inputs.choose_hc_weight("welfare ranges")

WR_PARAMS = {'N_SCENARIOS': 10000, 'UPDATE_EVERY': 100, "WEIGHT_NOS": wr_weight_nos, "HC_WEIGHT": wr_hc_weight}

def run_cmd(cmd):
    print(cmd)
    os.system(cmd)

def simulate_scores(species, params, s_or_wr):
    print("### {} ###".format(s_or_wr.upper()))
    print('...Simulate all Scores for {}'.format(species))

    params['species'] = species

    if s_or_wr == "sentience":
        params['path'] = "sent_{}".format(species)
        params['unknown_prob'] = s_unknowns[species]
        run_cmd('python3 sent_simulate.py --species {species} --unknown_prob {unknown_prob} --weight_no {WEIGHT_NOS} --hc_weight {HC_WEIGHT} --scenarios {N_SCENARIOS} \
            --csv output_data/scores_{path}.csv --path "output_data/{path}_" --update_every {UPDATE_EVERY}'.format(**params))
    else:
        params['path'] = "wr_{}".format(species)
        params['unknown_prob'] = wr_unknowns[species]
        run_cmd('python3 wr_simulate.py --species {species} --unknown_prob {unknown_prob} --weight_no {WEIGHT_NOS} --hc_weight {HC_WEIGHT} --scenarios {N_SCENARIOS} \
            --csv output_data/scores_{path}.csv --path "output_data/{path}_" --update_every {UPDATE_EVERY}'.format(**params))

if platform.system() == 'Darwin' or platform.system() == 'Linux':
    run_cmd('rm -rf output_data')
    run_cmd('mkdir output_data')
elif platform.system() == 'Windows':
    run_cmd('rmdir /Q /S output_data')
    run_cmd('mkdir output_data')
else:
    raise ValueError('Platform `{}` not supported'.format(platform.system()))

pickle.dump(s_unknowns, open(os.path.join('input_data', 'Sentience Unknown Probabilities.p'), 'wb'))
pickle.dump(S_PARAMS, open(os.path.join('input_data', 'Sentience Parameters.p'), 'wb'))
pickle.dump(wr_unknowns, open(os.path.join('input_data', 'Welfare Range Unknown Probabilities.p'), 'wb'))
pickle.dump(WR_PARAMS, open(os.path.join('input_data', 'Welfare Range Parameters.p'), 'wb'))

for species in SENT_SPECIES:
    simulate_scores(species, S_PARAMS, "sentience")

for species in WR_SPECIES:
    simulate_scores(species, S_PARAMS, "welfare ranges")

print('...Launching sentience notebook')
if platform.system() == 'Darwin' or platform.system() == 'Linux':
    run_cmd('jupyter notebook "sentience_models.ipynb"') 
elif platform.system() == 'Windows':
    run_cmd('python -m notebook "sentience_models.ipynb"') 
else:
    raise ValueError('Platform `{}` not supported'.format(platform.system()))

print('...Launching welfare range notebook')
if platform.system() == 'Darwin' or platform.system() == 'Linux':
    run_cmd('jupyter notebook "wr_models.ipynb"') 
elif platform.system() == 'Windows':
    run_cmd('python -m notebook "wr_models.ipynb"') 
else:
    raise ValueError('Platform `{}` not supported'.format(platform.system()))

