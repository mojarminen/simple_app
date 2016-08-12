# -*- coding: utf-8 -*-

import os
import os.path
import csv
import datetime
import sqlite3

VEIKKAUSLIIGA_PATH = '../datafiles/finland/veikkausliiga'
YKKONEN_PATH = '../datafiles/finland/ykkönen'
DB_FILE = '../football.db'

# Keys are all the team names used.
# Values are official names of the teams.
TEAMS = {u'AC Allianssi': 'AC Allianssi',
         u'AC Kajaani': 'AC Kajaani',
         u'AC Oulu': u'AC Oulu',
         u'Atlantis': u'Atlantis FC',
         u'Ekenas': u'Ekenäs IF',
         u'Espoo': u'FC Espoo',
         u'GBK Kokkola': u'GBK Kokkola',
         u'GrIFK': u'Grankulla IFK',
         u'Haka': u'FC Haka',
         u'Hameenlinna': u'FC Hämeenlinna',
         u'HIFK': u'HIFK Fotboll',
         u'HJK': u'Helsingin Jalkapalloklubi',
         u'Honka': u'FC Honka Espoo', 
         u'Ilves': u'Tampereen Ilves',
         u'Inter Turku': u'FC Inter Turku',
         u'Jaro': u'FF Jaro',
         u'Jazz Pori': u'FC Jazz Pori',
         u'JIPPO': u'JIPPO Joensuu',
         u'JJK Jyvaskyla': u'JJK Jyväskylä',
         u'Jokerit FC': u'FC Jokerit',
         u'KaPa': u'Käpylän Pallo',
         u'Kiisto': u'FC Kiisto',
         u'Klubi 04': u'Talenttiklubi Klubi-04',
         u'KooTeePee': u'FC KTP',
         u'KPV Kokkola': u'Kokkolan Palloveikot (KPV)',
         u'KTP': u'Kotkan Työväen Palloilijat',
         u'KuPS': u'Kuopion Palloseura',
         u'Kuusankoski': u'FC Kuusankoski',
         u'Lahti': u'FC Lahti',
         u'Mariehamn': u'IFK Mariehamn',
         u'Mikkeli': u'Mikkelin Palloilijat',
         u'MyPa': u'Myllykosken Pallo',
         u'Narpes Kraft': u'IF Närpes Kraft',
         u'OLS Oulu': u'Oulun Luistinseura (OLS)',
         u'OPS': u'Oulun Palloseura',
         u'P-Iirot Rauma': u'Pallo-Iirot',
         u'PK-35 Vantaa': u'PK-35 Vantaa',
         u'PoPa': u'Porin Palloilijat',
         u'PP-70 Tampere': u'Tampereen Peli-Pojat 70 (PP-70)',
         u'PS Kemi': u'Palloseura Kemi Kings',
         u'Rakuunat': u'Rakuunat Lappeenranta',
         u'Rovaniemi': u'Rovaniemen Palloseura',
         u'SJK': u'Seinäjoen Jalkapallokerho',
         u'Tampere Utd': u'Tampere United',
         u'TP-47': u'Tornion Pallo -47',
         u'TPS': u'Turun Palloseura',
         u'TPV': u'Tampereen Pallo-Veikot (TPV)',
         u'VG-62 Naantali': u'VG-62 Naantali',
         u'VIFK': u'Vasa IFK',
         u'Viikingit': u'FC Viikingit',
         u'VPS': u'Vaasan Palloseura',
         }
         
LEAGUES = ("Veikkausliiga", u"Ykkönen")
SEASONS = ("2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016")

conn = sqlite3.connect(DB_FILE)

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

    for inputpath in (VEIKKAUSLIIGA_PATH, YKKONEN_PATH):
        
        for filename in [f for f in os.listdir(inputpath) if os.path.isfile(os.path.join(inputpath, f))]:

            season = str(int(filename.rsplit('_', 1)[1].split('.')[0]))

            if inputpath == VEIKKAUSLIIGA_PATH:
                competition_id = get_competition_id('Veikkausliiga', season)
            elif inputpath == YKKONEN_PATH:
                competition_id = get_competition_id(u'Ykkönen', season)
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
