import os
import requests
import json
from flask import Flask, render_template, request
from datetime import datetime

from constants import TEAMS, LEAGUES

API_KEY = os.getenv("DATAROBOT_API_KEY")
DEPLOYMENT_SERVER_URL = os.getenv("DATAROBOT_DEPLOYMENT_SERVER_URL")
DEPLOYMENT_ID = os.getenv("DATAROBOT_DEPLOYMENT_ID")
PREDICTION_HEADERS = {
    "Authorization": "Bearer {}".format(API_KEY),
    "Content-Type": "application/json"
}

app = Flask(__name__)

def normalize_score(score):
    if score is None:
        return None
    elif(score < 0.7):
        return 0
    else:
        return round(score)

@app.route('/')
def root():
    spi1 = spi2 = score1 = score2 = None
    team1 = request.args.get('team1', None)
    team2 = request.args.get('team2', None)
    league = request.args.get('league', None)

    if team1 and team2 and league:
        spi1 = TEAMS[team1]
        spi2 = TEAMS[team2]

        matches = [
            {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'league': league,
                'team1': team1,
                'team2': team2,
                'spi1': spi1,
                'spi2': spi2
            },
            {
                'date': datetime.now().strftime("%Y-%m-%d"),
                'league': league,
                'team1': team2,
                'team2': team1,
                'spi1': spi2,
                'spi2': spi1
            }
        ]
        predictions = requests.post(
            "{server_url}/api/v2/deployments/{deployment_id}/predictions".format(server_url=DEPLOYMENT_SERVER_URL, deployment_id=DEPLOYMENT_ID),
            headers=PREDICTION_HEADERS,
            data=json.dumps(matches),
        )

        print(predictions.json())

        score1 = float(predictions.json()['data'][0]['prediction'])
        score2 = float(predictions.json()['data'][1]['prediction'])

    return render_template(
        'index.html',
        teams=TEAMS.keys(),
        leagues=LEAGUES,
        team1=team1,
        team2=team2,
        league=league,
        score1=normalize_score(score1),
        score2=normalize_score(score2)
    )
