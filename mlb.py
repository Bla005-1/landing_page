import datetime as dt


class Team:
    def __init__(self, team_data: dict):
        self.name = team_data.get('team', {}).get('name')
        self.id = team_data.get('team', {}).get('id')
        self.link = team_data.get('team', {}).get('link')
        self.wins = team_data.get('leagueRecord', {}).get('wins')
        self.losses = team_data.get('leagueRecord', {}).get('losses')
        self.pct = team_data.get('leagueRecord', {}).get('pct')
        self.score = team_data.get('score')
        self.is_winner = team_data.get('isWinner', False)
        self.split_squad = team_data.get('splitSquad', False)
        self.series_number = team_data.get('seriesNumber')

    def __repr__(self):
        return (
            f"Team(name={self.name}, id={self.id}, wins={self.wins}, "
            f"losses={self.losses}, pct={self.pct}, score={self.score}, "
            f"is_winner={self.is_winner})"
        )


class LiteSchedule:
    def __init__(self, game_data: dict, league):
        self.league = league
        self.game_data = game_data
        self.game_pk = game_data.get('gamePk')
        self.game_guid = game_data.get('gameGuid')
        self.link = game_data.get('link')
        self.game_type = game_data.get('gameType')
        self.season = game_data.get('season')
        self.date = game_data.get('gameDate')
        self.official_date = game_data.get('officialDate')

        status = game_data.get('status', {})
        self.abstract_game_state = status.get('abstractGameState')
        self.coded_game_state = status.get('codedGameState')
        self.detailed_state = status.get('detailedState')
        self.status_code = status.get('statusCode')
        self.start_time_tbd = status.get('startTimeTBD', False)
        self.abstract_game_code = status.get('abstractGameCode')
        self.reason = status.get('reason')

        self.reschedule_date = game_data.get('rescheduleDate')
        self.reschedule_game_date = game_data.get('rescheduleGameDate')
        self.rescheduled_from = game_data.get('rescheduledFrom')
        self.rescheduled_from_date = game_data.get('rescheduledFromDate')
        self.is_rescheduled = True if self.reschedule_date else False

    def get_datetime(self) -> dt.datetime:
        raw_date = self.reschedule_date or self.date
        utc_time = dt.datetime.strptime(raw_date, '%Y-%m-%dT%H:%M:%SZ')
        utc_time = utc_time.replace(tzinfo=dt.timezone.utc)
        return utc_time


class FullSchedule(LiteSchedule):
    def __init__(self, game_data: dict, league):
        super().__init__(game_data, league)
        teams = game_data.get('teams', {})
        self.away_team = Team(teams.get('away', {}))
        self.home_team = Team(teams.get('home', {}))

        self.venue = game_data.get('venue', {}).get('name')
        self.venue_id = game_data.get('venue', {}).get('id')
        self.venue_link = game_data.get('venue', {}).get('link')
        self.content_link = game_data.get('content', {}).get('link')

        self.scheduled_innings = game_data.get('scheduledInnings', 9)
        self.games_in_series = game_data.get('gamesInSeries')
        self.series_game_number = game_data.get('seriesGameNumber')
        self.series_description = game_data.get('seriesDescription')
        self.is_tie = game_data.get('isTie', False)
        self.double_header = game_data.get('doubleHeader', 'N')
        self.gameday_type = game_data.get('gamedayType')
        self.day_night = game_data.get('dayNight')
        self.description = game_data.get('description')

    def __repr__(self):
        return (
            f"Game(game_pk={self.game_pk}, date={self.date}, official_date={self.official_date}, "
            f"status={{'abstract': {self.abstract_game_state}, 'coded': {self.coded_game_state}, "
            f"'detailed': {self.detailed_state}, 'reason': {self.reason}}}, "
            f"home_team={self.home_team}, away_team={self.away_team}, "
            f"venue={self.venue}, series={{'games_in_series': {self.games_in_series}, "
            f"'series_game_number': {self.series_game_number}, 'description': {self.series_description}}})"
        )
