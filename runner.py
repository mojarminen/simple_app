# -*- coding: utf-8 -*-

import db
import estimator
import betting_strategy

def play(initial_money, estimator, betting_strategy, league=None, season=None, start=None, end=None):
    
    money = initial_money
    
    league_id = db.get_league_id(league) if league else None
    season_id = db.get_season_id(season) if season else None

    
    for match in db.get_matches(league_id=league_id, season_id=season_id, start=start, end=end, cancelled=False, awarded=False):
        print match['date'], ':', match['home_team'], '-', match['away_team'], '***', match['home_goals'], '-', match['away_goals']
    
        estimation = estimator(match['home_team'], match['away_team'], match['date'], season=season, league=league)
        if estimation is None:
            print 'NO ESTIMATION!'
            continue

        print 'estimated probabilities:', estimation['1'], '-', estimation['X'], '-', estimation['2']
        print 'odd limits:', 1/estimation['1'], '-', 1/estimation['X'], '-', 1/estimation['2']
        
        odds = db.get_match_1X2_odds(match['match_id'])['HIGHEST']
        print 'odds:', odds['home_win'], '-', odds['draw'], '-', odds['away_win']
        
        # Set bets.
        bet_1 = betting_strategy(money, estimation['1'], odds['home_win'])
        bet_X = betting_strategy(money, estimation['X'], odds['draw'])
        bet_2 = betting_strategy(money, estimation['2'], odds['away_win'])
        money = money - bet_1 - bet_X - bet_2

        # Collect.
        if match['home_goals'] > match['away_goals'] and bet_1:
            money += odds['home_win'] * bet_1
            print 'WIN:', odds['home_win'] * bet_1 - bet_2 - bet_X - bet_1
        elif match['home_goals'] < match['away_goals'] and bet_2:
            money += odds['away_win'] * bet_2
            print 'WIN:', odds['away_win'] * bet_2 - bet_2 - bet_X - bet_1
        elif match['home_goals'] == match['away_goals'] and bet_X:
            money += odds['draw'] * bet_X
            print 'WIN:', odds['draw'] * bet_X - bet_2 - bet_X - bet_1
        elif bet_1 or bet_X or bet_2:
            print 'LOSS:', -(bet_1 + bet_X + bet_2)
        
        print 'MONEY:', money
        print

    return money
    
if __name__ == '__main__':
#    play(1000, league='Veikkausliiga', season='2015', start='2015-08-01')
    
    veikkausliiga_poisson = play(1000, estimator.poisson, betting_strategy.kelly_div_10, league=u'Veikkausliiga', start='2010-01-01')
    veikkausliiga_my_simple = play(1000, estimator.simple_estimation, betting_strategy.kelly_div_10, league=u'Veikkausliiga', start='2010-01-01') 

    ykkonen_poisson = play(1000, estimator.poisson, betting_strategy.kelly_div_10, league=u'Ykkönen', start='2010-01-01')
    ykkonen_my_simple = play(1000, estimator.simple_estimation, betting_strategy.kelly_div_10, league=u'Ykkönen', start='2010-01-01') 

    print 'Veikkausliiga:'
    print 'poisson:', veikkausliiga_poisson
    print 'my_simple:', veikkausliiga_my_simple

    print 'Veikkausliiga:'
    print 'poisson:', ykkonen_poisson
    print 'my_simple:', ykkonen_my_simple
