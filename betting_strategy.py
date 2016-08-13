# -*- coding: utf-8 -*-

def kelly_div_10(all_money, probability, odd):
    
#    if odd < 1.4 or odd > 3.5:
#        return 0
    
    if odd - 1/probability > 0:
        return all_money * min(0.1, ((probability * odd) / (odd - 1))/20)
    else:
        return 0
        

def div_100(all_money, probability, odd):
    return 0.01 * all_money
