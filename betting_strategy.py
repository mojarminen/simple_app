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
        

def div_100(all_money, probability, odd):
    if odd - 1/probability > 0:
        result = 0.01 * all_money
        
        if result < MIN_BET:
            result = MIN_BET
    else:
        result = 0
        
    return result
    
    
def bet_2(all_money, probability, odd):
    if odd - 1/probability > 0:
        result = 2
    else:
        result = 0
    return result
