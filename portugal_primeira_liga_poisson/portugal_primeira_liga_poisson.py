# -*- coding: utf-8 -*-

import os
import os.path
import csv
import datetime
import math

DATAFILES = [
        'portugal_primeira_liga_2016-2017.csv',
    ]

TEAMS = {
    'Arouca': 'Arouca',
    'Belenenses': 'Belenenses',
    'Benfica': 'Benfica',
    'Boavista': 'Boavista',
    'Braga': 'Braga',
    'Chaves': 'Chaves',
    'Estoril': 'Estoril',
    'FC Porto': 'FC Porto',
    'Feirense': 'Feirense',
    'Ferreira': 'Ferreira',
    'Guimaraes': 'Guimaraes',
    'Maritimo': 'Maritimo',
    'Moreirense': 'Moreirense',
    'Nacional': 'Nacional',
    'Rio Ave': 'Rio Ave',
    'Setubal': 'Setubal',
    'Sporting': 'Sporting',
    'Tondela': 'Tondela',
}

def read_data(filepath):
    result = []
    with open(filepath, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            
            cancelled = False
            awarded = False
            full_time_home_goals = None
            full_time_away_goals = None
            
            # Jump over heading rows.
            if ('Round' in row[0] or row[0] == '') and row[2] == '1' and row[3] == 'X' and row[4] == '2':
                continue
            
            # parse teams
            home_team, away_team = row[0].split(' - ')
            assert len(home_team) > 0
            assert len(away_team) > 0

            # parse result
            if 'CAN.' in row[1]:
                cancelled = True
            elif 'AWA.' in row[1]:
                full_time_home_goals, full_time_away_goals = [int(goals) for goals in row[1].split(' ')[0].split(':')]                
                awarded = True
            elif 'ET' in row[1]:
                extra_time_home_goals, extra_time_away_goals = [int(goals) for goals in row[1].split(' ')[0].split(':')]
                full_time_home_goals = min(extra_time_home_goals, extra_time_away_goals)              
                full_time_away_goals = min(extra_time_home_goals, extra_time_away_goals)              
            elif 'pen.' in row[1]:
                penalties_home_goals, penalties_away_goals = [int(goals) for goals in row[1].split(' ')[0].split(':')]
                full_time_home_goals = min(penalties_home_goals, penalties_away_goals)              
                full_time_away_goals = min(penalties_home_goals, penalties_away_goals)              
                extra_time_home_goals = min(penalties_home_goals, penalties_away_goals)              
                extra_time_away_goals = min(penalties_home_goals, penalties_away_goals)              
            else:
                full_time_home_goals, full_time_away_goals = [int(goals) for goals in row[1].split(':')]
            
            # parse date
            day, month, year = [int(d) for d in row[5].split('.')]
            date = datetime.date(year, month, day).strftime('%Y-%m-%d')

            # parse odds
            home_win, draw, away_win = float(row[2] or '0'), float(row[3] or '0'), float(row[4] or '0')
            
            result.append({'date': date, 
                           'home_team': TEAMS[home_team], 
                           'away_team': TEAMS[away_team], 
                           'full_time_home_goals': full_time_home_goals, 
                           'full_time_away_goals': full_time_away_goals, 
                           'cancelled': cancelled, 
                           'awarded': awarded,
                           'home_win_odds': home_win,
                           'draw_odds': draw,
                           'away_win_odds': away_win})
                           
    return result

def get_1X2_of_team(team, games):
    wins = 0
    draws = 0
    losses = 0
    
    for g in games:
        if g['home_team'] == team:
            if g['full_time_home_goals'] > g['full_time_away_goals']:
                wins += 1
            elif g['full_time_home_goals'] < g['full_time_away_goals']:
                losses += 1
            else:
                draws += 1
        elif g['away_team'] == team:
            if g['full_time_home_goals'] < g['full_time_away_goals']:
                wins += 1
            elif g['full_time_home_goals'] > g['full_time_away_goals']:
                losses += 1
            else:
                draws += 1
                
    game_count = float(wins + draws + losses)
                
    return wins, draws, losses, wins/game_count, draws/game_count, losses/game_count


def get_1X2_of_teams(team1, team2, games):
    counts = [0, 0, 0]

    for g in games:
        if g['home_team'] == team1 and g['away_team'] == team2:
            if g['full_time_home_goals'] > g['full_time_away_goals']:
                counts[0] += 1
            elif g['full_time_home_goals'] < g['full_time_away_goals']:
                counts[2] += 1
            else:
                counts[1] += 1
        elif g['home_team'] == team2 and g['away_team'] == team1:
            if g['full_time_home_goals'] < g['full_time_away_goals']:
                counts[0] += 1
            elif g['full_time_home_goals'] > g['full_time_away_goals']:
                counts[2] += 1
            else:
                counts[1] += 1
    
    game_count = float(sum(counts))
    return counts, counts[0]/game_count, counts[1]/game_count, counts[2]/game_count


def draw_percentage(games):
    game_count = 0
    draw_count = 0
    for g in games:
        game_count += 1
        if g['full_time_home_goals'] == g['full_time_away_goals']:
            draw_count += 1

    return float(draw_count) / float(game_count)


def poisson(successes, successes_mean):
    return (pow(math.e, -successes_mean)*pow(successes_mean, successes))/math.factorial(successes)


def get_estimations(home_team, away_team, games):
    
    print '***', home_team, '-', away_team, '***'
    
    # Get home/away mean amount of goals
    mean_home_goals = 0
    mean_away_goals = 0
    for game in games:
        mean_home_goals += game['full_time_home_goals']
        mean_away_goals += game['full_time_away_goals']
    mean_home_goals = float(mean_home_goals) / len(games)
    mean_away_goals = float(mean_away_goals) / len(games)

    home_team_home_goals_for = 0
    home_team_home_goals_against = 0
    home_team_home_games = 0
    home_team_away_goals_for = 0
    home_team_away_goals_against = 0
    home_team_away_games = 0
    away_team_away_goals_for = 0
    away_team_away_goals_against = 0
    away_team_away_games = 0
    away_team_home_goals_for = 0
    away_team_home_goals_against = 0
    away_team_home_games = 0
    for game in games:
        if game['home_team'] == home_team:
            home_team_home_goals_for += game['full_time_home_goals']
            home_team_home_goals_against += game['full_time_away_goals']
            home_team_home_games += 1
        elif game['away_team'] == home_team:
            home_team_away_goals_for += game['full_time_away_goals']
            home_team_away_goals_against += game['full_time_home_goals']
            home_team_away_games += 1
            
        if game['away_team'] == away_team:
            away_team_away_goals_for += game['full_time_away_goals']
            away_team_away_goals_against += game['full_time_home_goals']
            away_team_away_games += 1
        elif game['home_team'] == away_team:
            away_team_home_goals_for += game['full_time_home_goals']
            away_team_home_goals_against += game['full_time_away_goals']
            away_team_home_games += 1

    home_team_home_attack = (float(home_team_home_goals_for) / home_team_home_games) / mean_home_goals
    home_team_home_defence = (float(home_team_home_goals_against) / home_team_home_games) / mean_away_goals
    home_team_away_attack = (float(home_team_away_goals_for) / home_team_away_games) / mean_away_goals
    home_team_away_defence = (float(home_team_away_goals_against) / home_team_away_games) / mean_home_goals
    
    away_team_away_attack = (float(away_team_away_goals_for) / away_team_away_games) / mean_away_goals
    away_team_away_defence = (float(away_team_away_goals_against) / away_team_away_games) / mean_home_goals
    away_team_home_attack = (float(away_team_home_goals_for) / away_team_home_games) / mean_home_goals
    away_team_home_defence = (float(away_team_home_goals_against) / away_team_home_games) / mean_away_goals

    estimated_home_goals = home_team_home_attack * home_team_away_attack * away_team_away_defence * away_team_home_defence * mean_home_goals
    estimated_away_goals = home_team_home_defence * home_team_away_defence * away_team_away_attack * away_team_away_attack * mean_away_goals

    print 'estimations:', estimated_home_goals, '-', estimated_away_goals
    
    probabilities = []
    home_win = 0
    draw = 0
    away_win = 0
    for h in range(20):
        for a in range(20):
            prob = poisson(h, estimated_home_goals)*poisson(a, estimated_away_goals)
            probabilities.append((h,a,prob)) 

            if h > a:
                home_win += prob
            elif h < a:
                away_win += prob
            else:
                draw += prob

    print 'Probabilities (homewin-draw-awaywin):', '%s-%s-%s' % (int(round(home_win*100)), int(round(draw*100)), int(round(away_win*100)))
    print 'Odd limits (homewin-draw-awaywin):', '%s-%s-%s' % (1/home_win, 1/draw, 1/away_win)
    
    print 'Poissons'
    probabilities = sorted(probabilities, key=lambda x: -x[2])
    for p in probabilities[:20]:
        print '%s-%s: %s' % p             
    print


if __name__ == '__main__':
    games = []
    for datafile in DATAFILES:
        games += read_data(datafile)

    get_estimations('Maritimo', 'Feirense', games)
    get_estimations('FC Porto', 'Chaves', games)
