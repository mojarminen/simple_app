# -*- coding: utf-8 -*-

import db
import estimator as estimator_module
import betting_strategy
import runner
import pickle
import random
import time
import sys

def median(lst):
    lst = sorted(lst)
    if len(lst) < 1:
            return None
    if len(lst) %2 == 1:
            return lst[((len(lst)+1)/2)-1]
    else:
            return float(sum(lst[(len(lst)/2)-1:(len(lst)/2)+1]))/2.0
        
def get_random_object():
    obj = {
#        'history_in_weeks': random.randint(10, 150),
        'history_in_matches': random.randint(10, 150),
        'start_weight': random.random(), # 0.0-1.0
        'end_weight': random.uniform(0.5, 1.0), # 0.5-1.0
        'over_power_threshold': random.randint(1,4) + random.random(), # 1.0-5.0
        'over_power_extra': random.uniform(0.0, 0.2), # 0.0-0.2
        'close_match_threshold': random.uniform(0.0, 0.5), # 0.0-0.5
        'close_match_trim': random.uniform(0.0, 0.4) # 0.0-0.4
    }
    
    if obj['end_weight'] < obj['start_weight']:
        obj['end_weight'] = 1.0
        
    return obj
        
if __name__ == '__main__':
        
    INITIAL_MONEY = 1000
    
    POPULATION_SIZE = 100
    MUTATION_FREQUENCY = 0.01 # portion of new genes mutated
    
    ESTIMATOR = estimator_module.direct

    BETTING_STRATEGY = betting_strategy.div_100 # betting_strategy.kelly_div_10, betting_strategy.div_10, betting_strategy.div_100, betting_strategy.bet_2, betting_strategy.bet_10

    # Load or create the initial population.
    population = []
    if len(sys.argv) >= 2:
        pickle_file = sys.argv[1]
        with open(pickle_file, 'rb') as f:
            population = pickle.load(f)

        while len(population) < POPULATION_SIZE:
            population.append([get_random_object(), None])

        if len(sys.argv) >= 3 and sys.argv[2] == 'reset':
            print 'RESETTING...'
            for idx in range(len(population)):
                population[idx][1] = None

    else:
        for idx in range(POPULATION_SIZE):
            population.append([get_random_object(), None])

    population_number = 1
    while True:
        print 'POPULATION', population_number
    
        # Evaluate the population.
        for idx, elem in enumerate(population):
        
            print str(idx+1) + '/' + str(POPULATION_SIZE)
        
            if elem[1] is None: # Only calculate value if not previously calculated
                ukko = elem[0]
                print ukko
            
                estimator_module.HISTORY_IN_MATCHES = ukko['history_in_matches']
                estimator_module.START_WEIGHT = ukko['start_weight']
                estimator_module.END_WEIGHT = ukko['end_weight']
                estimator_module.OVER_POWER_THRESHOLD = ukko['over_power_threshold']
                estimator_module.OVER_POWER_EXTRA = ukko['over_power_extra']
                estimator_module.CLOSE_MATCH_THRESHOLD = ukko['close_match_threshold']
                estimator_module.CLOSE_MATCH_TRIM = ukko['close_match_trim']
                
                winnings = []
                for season in range(2006, 2017): 
                    print '\tVEIKKAUSLIIGA ' + str(season) + '-' + str(season+1) + ': ',
                    money_left, matches = runner.play(INITIAL_MONEY, ESTIMATOR, BETTING_STRATEGY, league=u'Veikkausliiga', season=str(season))
                    print money_left
                    winnings.append(money_left - INITIAL_MONEY)
                print 'TOTAL:', sum(winnings)
                
                winnings = list(sorted(winnings))
                print 'winnings:', winnings
                population[idx][0]['winnings'] = winnings
                population[idx][1] = sum(winnings[:3])
            
            print 'SUM OF SMALLEST THREE:', population[idx][1]


        # Write population to file.
        with open('populations_veikkausliiga/' + time.strftime('%Y-%m-%d_%H:%M:%s') + '.pickle', 'wb') as f:
            pickle.dump(population, f)

        # Remove the worst 50 percent.
        population = list(reversed(list(sorted(population, key=lambda x: x[1]))))
        population = population[:len(population)/2]

        # Create offsprings.
        offsprings = []
        while len(population) + len(offsprings) < POPULATION_SIZE:
            parents = [
                population[random.randint(0,len(population)-1)],
                population[random.randint(0,len(population)-1)]
            ]
            
            mean_pseudo_parent = [
                {
                    'history_in_matches': (parents[0][0]['history_in_matches'] + parents[1][0]['history_in_matches'])/2,
                    'start_weight': (parents[0][0]['start_weight'] + parents[1][0]['start_weight'])/2,
                    'end_weight': (parents[0][0]['end_weight'] + parents[1][0]['end_weight'])/2,
                    'over_power_threshold': (parents[0][0]['over_power_threshold'] + parents[1][0]['over_power_threshold'])/2,
                    'over_power_extra': (parents[0][0]['over_power_extra'] + parents[1][0]['over_power_extra'])/2,
                    'close_match_threshold': (parents[0][0]['close_match_threshold'] + parents[1][0]['close_match_threshold'])/2,
                    'close_match_trim': (parents[0][0]['close_match_trim'] + parents[1][0]['close_match_trim'])/2
                }, 
                None
            ]
            
            parents.append(mean_pseudo_parent)
            
            offspring = [
                {
                    'history_in_matches': parents[random.randint(0, 2)][0]['history_in_matches'],
                    'start_weight': parents[random.randint(0, 2)][0]['start_weight'],
                    'end_weight': parents[random.randint(0, 2)][0]['end_weight'],
                    'over_power_threshold': parents[random.randint(0, 2)][0]['over_power_threshold'],
                    'over_power_extra': parents[random.randint(0, 2)][0]['over_power_extra'],
                    'close_match_threshold': parents[random.randint(0, 2)][0]['close_match_threshold'],
                    'close_match_trim': parents[random.randint(0, 2)][0]['close_match_trim']
                },
                None
            ]
            
            # Make mutations. Maybe...
            mutatable_genes = ['history_in_matches', 'start_weight', 'end_weight', 'over_power_threshold', 'over_power_extra', 'close_match_threshold', 'close_match_trim']
            for mutated_gene in mutatable_genes:
                is_mutate = (random.random() <= MUTATION_FREQUENCY)
                if is_mutate:
                    if mutated_gene == 'history_in_matches':
                        offspring[0]['history_in_matches'] = random.randint(10, 150)
                    elif mutated_gene == 'start_weight':
                        offspring[0]['start_weight'] = random.random() # 0.0-1.0
                    elif mutated_gene == 'end_weight':
                        offspring[0]['end_weight'] = random.uniform(0.5, 1.0) # 0.5-1.0
                    elif mutated_gene == 'over_power_threshold':
                        offspring[0]['over_power_threshold'] = random.randint(1,4) + random.random() # 1.0-5.0
                    elif mutated_gene == 'over_power_extra':
                        offspring[0]['over_power_extra'] = random.uniform(0.0, 0.2) # 0.0-0.2
                    elif mutated_gene == 'close_match_threshold':
                        offspring[0]['close_match_threshold'] = random.uniform(0.0, 0.5) # 0.0-0.5
                    elif mutated_gene == 'close_match_trim':
                        offspring[0]['close_match_trim'] = random.uniform(0.0, 0.4) # 0.0-0.4
                    else:
                        raise Exception('unrecognized gene ' + mutated_gene)

            if offspring[0]['end_weight'] < offspring[0]['start_weight']:
                offspring[0]['end_weight'] = 1.0
            
            offsprings.append(offspring)

        population = population + offsprings
        
        population_number += 1
