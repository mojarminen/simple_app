# -*- coding: utf-8 -*-

import os
import os.path
import csv
import datetime
import sqlite3

PREMIER_LEAGUE_PATH = '../datafiles/england/premier_league'

DB_FILE = '../football.db'
conn = sqlite3.connect(DB_FILE)

# Keys are all the team names used.
# Values are official names of the teams.
TEAMS = {u'Arsenal': 'Arsenal',
         u'Aston Villa': 'Aston Villa',
         u'Birmingham': 'Birmingham City',
         u'Blackburn': 'Blackburn Rovers',
         u'Blackpool': 'Blackpool',
         u'Bolton': 'Bolton Wanderers',
         u'Bournemouth': 'AFC Bournemouth',
         u'Bradford': 'Bradford City',
         u'Burnley': 'Burnley',
         u'Cardiff': 'Cardiff City',
         u'Charlton': 'Charlton Athletic',
         u'Chelsea': 'Chelsea',
         u'Coventry': 'Coventry City',
         u'Crystal Palace': 'Crystal Palace',
         u'Derby': 'Derby County',
         u'Everton': 'Everton',
         u'Fulham': 'Fulham',
         u'Hull City': 'Hull City',
         u'Ipswich': 'Ipswich Town',
         u'Leeds': 'Leeds United',
         u'Leicester': 'Leicester City',
         u'Liverpool': 'Liverpool',
         u'Manchester City': 'Manchester City',
         u'Manchester United': 'Manchester United',
         u'Middlesbrough': 'Middlesbrough',
         u'Newcastle Utd': 'Newcastle United',
         u'Norwich': 'Norwich City',
         u'Nottingham': 'Nottingham Forest',
         u'Portsmouth': 'Portsmouth',
         u'QPR': 'Queens Park Rangers',
         u'Reading': 'Reading',
         u'Sheffield Utd': 'Sheffield United',
         u'Sheffield Wed': 'Sheffield Wednesday',
         u'Southampton': 'Southampton',
         u'Stoke City': 'Stoke City',
         u'Sunderland': 'Sunderland',
         u'Swansea': 'Swansea City',
         u'Tottenham': 'Tottenham Hotspur',
         u'Watford': 'Watford',
         u'West Brom': 'West Bromwich Albion',
         u'West Ham': 'West Ham United',
         u'Wigan': 'Wigan Athletic',
         u'Wimbledon FC': 'Wimbledon FC',
         u'Wolves': 'Wolverhampton Wanderers',
         }
         
LEAGUES = ("Premier League",)
SEASONS = ("1998-1999", "1999-2000", "2000-2001", "2001-2002", "2002-2003", 
           "2003-2004", "2004-2005", "2005-2006", "2006-2007", "2007-2008", 
           "2008-2009", "2009-2010", "2010-2011", "2011-2012", "2012-2013", 
           "2013-2014", "2014-2015", "2015-2016", "2016-2017")

def read_data(filepath):
    result = []
    with open(filepath, 'rb') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            cancelled = False
            awarded = False
            home_goals = None
            away_goals = None
            
            # Jump over heading rows.
            if 'Round' in row[0] and row[2] == '1' and row[3] == 'X' and row[4] == '2':
                continue
            
            # parse teams
            home_team, away_team = row[0].split(' - ')
            assert len(home_team) > 0
            assert len(away_team) > 0

            # parse result
            if 'CAN.' in row[1]:
                cancelled = True
            elif 'AWA.' in row[1]:
                home_goals, away_goals = [int(goals) for goals in row[1].split(' ')[0].split(':')]                
                awarded = True
            else:
                home_goals, away_goals = [int(goals) for goals in row[1].split(':')]
            
            # parse date
            day, month, year = [int(d) for d in row[5].split('.')]
            date = datetime.date(year, month, day).strftime('%Y-%m-%d')

            # parse odds
            home_win, draw, away_win = float(row[2] or '0'), float(row[3] or '0'), float(row[4] or '0')
            
            result.append({'date': date, 
                           'home_team': home_team, 
                           'away_team': away_team, 
                           'home_goals': home_goals, 
                           'away_goals': away_goals, 
                           'cancelled': cancelled, 
                           'awarded': awarded,
                           'home_win_odds': home_win,
                           'draw_odds': draw,
                           'away_win_odds': away_win})
            
    if len(result) == 0:
        raise Exception("no data found in file '" + filepath + "'")
    else:
        return result


def add_teams():
    cur = conn.cursor()
    
    for team in TEAMS.values():
        cur.execute('''SELECT id FROM team WHERE title = ?''', (team,))
        result = cur.fetchone()
        if not result:
            cur.execute('''INSERT INTO team (title) VALUES (?)''', (team,))
    
    
def insert_match(competition, date, home_team_id, away_team_id, home_goals, away_goals, cancelled, awarded):
    cur = conn.cursor()
    
    cur.execute('''SELECT id FROM match WHERE "date" = ? AND home_team = ? AND away_team = ?''', (date, home_team_id, away_team_id))
    
    result = cur.fetchone()
    if result:
        matchid = result[0]
    else:
        cur.execute('''INSERT INTO match (competition, "date", home_team, away_team, 
                       full_time_home_team_goals, full_time_away_team_goals, cancelled, awarded) 
                       VALUES (?,?,?,?,?,?,?,?)''', 
                    (competition, date, home_team_id, away_team_id, home_goals, away_goals, cancelled, awarded))
        matchid = cur.lastrowid
    
    return matchid


def get_competition_id(league, season):
    cur = conn.cursor()
    
    cur.execute('''SELECT competition.id 
                   FROM competition, league, season
                   WHERE competition.league = league.id
                   AND competition.season = season.id
                   AND league.title = ?
                   AND season.title = ?''', (league, season))
                   
    return cur.fetchone()[0]


def add_competitions():
    cur = conn.cursor()
    
    for league in LEAGUES:
        cur.execute('''SELECT id FROM league WHERE title = ?''', (league,))
        result = cur.fetchone()
        if result:
            league_id = result[0]
        else:
            cur.execute('''INSERT INTO league (title) VALUES (?)''', (league,))
            league_id = cur.lastrowid
    
        for season in SEASONS:
            cur.execute('''SELECT id FROM season WHERE title = ?''', (season,))
            result = cur.fetchone()
            if result:
                season_id = result[0]
            else:
                cur.execute('''INSERT INTO season (title) VALUES (?)''', (season,))
                season_id = cur.lastrowid
                
            # Insert competition
            cur.execute('''SELECT id FROM competition WHERE league = ? AND season = ?''', (league_id, season_id))
            if not cur.fetchone():
                cur.execute('''INSERT INTO competition (title, league, season) VALUES (?,?,?)''', (league + " " + season, league_id, season_id))


def get_team_id(team_name):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM team WHERE title = ?''', (team_name,))
    return cur.fetchone()[0]


def insert_odds(matchid, booker, home_win, draw, away_win):
    cur = conn.cursor()
    cur.execute('''SELECT * FROM odds_1X2 WHERE match = ? AND booker = ?''', (matchid, booker))
    
    result = cur.fetchone()
    
    if result:
        odds_id = result[0]
    else:
        cur.execute('''INSERT INTO odds_1X2 (match, booker, home_win, draw, away_win) VALUES (?,?,?,?,?)''', (matchid, booker, home_win, draw, away_win))
        odds_id = cur.lastrowid
        
    return odds_id


if __name__ == "__main__":

    add_teams()
    add_competitions()

    for inputpath in (PREMIER_LEAGUE_PATH,):
        
        for filename in [f for f in os.listdir(inputpath) if os.path.isfile(os.path.join(inputpath, f))]:
            print filename

            season = filename.rsplit('_', 1)[1].split('.')[0]
            season = str(int(season.split('-')[0])) + '-' + str(int(season.split('-')[1]))


            if inputpath == PREMIER_LEAGUE_PATH:
                competition_id = get_competition_id('Premier League', season)
            else:
                raise Exception('competition undefined')
            
            filepath = os.path.join(inputpath, filename)
            
            for row in read_data(filepath):
                date = row['date']
                
                # Get official team names.
                home_team = TEAMS[row['home_team']]
                away_team = TEAMS[row['away_team']]
                
                # Get database id of the home team
                home_team_id = get_team_id(home_team)
                away_team_id = get_team_id(away_team)
                assert type(home_team_id) is int
                assert type(away_team_id) is int
                
                # Insert match information.
                matchid = insert_match(competition_id, date, home_team_id, away_team_id, row['home_goals'], row['away_goals'], row['cancelled'], row['awarded'])
                
                # Insert odds.
                insert_odds(matchid, 'HIGHEST', row['home_win_odds'], row['draw_odds'], row['away_win_odds'])
        
    conn.commit()
