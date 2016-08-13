# -*- coding: utf-8 -*-

import sqlite3

DB_FILE = 'football.db'
conn = sqlite3.connect(DB_FILE)

def get_matches(team_id=None, home_team_id=None, away_team_id=None, league_id=None, season_id=None, start=None, end=None, cancelled=None, awarded=None):
    if league_id is not None and type(league_id) is not int:
        raise Exception('Invalid type for league_id %s' % str(type(league_id)))
    if season_id is not None and type(season_id) is not int:
        raise Exception('Invalid type for season_id %s' % str(type(season_id)))
    if team_id is not None and type(team_id) is not int:
        raise Exception('Invalid type for team_id %s' % str(type(team_id)))
    if home_team_id is not None and type(home_team_id) is not int:
        raise Exception('Invalid type for home_team_id %s' % str(type(home_team_id)))
    if away_team_id is not None and type(away_team_id) is not int:
        raise Exception('Invalid type for away_team_id %s' % str(type(away_team_id)))
    if start is not None:
        year, month, day = [int(s) for s in start.split('-')]
        assert year >= 1900 and year <= 2100
        assert month >= 1 and month <= 12
        assert day >= 1 and day <= 31
    if end is not None:
        year, month, day = [int(s) for s in end.split('-')]
        assert year >= 1900 and year <= 2100
        assert month >= 1 and month <= 12
        assert day >= 1 and day <= 31
    if cancelled is not None and type(cancelled) is not bool:
        raise Exception('Invalid type for cancelled %s' % str(type(cancelled)))
    if awarded is not None and type(awarded) is not bool:
        raise Exception('Invalid type for awarded %s' % str(type(awarded)))

    cur = conn.cursor()

    query = '''SELECT home_team.id, away_team.id, match.date, match.full_time_home_team_goals, 
               match.full_time_away_team_goals, match.cancelled, match.awarded, home_team.title, away_team.title, 
               league.id, league.title, season.id, season.title
               FROM match, team as home_team, team as away_team, competition, league, season
               WHERE match.home_team = home_team.id
               AND match.away_team = away_team.id
               AND match.competition = competition.id
               AND competition.league = league.id
               AND competition.season = season.id '''

    if league_id is not None:
        query += ' AND league.id = %s ' % league_id
    if season_id is not None:
        query += ' AND season.id = %s ' % season_id
    if team_id is not None:
        query += ' AND (home_team.id = %s OR away_team.id = %s)' % (team_id, team_id)
    if home_team_id is not None:
        query += ' AND home_team.id = %s' % home_team_id
    if away_team_id is not None:
        query += ' AND away_team.id = %s' % away_team_id
    if start is not None:
        query += " AND match.date >= '%s' " % start
    if end is not None:
        query += " AND match.date < '%s' " % end
    if cancelled is not None:
        if cancelled:
            query += " AND match.cancelled = 1 "
        else:
            query += " AND match.cancelled = 0 "
    if awarded is not None:
        if awarded:
            query += " AND match.awarded = 1 "
        else:
            query += " AND match.awarded = 0 "
            

    cur.execute(query)
    
    matches = []
    for row in cur.fetchall():
        matches.append({'home_team_id': row[0],
                        'away_team_id': row[1],
                        'date': row[2],
                        'home_goals': row[3],
                        'away_goals': row[4],
                        'cancelled': bool(row[5]),
                        'awarded': bool(row[6]),
                        'home_team': row[7],
                        'away_team': row[8],
                        'league_id': row[9],
                        'league': row[10],
                        'season_id': row[11],
                        'season': row[12]})

    return matches


def get_league_id(league):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM league WHERE title = ?''', (league,))
    result = cur.fetchone()
    if not result:
        raise Exception("No league found '%s'" % team)
    return result[0]
    

def get_season_id(season):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM season WHERE title = ?''', (season,))
    result = cur.fetchone()
    if not result:
        raise Exception("No season found '%s'" % team)
    return result[0]
    

def get_team_id(team):
    cur = conn.cursor()
    cur.execute('''SELECT id FROM team WHERE title = ?''', (team,))
    result = cur.fetchone()
    if not result:
        raise Exception("No team found '%s'" % team)
    return result[0]


def get_team_name(team_id):
    cur = conn.cursor()
    cur.execute('''SELECT title FROM team WHERE id = ?''', (team_id,))
    result = cur.fetchone()
    if not result:
        raise Exception("No team found with id %s" % team)
    return result[0]


def get_teams():
    cur = conn.cursor()
    cur.execute('''SELECT id, title FROM team''')
    return cur.fetchall()

