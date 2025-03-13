import os
import sys
grandparent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, grandparent_dir)
# Above is ugly but it is what it is
from utils.measure_time import measure_time
from leagues import betinia_leagues as leagues

import requests
import gspread
import time
import traceback
from datetime import datetime, timedelta, timezone

sa = gspread.service_account(filename='service_account.json')
sh = sa.open("CardBot")
wks = sh.worksheet("BetiniaCards")

sh_error = sa.open("ErrorLog")
wks_error = sh_error.worksheet("Error")
wks_error_log = sh_error.worksheet("ErrorLog")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://betinia.se/',
    'Host': 'sb2frontend-altenar2.biahosted.com',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
}

def get_events(leagues):
    print("Getting events...")
    start_time = measure_time()
    events = []
    for league in leagues:
        url = f'https://sb2frontend-altenar2.biahosted.com/api/widget/GetEvents?culture=sv-SE&timezoneOffset=-120&integration=betiniase&deviceType=1&numFormat=en-GB&countryCode=SE&eventCount=0&sportId=0&champIds={league}'
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json() 
            for event in data['events']:
                if datetime.strptime(event['startDate'], '%Y-%m-%dT%H:%M:%S%z') > datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=1):
                    continue
                #if datetime.strptime(event['betting_end'], '%Y-%m-%dT%H:%M:%S%z') < datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(minutes=2):
                    #continue
                events.append({
                    'id': event['id'],
                    'match_name': event['name'].replace("vs.", "-")
                })
            print("Finished getting events")
        else:
            print("Failed to retrieve events:", response.text)
    measure_time(start_time)
    return events

def get_event_bets(events): # Uglyyyy
    print("Getting event_bets...")
    start_time = measure_time()
    event_bets = []
    for event in events:
        url = f"https://sb2frontend-altenar2.biahosted.com/api/widget/GetEventDetails?culture=sv-SE&timezoneOffset=-120&integration=betiniase&deviceType=1&numFormat=en-GB&countryCode=SE&eventId={event['id']}"
        try:
            response = requests.get(url, headers=headers)
        except:
            continue
        if response.status_code != 200:
            print(f"Failed to retrieve events for {event['match_name']}:", response.text)
            continue
        
        data = response.json()
        event_bets.append({
            'id': event['id'],
            'match_name': event['match_name'],
            'lines': []
        })

        home_team, away_team = event['match_name'].split(" - ")
        lines = []
        fetched_markets = []
        for market_object in data['markets']:
            if 'total' in fetched_markets and '-0.5' in fetched_markets:
                break
            if 'shortName' not in market_object.keys(): # Next 10-min lines don't have shortName key
                continue

            if 'Totalt antal kort' in market_object['shortName']:
                market = "total"
                odds_ids_over = market_object['desktopOddIds'][0]
                odds_ids_under = market_object['desktopOddIds'][1]
            elif 'Kort 1x2' in market_object['shortName']:
                market = "-0.5"
                odds_ids = [market_object['desktopOddIds'][0][0], market_object['desktopOddIds'][1][0], market_object['desktopOddIds'][2][0]]
            else:
                continue
            
            data['odds'] = data['odds'][200:] # Remove first odds as they are not cards
            if market == "total":
                if market in fetched_markets:
                    continue

                for x, odds in enumerate(data['odds']):
                    if x > 900:
                        break
                    for odds_id in odds_ids_over:
                        if odds['id'] != odds_id:
                            continue

                        is_in_lines = False
                        for existing_line in lines: # Again two of each market...
                            if odds['id'] == existing_line['id']:
                                is_in_lines = True
                        if is_in_lines:
                            continue

                        if odds['price'] > 3 or odds['price'] < 1.35:
                            continue

                        lines.append({
                            'id': odds['id'],
                            'line': odds['name'].replace("Över ", "Ö"),
                            'odds': odds['price'],
                        })
                        break
                    for odds_id in odds_ids_under:
                        if odds['id'] != odds_id:
                            continue

                        is_in_lines = False
                        for existing_line in lines: # Again two of each market...
                            if odds['id'] == existing_line['id']:
                                is_in_lines = True
                        if is_in_lines:
                            continue

                        lines.append({
                            'id': odds['id'],
                            'line': odds['name'].replace("Under ", "U"),
                            'odds': odds['price'],
                        })
                        break

            elif market == "-0.5":
                if market in fetched_markets: # Again two of each market...
                    continue

                for x, odds in enumerate(data['odds']):
                    if x > 900:
                        break
                    for odds_id in odds_ids:
                        if odds['id'] != odds_id:
                            continue

                        if odds['name'] == home_team:
                            line = "Hemma -0.5"
                        elif odds['name'] == away_team:
                            line = "Borta -0.5"
                        else:
                            continue
                        
                        is_in_lines = False
                        for existing_line in lines: # Again two of each market...
                            if odds['id'] == existing_line['id']:
                                is_in_lines = True
                        if is_in_lines:
                            continue

                        lines.append({
                            'id': odds['id'],
                            'line': line,
                            'odds': odds['price'],
                        })
                        break
            
            if len(lines) > 0:
                event_bets[-1]['lines'].append({
                    'market': market,
                    'lines': lines,
                })
                lines = []
                fetched_markets.append(market)
        
    print("Finished getting event_bets")
    measure_time(start_time)
    return event_bets

def spread_bets(event_bets):
    print("Spreading bets...")
    start_time = measure_time()
    bet_arr = []
    for event_bet in event_bets: # Uglyyyy
        for market_arr in event_bet['lines']:
            market = market_arr['market']
            for line in market_arr['lines']:
                if line["odds"] > 3 or line["odds"] < 1.4:
                    continue
                
                if market == "total":
                    bet_arr.append([ event_bet['match_name'], f"{line['line']}", line["odds"] ])
                elif market == "-0.5" :
                    bet_arr.append([ event_bet['match_name'], f"{line['line']}", line["odds"] ])
                
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
    print("---------------cards_betinia Script initiated--------------------")
    events = get_events(leagues)
    x = 0
    while x < 50:
        print("Starting main loop")
        start_time = measure_time()
        if x % 6 == 0 and x != 0:
            print("Updating events and event_bets...")
            events = get_events(leagues) 
            print("Updated events")

        bets = get_event_bets(events) 
        spread_bets(bets)
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
