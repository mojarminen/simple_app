# -*- coding: utf-8 -*-

import datetime
import math

import history
import db

def simple_estimation(home_team, away_team, date, season=None, league=None):

    year, month, day = [int(d) for d in date.split('-')]
    start = datetime.date(year, month, day) + datetime.timedelta(weeks=-52)
    start = start.strftime('%Y-%m-%d')
    
    HISTORY_WEIGHT = 0.5
    
    h1, hX, h2, h_count = history.get_home_match_percentages_of_team(home_team, league=league, season=season, start=start, end=date)
    a2, aX, a1, a_count = history.get_away_match_percentages_of_team(away_team, league=league, season=season, start=start, end=date)
    c1, cX, c2, c_count = history.get_1X2_percentages(league=league, season=season)

    if h_count == 0 or a_count == 0:
        return None

    result = {'1': h1*(float(h_count)/(h_count+a_count)) + a1*(float(a_count)/(h_count+a_count)),
              'X': hX*(float(h_count)/(h_count+a_count)) + aX*(float(a_count)/(h_count+a_count)),
              '2': h2*(float(h_count)/(h_count+a_count)) + a2*(float(a_count)/(h_count+a_count)), 
              'home_team_games': h_count, 
              'away_team_games': a_count}
              
    result['1'] = result['1'] * (1 - HISTORY_WEIGHT) + c1 * HISTORY_WEIGHT
    result['X'] = result['X'] * (1 - HISTORY_WEIGHT) + cX * HISTORY_WEIGHT
    result['2'] = result['2'] * (1 - HISTORY_WEIGHT) + c2 * HISTORY_WEIGHT
    
    return result
    
    
def poisson(home_team, away_team, date, season=None, league=None):
    HISTORY_IN_WEEKS = 56
    
    year, month, day = [int(d) for d in date.split('-')]
    start = datetime.date(year, month, day) + datetime.timedelta(weeks=-HISTORY_IN_WEEKS)
    start = start.strftime('%Y-%m-%d')
    matches = history.get_matches(league=league, start=start, end=date)
    if len(matches) == 0:
        return None

    print start
    print date
    print 'matches:', len(matches)

    # Get the mean values of home goals and away goals per game.
    home_goals = 0
    away_goals = 0
    for m in matches:
        home_goals += m['home_goals']
        away_goals += m['away_goals']
    average_goals_scored_at_home = float(home_goals)/len(matches)
    average_goals_scored_away = float(away_goals)/len(matches)
    average_goals_conceded_at_home = average_goals_scored_away
    average_goals_conceded_away = average_goals_scored_at_home
    
    # Estimate home team goals.
    
    # Calculate home team attack strength.
    home_goals = 0
    number_of_matches = 0
    for m in matches:
        if m['home_team'] == home_team:
            home_goals += m['home_goals']
            number_of_matches += 1
    if number_of_matches == 0:
        return None
    home_attack_strength = (float(home_goals)/number_of_matches)/average_goals_scored_at_home
    print 'home_attack_strength:', home_attack_strength
    
    # Calculate away team defence strength.
    home_goals = 0
    number_of_matches = 0
    for m in matches:
        if m['away_team'] == away_team:
            home_goals += m['home_goals']
            number_of_matches += 1
    if number_of_matches == 0:
        return None
    away_defence_strength = (float(home_goals)/number_of_matches)/average_goals_conceded_away
    print away_defence_strength
    
    home_goals_estimation = home_attack_strength * away_defence_strength * average_goals_scored_at_home
    print 'home goals estimation:', home_goals_estimation
    
    # Calculate away team attack strength.
    
    # Estimate away_team goals.
    away_goals = 0
    number_of_matches = 0
    for m in matches:
        if m['away_team'] == away_team:
            away_goals += m['away_goals']
            number_of_matches += 1
    if number_of_matches == 0:
        return None
    away_attack_strength = (float(away_goals)/number_of_matches)/average_goals_scored_away
    print away_attack_strength
    
    # Calculate home team defence strength.
    away_goals = 0
    number_of_matches = 0
    for m in matches:
        if m['home_team'] == home_team:
            away_goals += m['away_goals']
            number_of_matches += 1
    if number_of_matches == 0:
        return None
    home_defence_strength = (float(away_goals)/number_of_matches)/average_goals_conceded_at_home
    print home_defence_strength
    
    away_goals_estimation = away_attack_strength * home_defence_strength * average_goals_scored_away
    print 'away goals estimation:', away_goals_estimation
    
    home_win_probability = 0
    draw_probability = 0
    away_win_probability = 0
    for h in range(0,10):
        for a in range(0,10):
            h_probability = (math.pow(math.e, -home_goals_estimation) * math.pow(home_goals_estimation, h))/math.factorial(h)
            a_probability = (math.pow(math.e, -away_goals_estimation) * math.pow(away_goals_estimation, a))/math.factorial(a)
            probability = h_probability * a_probability 
            if h > a:
                home_win_probability += probability
            elif h < a:
                away_win_probability += probability
            else:
                draw_probability += probability
    
    assert home_win_probability + draw_probability + away_win_probability <= 1
    
    if home_win_probability < 0.05 or draw_probability < 0.05 or away_win_probability < 0.05:
        return None

    result = {'1': home_win_probability,
              'X': draw_probability,
              '2': away_win_probability}

    return result


if __name__ == '__main__':
#    print db.get_teams()
    
#    print simple_estimation('Tampereen Ilves', 'HIFK Fotboll', start='2016-01-01', end='2016-08-13', season='2016', league='Veikkausliiga')
#    print simple_estimation('Tampereen Ilves', 'HIFK Fotboll', start='2015-01-01', end='2016-08-13', league='Veikkausliiga')

    poisson('Tampereen Ilves', 'HIFK Fotboll', '2016-08-13', league='Veikkausliiga')
    
