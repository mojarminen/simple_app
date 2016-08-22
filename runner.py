# -*- coding: utf-8 -*-

import db
import estimator
import betting_strategy

def play(initial_money, estimator, betting_strategy, league=None, season=None, start=None, end=None):
    
    money = initial_money
    
    league_id = db.get_league_id(league) if league else None
    season_id = db.get_season_id(season) if season else None

    matches = db.get_matches(league_id=league_id, season_id=season_id, start=start, end=end, cancelled=False, awarded=False)
    matches = sorted(matches, key=lambda x: x['date'])
    for match in matches:
        match['home_win_probability'] = None
        match['draw_probability'] = None
        match['away_win_probability'] = None
        match['bet_1'] = None
        match['bet_X'] = None
        match['bet_2'] = None
        match['returning'] = 0

        # Get 1X2 odds.
        odds = db.get_match_1X2_odds(match['match_id'])['HIGHEST']
        match['max_home_win_odd'] = odds['home_win']
        match['max_draw_odd'] = odds['draw']
        match['max_away_win_odd'] = odds['away_win']
        
        # Get probability estimations.
        estimation = estimator(match['home_team'], match['away_team'], match['date'], season=season, league=league)
        if estimation is None:
            continue
        match['home_win_probability'] = estimation['1']
        match['draw_probability'] = estimation['X']
        match['away_win_probability'] = estimation['2']
        
        # Set bets.
        match['bet_1'], match['bet_X'], match['bet_2'] = betting_strategy(money, estimation['1'], odds['home_win'], estimation['X'], odds['draw'], estimation['2'], odds['away_win'])
        
#        match['bet_1'] = betting_strategy(money, estimation['1'], odds['home_win'])
#        match['bet_X'] = betting_strategy(money, estimation['X'], odds['draw'])
#        match['bet_2'] = betting_strategy(money, estimation['2'], odds['away_win'])
        money = money - match['bet_1'] - match['bet_X'] - match['bet_2']
        match['returning'] = match['returning'] - match['bet_1'] - match['bet_X'] - match['bet_2']
 
        # Collect.
        if match['home_goals'] > match['away_goals'] and match['bet_1']:
            money += (odds['home_win'] * match['bet_1'])
            match['returning'] += (odds['home_win'] * match['bet_1'])
        elif match['home_goals'] < match['away_goals'] and match['bet_2']:
            money += (odds['away_win'] * match['bet_2'])
            match['returning'] += (odds['away_win'] * match['bet_2'])
        elif match['home_goals'] == match['away_goals'] and match['bet_X']:
            money += (odds['draw'] * match['bet_X'])
            match['returning'] += (odds['draw'] * match['bet_X'])
        
    return money, matches
    
if __name__ == '__main__':
#    play(1000, league='Veikkausliiga', season='2015', start='2015-08-01')
    
#    veikkausliiga_poisson = play(1000, estimator.poisson, betting_strategy.kelly_div_10, league=u'Veikkausliiga', start='2010-01-01')
#    veikkausliiga_my_simple = play(1000, estimator.simple_estimation, betting_strategy.kelly_div_10, league=u'Veikkausliiga', start='2010-01-01')
        
    INITIAL_MONEY = 1000
    
    '''
    import csv
    with open('output.csv', 'wb') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(['Date', 'Home Team', 'Away Team', 
                            'Home Goals', 'Away Goals', 
                            'Home Win Prob.', 'Draw Prob.', 'Away Win Prob.', 
                            '1 Odd Limit', 'X Odd Limit', '2 Odd Limit', 
                            '1 odd', 'X odd', '2 odd', 
                            '1 bet', 'X bet', '2 bet', 'Returning'])
        
        money, matches = play(INITIAL_MONEY, estimator.simple_estimation, betting_strategy.kelly_div_10, league=u'Veikkausliiga', season=str('2014'))
        print money
        
        for match in matches:
            csvwriter.writerow([match['date'], match['home_team'].encode('utf-8'), match['away_team'].encode('utf-8'), 
                                match['home_goals'], match['away_goals'], 
                                match['home_win_probability'], match['draw_probability'], match['away_win_probability'],
                                1/match['home_win_probability'] if match['home_win_probability'] else '', 1/match['draw_probability'] if match['draw_probability'] else '', 1/match['away_win_probability'] if match['away_win_probability'] else '',
                                match['max_home_win_odd'], match['max_draw_odd'], match['max_away_win_odd'],
                                match['bet_1'], match['bet_X'], match['bet_2'], match['returning']])

    exit(0)
    for match in matches:
        print match
    '''
    
    strategies = ((estimator.simple_estimation2, betting_strategy.div_100),
                  (estimator.poisson, betting_strategy.div_100))

    results = []
    
    for get_estimations, get_bet in strategies:
        if get_estimations == estimator.simple_estimation:
            print 'My estimation:'
        elif get_estimations == estimator.simple_estimation2:
            print 'Next Generation Estimator:'
        elif get_estimations == estimator.poisson:
            print 'Poisson'
        else:
            raise Exception('unrecognised estimator')
        
        winnings_veikkausliiga = 0
        veikkausliiga_plus_minus = 0
        for season in range(2006, 2017): 
            print '\tVeikkausliiga ' + str(season) + ': ',
            money_left, matches = play(INITIAL_MONEY, get_estimations, get_bet, league=u'Veikkausliiga', season=str(season))
            print money_left
            winnings_veikkausliiga += (money_left - INITIAL_MONEY)
        
        winnings_ykkonen = 0
        ykkonen_plus_minus = 0
        for season in range(2006, 2017): 
            print '\tYkkönen ' + str(season) + ': ',
            money_left, matches = play(INITIAL_MONEY, get_estimations, get_bet, league=u'Ykkönen', season=str(season)) 
            print money_left
            winnings_ykkonen += (money_left - INITIAL_MONEY)
    
        winnings_premier_league = 0
        premier_league_plus_minus = 0
        for season in range(2006, 2016): 
            print '\tPremier League ' + str(season) + '-' + str(int(season)+1) + ': ',
            money_left, matches = play(INITIAL_MONEY, get_estimations, get_bet, league=u'Premier League', season=str(season) + '-' + str(season+1)) 
            print money_left
            winnings_premier_league += (money_left - INITIAL_MONEY)
            if winnings_premier_league > 0:
                premier_league_plus_minus += 1
            else:
                premier_league_plus_minus -= 1
    
