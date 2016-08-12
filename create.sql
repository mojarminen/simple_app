CREATE TABLE league (
  id integer,
  title text NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (title)
);

CREATE TABLE season (
  id integer,
  title text NOT NULL,
  PRIMARY KEY (id),
  UNIQUE (title)
);

CREATE TABLE competition (
  id integer,
  title text,
  league integer,
  season integer,
  PRIMARY KEY (id),
  UNIQUE (title),
  FOREIGN KEY (league) REFERENCES league(id),
  FOREIGN KEY (season) REFERENCES season(id)
);

CREATE TABLE team (
  id integer,
  title text NOT NULL,
  aliases text,
  PRIMARY KEY (id),
  UNIQUE (title)
);

CREATE TABLE match (
  id integer,
  competition integer NOT NULL, 
  "date" timestamp NOT NULL,
  neutral_field boolean NOT NULL DEFAULT FALSE,
  home_team integer NOT NULL,
  away_team integer NOT NULL,
  full_time_home_team_goals integer,
  full_time_away_team_goals integer,
  PRIMARY KEY (id),
  UNIQUE ("date", home_team, away_team),
  FOREIGN KEY (competition) REFERENCES competition(id),
  FOREIGN KEY (home_team) REFERENCES team(id),
  FOREIGN KEY (away_team) REFERENCES team(id)
);

CREATE TABLE odds_1X2 (
  "match" integer,
  booker text,
  home_win real NOT NULL,
  draw real NOT NULL,
  away_win real NOT NULL,
  PRIMARY KEY ("match", booker)
);
