
from datetime import datetime, timedelta
import requests
from config import WKS_KAMBISHOTS, MAIN_LOOP_ITERATIONS, WKS_STATUS, WKS_ERROR, KAMBI_TEAM_NAMES_TO_CONVERT
import json
import time
import requests
import traceback
import unidecode

todays_date = datetime.today()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.unibet.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
}

def throw_error(attempted_action="", error=""):
    WKS_ERROR.append_row([datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), attempted_action, error], table_range="A1:E1")

def get_events():
    print("Getting events...")
    leagues = [
        "england/premier_league",
        "italy/serie_a",
        "spain/la_liga",
        "germany/bundesliga",
        "france/ligue_1",
    ]
    
    events = []
    for league in leagues:
        url = f'https://eu-offering-api.kambicdn.com/offering/v2018/ubca/listView/football/{league}.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&ncid=1693053935240&useCombined=true'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json() 
            for event in data['events']:
                if datetime.strptime(event['event']['start'], '%Y-%m-%dT%H:%M:%SZ').day != todays_date.day:
                    continue
                if event['event']['state'] == 'STARTED':
                    continue
                events.append({
                    'id': event['event']['id'],
                    'match_name': unidecode.unidecode(event['event']['englishName']),
                    'path': json.dumps(event['event']['path']),
                    'eventStart': (datetime.strptime(event['event']['start'], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=1)).isoformat(),
                })
        else:
            print("Failed to retrieve events:", response.text)
    print(f"Got {len(events)} events...")
    return events

def get_betoffers(events):
    print("Getting betoffers...")
    betoffers = []
    for event in events:
        if (datetime.strptime(event['eventStart'], '%Y-%m-%dT%H:%M:%S') > datetime.now() + timedelta(minutes=65)):
            continue
        url = f"https://eu-offering-api.kambicdn.com/offering/v2018/ubca/betoffer/event/{event['id']}.json?lang=en_GB&market=ZZ&client_id=2&channel_id=1&ncid=1698228899164&includeParticipants=true"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve events for {event['match_name']}:", response.text)
            continue
        
        data = response.json()
        betoffers.append({
            'match_name': event['match_name'],
            'lines': {
                'total': [],
                'home': [],
                'away': []
            }
        })
        for bet_offer in data['betOffers']:
            if 'Total Shots' in bet_offer['criterion']['label'] and 'Target' not in bet_offer['criterion']['label']:
                try:
                    over_odds = next(outcome['odds']/1000 for outcome in bet_offer['outcomes'] if outcome['label'] == 'Over')
                    under_odds = next(outcome['odds']/1000 for outcome in bet_offer['outcomes'] if outcome['label'] == 'Under')
                except:
                    continue

                try: # Fails if not an interesting market
                    line = str(bet_offer['outcomes'][0]['line']/1000)
                except:
                    continue

                if 'Total Shots by ' in bet_offer['criterion']['label']: # team totals
                    home_team, away_team = event['match_name'].split(" - ")
                    if home_team in unidecode.unidecode(bet_offer['criterion']['label']):
                        market = f"home"
                    elif away_team in unidecode.unidecode(bet_offer['criterion']['label']):
                        market = f"away"
                    betoffers[-1]['lines'][market].append({
                        'line': f"O{line}",
                        'odds': over_odds
                    })
                    betoffers[-1]['lines'][market].append({
                        'line': f"U{line}",
                        'odds': under_odds
                    })
                elif 'Total Shots (Settled using Opta data)' == bet_offer['criterion']['label']: # totals
                    betoffers[-1]['lines']["total"].append({
                        'line': f"O{line}",
                        'odds': over_odds
                    })
                    betoffers[-1]['lines']["total"].append({
                        'line': f"U{line}",
                        'odds': under_odds
                    })

    print(f"Got {len(betoffers)} betoffers")
    return betoffers

def convert_betoffer_match_name(betoffers):
    for index, betoffer in enumerate(betoffers):
        for team in KAMBI_TEAM_NAMES_TO_CONVERT:
            if team['betoffer_name'] in betoffer['match_name']:
                betoffers[index]['match_name'] = betoffer['match_name'].replace(team['betoffer_name'], team['convert_to_name'])
    return betoffers

def add_bets_to_wkskambi_shots(bet_data_to_append):
    rows_to_append = [[json.dumps(bet)] for bet in bet_data_to_append]
    WKS_KAMBISHOTS.append_rows(rows_to_append, value_input_option='USER_ENTERED', table_range="A1:D1")
    print("bet_data spreaded")
    return []

def bot_loop():
    for i in range (0, MAIN_LOOP_ITERATIONS):
        if WKS_STATUS.cell(2,2).value != "TRUE":
            print("statusSakoShots is false, sleeping for 300 seconds...")
            time.sleep(300)
            continue

        events = get_events()
        betoffers = get_betoffers(events)
        
        betoffers = convert_betoffer_match_name(betoffers)
        add_bets_to_wkskambi_shots(betoffers)

        print("Finished main loop, sleeping for 40 seconds...") 
        time.sleep(40)

print("---------------shots_kambi Script initiated--------------------")
try:
    bot_loop()
except Exception:
    throw_error("Last try except", traceback.format_exc())