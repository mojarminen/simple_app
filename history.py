# -*- coding: utf-8 -*-

import sqlite3

import db


def get_matches(team=None, league=None, season=None, start=None, end=None, cancelled=False, awarded=False):

    if team is not None:
        team_id = db.get_team_id(team)
    else:
        team_id = None

    if league is not None:
        league_id = db.get_league_id(league)
    else:
        league_id = None
        
    if season is not None:
        season_id = db.get_season_id(season)
    else:
        season_id = None
        
    return db.get_matches(team_id=team_id, start=start, end=end, league_id=league_id, season_id=season_id, cancelled=cancelled, awarded=awarded)


def print_match_preview(home_team, away_team, season):
    
    print 'HOME TEAM:', home_team
    print
    
    if '-' in season:
        for s in range(int(season.split('-')[0]), int(season.split('-')[0])-4, -1):
            s_str = str(s) + '-' + str(s+1)
            print '\thome percentages', s_str, ':', get_home_match_percentages_of_team(home_team, season=s_str)
        print
        for s in range(int(season.split('-')[0]), int(season.split('-')[0])-4, -1):
            s_str = str(s) + '-' + str(s+1)
            print '\tmatch percentages', s_str, ':', get_match_percentages_of_team(home_team, season=s_str)
        print

        print 'AWAY TEAM:', away_team
        print
        for s in range(int(season.split('-')[0]), int(season.split('-')[0])-4, -1):
            s_str = str(s) + '-' + str(s+1)
            print '\taway percentages', s_str, ':', get_away_match_percentages_of_team(away_team, season=s_str)
        print
        for s in range(int(season.split('-')[0]), int(season.split('-')[0])-4, -1):
            s_str = str(s) + '-' + str(s+1)
            print '\tmatch percentages', s_str, ':', get_match_percentages_of_team(away_team, season=s_str)
        print
        
        s = str(int(season.split('-')[0])-1) + '-' + str(int(season.split('-')[1])-1)
    else:
        for s in range(int(season), int(season)-4, -1):
            s_str = str(s)
            print '\thome percentages', s_str, ':', get_home_match_percentages_of_team(home_team, season=s_str)
        print
        for s in range(int(season), int(season)-4, -1):
            s_str = str(s)
            print '\tmatch percentages', s_str, ':', get_match_percentages_of_team(home_team, season=s_str)
        print

        print 'AWAY TEAM:', away_team
        print
        for s in range(int(season), int(season)-4, -1):
            s_str = str(s)
            print '\taway percentages', s_str, ':', get_away_match_percentages_of_team(away_team, season=s_str)
        print
        for s in range(int(season), int(season)-4, -1):
            s_str = str(s)
            print '\tmatch percentages', s_str, ':', get_match_percentages_of_team(away_team, season=s_str)
        print
        
        s = season
        

    home_home_percentages = get_home_match_percentages_of_team(home_team, season=s)
    home_match_percentages = get_match_percentages_of_team(home_team, season=s)
    away_away_percentages = get_away_match_percentages_of_team(away_team, season=s)
    away_match_percentages = get_match_percentages_of_team(away_team, season=s)
    
    general_1X2 = get_1X2_percentages(season=s)
    print 'GENERAL 1X2:', general_1X2
    print
        
    print 'ESTIMATED PROBABILITIES:', 
    home_win_p = (home_home_percentages[0] + home_match_percentages[0] + away_away_percentages[2] + away_match_percentages[2] + general_1X2[0])*100./5.
    print home_win_p,
    print '-',
    draw_p = (home_home_percentages[1] + home_match_percentages[1] + away_away_percentages[1] + away_match_percentages[1] + general_1X2[1])*100./5.
    print draw_p,
    print '-',
    away_win_p = (home_home_percentages[2] + home_match_percentages[2] + away_away_percentages[0] + away_match_percentages[0] + general_1X2[2])*100./5. 
    print away_win_p
    
    print 'ODD LIMITS:', 100./home_win_p, '-', 100./draw_p, '-', 100./away_win_p


def get_n_previous_matches_of_team(team, date, count, league=None, season=None):

    team_id = db.get_team_id(team)

    if league is not None:
        league_id = db.get_league_id(league)
    else:
        league_id = None
        
    if season is not None:
        season_id = db.get_season_id(season)
    else:
        season_id = None
        
    matches = db.get_matches(team_id=team_id, end=date, league_id=league_id, season_id=season_id, cancelled=False, awarded=False)
    
    matches = sorted(matches, key=lambda x: x['date'])
    matches.reverse()
    
    return matches[:min(count, len(matches))]
    

def get_season_table(league, season):
    
    league_id = db.get_league_id(league)
    season_id = db.get_season_id(season)
    
    matches = db.get_matches(league_id=league_id, season_id=season_id, cancelled=False)
    
    teams = {}
    for row in matches:
        home_team = row['home_team']
        away_team = row['away_team']
        home_goals = row['home_goals']
        away_goals = row['away_goals']
        
        if home_team not in teams:
            teams[home_team] = 0
        if away_team not in teams:
            teams[away_team] = 0
        
        # home win
        if home_goals > away_goals:
            teams[home_team] += 3
        # away win
        elif home_goals < away_goals:
            teams[away_team] += 3
        # draw
        else:
            teams[home_team] += 1
            teams[away_team] += 1
            
    result = teams.items()
    return reversed(sorted(result, key=lambda x: x[1]))


def get_full_time_match_percentages_of_team(team, league=None, season=None, start=None, end=None, start_weight=None, end_weight=None, number_of_matches=None):
    '''returns win%, draw%, loss%'''

    team_id = db.get_team_id(team)
    
    if league:
        league_id = db.get_league_id(league)
    else:
        league_id = None

    if season:
        season_id = db.get_season_id(season)
    else:
        season_id = None

    matches = db.get_matches(team_id=team_id, season_id=season_id, league_id=league_id, start=start, end=end, cancelled=False, awarded=False)
    
    if number_of_matches:
        if len(matches) > number_of_matches:
            matches.reverse()
            matches = matches[:number_of_matches]
            matches.reverse()
    
    if start_weight is None or end_weight is None:
        num_of_games = len(matches)
        wins = 0
        draws = 0
        losses = 0
        for row in matches:
            home_team_id = row['home_team_id']
            away_team_id = row['away_team_id']
            full_time_home_team_goals = row['full_time_home_team_goals']
            full_time_away_team_goals = row['full_time_away_team_goals']
            
            if home_team_id == team_id:
                if full_time_home_team_goals > full_time_away_team_goals:
                    wins += 1
                elif full_time_home_team_goals < full_time_away_team_goals:
                    losses += 1
                else:
                    draws += 1
            elif away_team_id == team_id:
                if full_time_home_team_goals < full_time_away_team_goals:
                    wins += 1
                elif full_time_home_team_goals > full_time_away_team_goals:
                    losses += 1
                else:
                    draws += 1
            else:
                raise Exeption('not a game of the team ' + team)

        if num_of_games == 0:
            return (0,0,0,0)
        else:
            return (float(wins)/num_of_games,
                    float(draws)/num_of_games,
                    float(losses)/num_of_games,
                    num_of_games)
    else:
        if len(matches) == 0:
            return (0,0,0,0)
        
        delta = (end_weight - start_weight)/len(matches)
        weight_sum = 0.
        
        wins = 0.
        draws = 0.
        losses = 0.
        
        weight = start_weight
        
        for row in matches:
            home_team_id = row['home_team_id']
            away_team_id = row['away_team_id']
            full_time_home_team_goals = row['full_time_home_team_goals']
            full_time_away_team_goals = row['full_time_away_team_goals']
            
            if home_team_id == team_id:
                if full_time_home_team_goals > full_time_away_team_goals:
                    wins += weight
                elif full_time_home_team_goals < full_time_away_team_goals:
                    losses += weight
                else:
                    draws += weight
            elif away_team_id == team_id:
                if full_time_home_team_goals < full_time_away_team_goals:
                    wins += weight
                elif full_time_home_team_goals > full_time_away_team_goals:
                    losses += weight
                else:
                    draws += weight
            else:
                raise Exeption('not a game of the team ' + team)

            weight_sum += weight

            weight += delta

        return (wins/weight_sum,
                draws/weight_sum,
                losses/weight_sum,
                len(matches))

def get_full_time_home_match_percentages_of_team(team, league=None, season=None, start=None, end=None, start_weight=None, end_weight=None, number_of_matches=None):
    '''returns win%, draw%, loss%'''

    team_id = db.get_team_id(team)
    
    if league:
        league_id = db.get_league_id(league)
    else:
        league_id = None

    if season:
        season_id = db.get_season_id(season)
    else:
        season_id = None

    matches = db.get_matches(home_team_id=team_id, season_id=season_id, league_id=league_id, start=start, end=end, cancelled=False, awarded=False)
   
    if number_of_matches:
        if len(matches) > number_of_matches:
            matches.reverse()
            matches = matches[:number_of_matches]
            matches.reverse()

    if start_weight is None or end_weight is None:
        num_of_games = len(matches)
        wins = 0
        draws = 0
        losses = 0
        for g in matches:
            if g['full_time_home_team_goals'] > g['full_time_away_team_goals']:
                wins += 1
            elif g['full_time_home_team_goals'] < g['full_time_away_team_goals']:
                losses += 1
            else:
                draws += 1
                
        if num_of_games == 0:
            return (0,0,0,0)
        else:
            return (float(wins)/num_of_games,
                    float(draws)/num_of_games,
                    float(losses)/num_of_games,
                    num_of_games)
    else:
        if len(matches) == 0:
            return (0,0,0,0)
        
        delta = (end_weight - start_weight)/len(matches)
        weight_sum = 0.
        
        wins = 0.
        draws = 0.
        losses = 0.
        
        weight = start_weight
        
        for g in matches:
            if g['full_time_home_team_goals'] > g['full_time_away_team_goals']:
                wins += weight
            elif g['full_time_home_team_goals'] < g['full_time_away_team_goals']:
                losses += weight
            else:
                draws += weight
                
            weight_sum += weight
                
            weight += delta
                
        return (wins/weight_sum,
                draws/weight_sum,
                losses/weight_sum,
                len(matches))
    
    
def get_full_time_away_match_percentages_of_team(team, league=None, season=None, start=None, end=None, start_weight=None, end_weight=None, number_of_matches=None):
    '''returns win%, draw%, loss%'''

    team_id = db.get_team_id(team)
    
    if league:
        league_id = db.get_league_id(league)
    else:
        league_id = None

    if season:
        season_id = db.get_season_id(season)
    else:
        season_id = None

    matches = db.get_matches(away_team_id=team_id, season_id=season_id, league_id=league_id, start=start, end=end, cancelled=False, awarded=False)
       
    if number_of_matches:
        if len(matches) > number_of_matches:
            matches.reverse()
            matches = matches[:number_of_matches]
            matches.reverse()

    if start_weight is None or end_weight is None:
        num_of_games = len(matches)
        wins = 0
        draws = 0
        losses = 0
        for g in matches:
            if g['full_time_home_team_goals'] < g['full_time_away_team_goals']:
                wins += 1
            elif g['full_time_home_team_goals'] > g['full_time_away_team_goals']:
                losses += 1
            else:
                draws += 1
                
        if num_of_games == 0:
            return (0,0,0,0)
        else:
            return (float(wins)/num_of_games,
                    float(draws)/num_of_games,
                    float(losses)/num_of_games,
                    num_of_games)
    else:
        if len(matches) == 0:
            return (0,0,0,0)
        
        delta = (end_weight - start_weight)/len(matches)
        weight_sum = 0.
        
        wins = 0.
        draws = 0.
        losses = 0.
        
        weight = start_weight
        
        for g in matches:
            if g['full_time_home_team_goals'] < g['full_time_away_team_goals']:
                wins += weight
            elif g['full_time_home_team_goals'] > g['full_time_away_team_goals']:
                losses += weight
            else:
                draws += weight
                
            weight_sum += weight
                
            weight += delta
                
        return (wins/weight_sum,
                draws/weight_sum,
                losses/weight_sum,
                len(matches))
    

def get_full_time_1X2_percentages(league=None, season=None, start=None, end=None, start_weight=None, end_weight=None, number_of_matches=None):

    if league:
        league_id = db.get_league_id(league)
    else:
        league_id = None

    if season:
        season_id = db.get_season_id(season)
    else:
        season_id = None

    matches = db.get_matches(season_id=season_id, league_id=league_id, start=start, end=end, cancelled=False, awarded=False)

    if number_of_matches:
        if len(matches) > number_of_matches:
            matches.reverse()
            matches = matches[:number_of_matches]
            matches.reverse()
    
    if start_weight is None or end_weight is None:
        num_of_matches = len(matches)
        home_win = 0
        draw = 0
        away_win = 0
        
        for match in matches:
            if match['full_time_home_team_goals'] > match['full_time_away_team_goals']:
                home_win += 1
            elif match['full_time_home_team_goals'] < match['full_time_away_team_goals']:
                away_win += 1
            else:
                draw += 1
                
        if num_of_matches == 0:
            return (0,0,0,0)
        else:
            return (float(home_win)/num_of_matches,
                    float(draw)/num_of_matches,
                    float(away_win)/num_of_matches,
                    num_of_matches)
    else:
        if len(matches) == 0:
            return (0,0,0,0)
        
        delta = (end_weight - start_weight)/len(matches)
        weight_sum = 0.
        
        home_win = 0.
        draw = 0.
        away_win = 0.
        
        weight = start_weight
        
        for g in matches:
            if g['full_time_home_team_goals'] > g['full_time_away_team_goals']:
                home_win += weight
            elif g['full_time_home_team_goals'] < g['full_time_away_team_goals']:
                away_win += weight
            else:
                draw += weight
                
            weight_sum += weight
                
            weight += delta
                
        return (home_win/weight_sum,
                draw/weight_sum,
                away_win/weight_sum,
                len(matches))

