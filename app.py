import datetime as dt
import json
import urllib.request
import urllib.error
from urllib.parse import urlencode
from flask import Flask, send_from_directory, render_template, request, jsonify

from mlb import FullSchedule


app = Flask(__name__, static_folder='static', template_folder='templates')


SPORT_IDS = {
    'MLB': 1,
    'AAA': 11,
    'AA': 12,
    'A+': 13,
    'A': 14,
    'ROOKIE BALL': 16,
    'WINTER LEAGUE': 17,
    'IND': 23,
}


def fetch_schedule(date: str, league: str):
    sport_id = SPORT_IDS.get(league, SPORT_IDS['MLB'])
    params = urlencode({'sportId': sport_id, 'date': date})
    url = f'https://statsapi.mlb.com/api/v1/schedule?{params}'
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.load(resp)
    games = []
    for day in data.get('dates', []):
        for g in day.get('games', []):
            games.append(FullSchedule(g, league))
    games.sort(key=lambda g: g.get_datetime())
    return games


@app.route('/gamepk_lookup', methods=['GET', 'POST'])
def gamepk_lookup():
    error = None
    games = []
    date_val = ''
    league_val = ''

    if request.method == 'POST':
        date_val = request.form.get('date', '').strip()
        league_val = request.form.get('league', '').strip()
        if not date_val:
            error = 'Date is required.'
        else:
            try:
                dt.datetime.strptime(date_val, '%Y-%m-%d')
                games = fetch_schedule(date_val, league_val or 'MLB')
                if not games:
                    error = 'No games scheduled for that date.'
            except ValueError:
                error = 'Invalid date format. Use YYYY-MM-DD.'
            except urllib.error.URLError:
                error = 'Error retrieving schedule.'

    return render_template(
        'gamepk_lookup.html',
        games=games,
        error=error,
        sport_ids=SPORT_IDS,
        selected_date=date_val,
        selected_league=league_val,
    )


@app.route('/api/gamepk_lookup')
def gamepk_lookup_api():
    date_val = request.args.get('date', '').strip()
    league_val = request.args.get('league', '').strip()
    if not date_val:
        return jsonify({'error': 'Date is required'}), 400
    try:
        dt.datetime.strptime(date_val, '%Y-%m-%d')
        games = fetch_schedule(date_val, league_val or 'MLB')
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD.'}), 400
    except urllib.error.URLError:
        return jsonify({'error': 'Error retrieving schedule'}), 502

    result = [
        {
            'game_pk': g.game_pk,
            'home_team': g.home_team.name,
            'away_team': g.away_team.name,
            'status': g.detailed_state,
        }
        for g in games
    ]
    return jsonify({'games': result})

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/builds/<path:filename>')
def builds(filename):
    return send_from_directory('static/builds', filename, as_attachment=True)

if __name__ == '__main__':
    app.run()
