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


def get_match_percentages_of_team(team, league=None, season=None, start=None, end=None):
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
    
    num_of_games = len(matches)
    wins = 0
    draws = 0
    losses = 0
    for row in matches:
        home_team_id = row['home_team_id']
        away_team_id = row['away_team_id']
        home_goals = row['home_goals']
        away_goals = row['away_goals']
        
        if home_team_id == team_id:
            if home_goals > away_goals:
                wins += 1
            elif home_goals < away_goals:
                losses += 1
            else:
                draws += 1
        elif away_team_id == team_id:
            if home_goals < away_goals:
                wins += 1
            elif home_goals > away_goals:
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


def get_home_match_percentages_of_team(team, league=None, season=None, start=None, end=None):
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
   
    num_of_games = len(matches)
    wins = 0
    draws = 0
    losses = 0
    for g in matches:
        if g['home_goals'] > g['away_goals']:
            wins += 1
        elif g['home_goals'] < g['away_goals']:
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
    
    
def get_away_match_percentages_of_team(team, league=None, season=None, start=None, end=None):
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
   
    num_of_games = len(matches)
    wins = 0
    draws = 0
    losses = 0
    for g in matches:
        if g['home_goals'] < g['away_goals']:
            wins += 1
        elif g['home_goals'] > g['away_goals']:
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
    

def get_1X2_percentages(league=None, season=None, start=None, end=None):

    if league:
        league_id = db.get_league_id(league)
    else:
        league_id = None

    if season:
        season_id = db.get_season_id(season)
    else:
        season_id = None

    matches = db.get_matches(season_id=season_id, league_id=league_id, start=start, end=end, cancelled=False, awarded=False)
    
    num_of_matches = len(matches)
    home_win = 0
    draw = 0
    away_win = 0
    
    for match in matches:
        if match['home_goals'] > match['away_goals']:
            home_win += 1
        elif match['home_goals'] < match['away_goals']:
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

    
if __name__ == "__main__":
    # Veikkausliiga :   2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003 - OK
    # Ykkönen:          2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004 - OK
    table = get_season_table(u"Veikkausliiga", "2015")
#    for row in table:
#        print row

    teams = db.get_teams()
#    print teams
        
    ps = get_match_percentages_of_team('Kuopion Palloseura', 'Veikkausliiga', '2015')
#    print ps
    ps = get_match_percentages_of_team('Kuopion Palloseura', season='2015')
#    print ps
    ps = get_match_percentages_of_team('Kuopion Palloseura', 'Veikkausliiga')
#    print ps
    ps = get_match_percentages_of_team('Kuopion Palloseura')
#    print ps
#    print

    ps = get_home_match_percentages_of_team('Kuopion Palloseura', 'Veikkausliiga', '2015')
#    print ps
    ps = get_home_match_percentages_of_team('Kuopion Palloseura', season='2015')
#    print ps
    ps = get_home_match_percentages_of_team('Kuopion Palloseura', 'Veikkausliiga')
#    print ps
    ps = get_home_match_percentages_of_team('Kuopion Palloseura')
#    print ps
#    print

    ps = get_away_match_percentages_of_team('Kuopion Palloseura', 'Veikkausliiga', '2015')
#    print ps
    ps = get_away_match_percentages_of_team('Kuopion Palloseura', season='2015')
#    print ps
    ps = get_away_match_percentages_of_team('Kuopion Palloseura', 'Veikkausliiga')
#    print ps
    ps = get_away_match_percentages_of_team('Kuopion Palloseura')
#    print ps
#    print
    
    ps = get_1X2_percentages()
    print ps    
    ps = get_1X2_percentages(league='Veikkausliiga')
    print ps
    ps = get_1X2_percentages(league='Veikkausliiga', season='2015')
    print ps    
    ps = get_1X2_percentages(league='Veikkausliiga', start='2015-01-01', end='2015-12-31')
    print ps    
    ps = get_1X2_percentages(season='2015')
    print ps
    ps = get_1X2_percentages(start='2015-01-01', end='2015-12-31')
    print ps
    ps = get_1X2_percentages(start='2015-01-01')
    print ps
    ps = get_1X2_percentages(end='2015-12-31')
    print ps
