## Ask the User for Model Assumption Inputs
import re
import copy


def assign_unknowns(SPECIES, default_unknowns):
    print("The list of species is: {}".format(SPECIES))
    change_probs = str(input("The default probability assigned to Unknown judgements is zero for all species. Do you want to change this for one or more species? Y/N "))
    change_probs = change_probs.strip()
    new_unknown_probs = copy.deepcopy(default_unknowns)
    if change_probs.lower() not in ["y", "n"]:
        change_probs = str(input("Invalid input, must be Y or N. Do you want to change this for one or more species? Y/N ")) 
    while change_probs.lower() == "y":
        str_to_change = str(input("Which species do you want non-zero judgements for? Enter a list: eg. salmon, pig, chicken. "))    
        lst_to_change = re.findall(r"[a-zA-Z]+", str_to_change)
        for species in lst_to_change:
            if species in new_unknown_probs:
                new_prob = float(input("What probability to assign to Unknowns for {}? ".format(species)))
                while new_prob <0 or new_prob > 1:
                    new_prob = float(input("Invalid probability (must be in [0,1]). Input again. "))
                new_unknown_probs[species] = new_prob
            else:
                print("{} is not in the species list. The species are: \n".format(species))
                print(SPECIES)
                new_species = input("Do you want to change the Unknown probability for another species? Y/N ")
                new_species = new_species.strip()
                if new_species.lower() == "y": 
                    str_to_change_2 = str(input("Which species do you want non-zero judgements for? Enter a list: eg. salmon, pig, chicken. "))  
                    lst_to_change_2 = re.findall(r"[a-zA-Z]+", str_to_change_2)
                    lst_to_change += lst_to_change_2
                
        change_probs = str(input("Do you want to change the unknown probability for any more species? Y/N "))
        change_probs = change_probs.strip()
    print("The assignments of unknown probabilities are: ")
    print(new_unknown_probs)
    return new_unknown_probs 


def choose_nonzero_nos(s_or_wr):
    weight_nos = str(input("Do you want to assign non-zero probabilities to species possessing {} proxies judged as 'Likely no' and 'Lean no'? Y/N ".format(s_or_wr)))

    weight_nos = weight_nos.strip()
    while weight_nos.lower() not in ["y", "n"]:
        weight_nos = str(input("Invalid input, must be Y or N. Do you want to assign non-zero probabilities to 'Likely no' or 'Lean no's? Y/N ")) 
        weight_nos = weight_nos.strip()

    if weight_nos.lower() == "y":
        return "Yes"
    else:
        return "No"

def choose_hc_weight(s_or_wr):
    weight_hc = float(input("What weight (number >= 1) do you want to give to proxies that we believe are highly relevant for {}? ".format(s_or_wr)))
    while weight_hc < 1:
        weight_hc = float(input("Invalid input, must be >= 1. What weight do you want to assign to high-confidence traits? ")) 
    return weight_hc
     
    