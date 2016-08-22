# -*- coding: utf-8 -*-

MIN_BET = 1

def kelly_div_10(all_money, probability, odd):
    
    if odd - 1/probability > 0:
        result = all_money * min(0.1, ((probability * odd) / (odd - 1))/10)
        
        if result < MIN_BET:
            result = 0
    else:
        result = 0
        
    return result
        

def div_100(all_money, probability_1, odd_1, probability_X, odd_X, probability_2, odd_2):
    if odd_1 - 1/probability_1 > 0:
        result_1 = 0.01 * all_money
        
        if result_1 < MIN_BET:
            result_1 = MIN_BET
    else:
        result_1 = 0
        
    if odd_X - 1/probability_X > 0:
        result_X = 0.01 * all_money
        
        if result_X < MIN_BET:
            result_X = MIN_BET
    else:
        result_X = 0
        
    if odd_2 - 1/probability_2 > 0:
        result_2 = 0.01 * all_money
        
        if result_2 < MIN_BET:
            result_2 = MIN_BET
    else:
        result_2 = 0
        
    '''
    if result_1 > 0 and result_X > 0:
        if probability_1 > probability_X:
            result_X = 0
        else:
            result_1 = 0
        
    if result_1 > 0 and result_2 > 0:
        if probability_1 > probability_2:
            result_2 = 0
        else:
            result_1 = 0
        
    if result_2 > 0 and result_X > 0:
        if probability_2 > probability_X:
            result_X = 0
        else:
            result_2 = 0
    '''
    
    return result_1, result_X, result_2
    
    
def bet_2(all_money, probability, odd):
    if odd - 1/probability > 0:
        result = 2
    else:
        result = 0
    return result
