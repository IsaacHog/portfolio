import os
import sys
grandparent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, grandparent_dir)
# Above is ugly but it is what it is
from utils.measure_time import measure_time
from leagues import kambi_leagues as leagues

import requests
import gspread
import time
import traceback
from datetime import datetime, timedelta

sa = gspread.service_account(filename='service_account.json')
sh = sa.open("CardBot")
wks = sh.worksheet("KambiCards")

sh_error = sa.open("ErrorLog")
wks_error = sh_error.worksheet("Error")
wks_error_log = sh_error.worksheet("ErrorLog")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.atg.se',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
}

def get_events(leagues):
    print("Getting events...")
    start_time = measure_time()
    events = []
    for league in leagues:
        url = f'https://eu-offering-api.kambicdn.com/offering/v2018/atg/listView/football/{league}.json?lang=sv_SE&market=SE&client_id=2&channel_id=1&ncid=1693053935240&useCombined=true'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json() 
            for event in data['events']:
                if datetime.strptime(event['event']['start'], '%Y-%m-%dT%H:%M:%SZ') > datetime.utcnow() + timedelta(days=1):
                    continue
                if event['event']['state'] == 'STARTED':
                    continue
                events.append({
                    'id': event['event']['id'],
                    'match_name': event['event']['name']
                })
            print("Finished getting events")
        else:
            print("Failed to retrieve events:", response.text)
        measure_time(start_time)
    return events

def get_event_bets(events):
    print("Getting event_bets...")
    start_time = measure_time()
    event_bets = []
    for event in events:
        url = f"https://eu-offering-api.kambicdn.com/offering/v2018/ubse/betoffer/event/{event['id']}.json?lang=sv_SE&market=SE&client_id=2&channel_id=1&ncid=1698228899164&includeParticipants=true"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve events for {event['match_name']}:", response.text)
            continue
        
        data = response.json()
        event_bets.append({
            'id': event['id'],
            'match_name': event['match_name'],
            'lines': []
        })
        for bet_offer in data['betOffers']:
            if 'kort' in bet_offer['criterion']['label']:
                if 'Flest kort' == bet_offer['criterion']['label']: # -0,5
                    try:
                        over_odds = f"{str(bet_offer['outcomes'][0]['odds'])[0]}.{str(bet_offer['outcomes'][0]['odds'])[1]}{str(bet_offer['outcomes'][0]['odds'])[2]}"
                        under_odds = f"{str(bet_offer['outcomes'][2]['odds'])[0]}.{str(bet_offer['outcomes'][2]['odds'])[1]}{str(bet_offer['outcomes'][2]['odds'])[2]}"
                    except:
                        continue
                        
                    event_bets[-1]['lines'].append({
                        'market': "-0,5",
                        'line': "-0.5",
                        'over_odds': over_odds,
                        'under_odds': under_odds
                    })
                    continue
            

                try:
                    over_odds = f"{str(bet_offer['outcomes'][0]['odds'])[0]}.{str(bet_offer['outcomes'][0]['odds'])[1]}{str(bet_offer['outcomes'][0]['odds'])[2]}"
                    under_odds = f"{str(bet_offer['outcomes'][1]['odds'])[0]}.{str(bet_offer['outcomes'][1]['odds'])[1]}{str(bet_offer['outcomes'][1]['odds'])[2]}"
                except:
                    continue

                try: # Fails if not an interesting market
                    line = f"{str(bet_offer['outcomes'][0]['line'])[0]}.{str(bet_offer['outcomes'][0]['line'])[1]}"
                except:
                    continue

                if 'Totalt antal kort - ' in bet_offer['criterion']['label']: # team totals
                    home_team, away_team = event['match_name'].split(" - ")
                    if home_team in bet_offer['criterion']['label']:
                        market = f"Hemma"
                    elif away_team in bet_offer['criterion']['label']:
                        market = f"Borta"
                    event_bets[-1]['lines'].append({
                        'market': market,
                        'line': line,
                        'over_odds': over_odds,
                        'under_odds': under_odds
                    })
                elif 'Totalt antal kort' == bet_offer['criterion']['label']: # totals
                    event_bets[-1]['lines'].append({
                        'market': "total",
                        'line': line,
                        'over_odds': over_odds,
                        'under_odds': under_odds
                    })

    print("Finished getting event_bets")
    measure_time(start_time)
    return event_bets

def spread_bets(event_bets):
    print("Spreading bets...")
    start_time = measure_time()
    bet_arr = []
    for event_bet in event_bets:
        for line in event_bet['lines']:
            if float(line["over_odds"]) > 3 or float(line["over_odds"]) < 1.4:
                continue
            
            if line['market'] == "total":
                bet_arr.append([ event_bet['match_name'], f"Ö{line['line']}", line["over_odds"] ])
                bet_arr.append([ event_bet['match_name'], f"U{line['line']}", line["under_odds"] ])
            elif line['market'] == "Hemma" :
                bet_arr.append([ event_bet['match_name'], f"Hemma Ö{line['line']}", line["over_odds"] ])
                bet_arr.append([ event_bet['match_name'], f"Hemma U{line['line']}", line["under_odds"] ])
            elif line['market'] == "Borta" :
                bet_arr.append([ event_bet['match_name'], f"Borta Ö{line['line']}", line["over_odds"] ])
                bet_arr.append([ event_bet['match_name'], f"Borta U{line['line']}", line["under_odds"] ])
            elif line['market'] == "-0,5" :
                bet_arr.append([ event_bet['match_name'], f"Hemma {line['line']}", line["over_odds"] ])
                bet_arr.append([ event_bet['match_name'], f"Borta {line['line']}", line["under_odds"] ])
                
        bet_arr.append([ f"END{event_bet['match_name']}" ])

    if (len(bet_arr) > 150): # help apps scripts
        chunk_size = len(bet_arr) // 2
        bet_arr_half = bet_arr[:chunk_size]
        bet_arr_other_half = bet_arr[chunk_size:]

        wks.append_rows(bet_arr_half, value_input_option='USER_ENTERED', table_range="A1:D1")
        time.sleep(10)
        wks.append_rows(bet_arr_other_half, value_input_option='USER_ENTERED', table_range="A1:D1")
    else:
        wks.append_rows(bet_arr, value_input_option='USER_ENTERED', table_range="A1:D1")
    print("Spreaded bets")
    measure_time(start_time)

try:
    print("---------------cards_kambi Script initiated--------------------")
    events = get_events(leagues)
    x = 0
    while x < 50:
        print("Starting main loop")
        start_time = measure_time()
        if x % 6 == 0 and x != 0:
            print("Updating events...")
            events = get_events(leagues)  
            print("Updated events")

        event_bets = get_event_bets(events)
        spread_bets(event_bets)
        print("Finished main loop")
        elapsed_time = measure_time(start_time)
        x+=1
        if elapsed_time < 30:
            print("Sleeping for 20 seconds...")
            time.sleep(20)
except Exception:
        error = traceback.format_exc()
        wks_error.append_row([error], table_range="A1:E1")
        wks_error_log.append_row([error], table_range="A1:E1")