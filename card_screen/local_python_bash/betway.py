import os
import sys
grandparent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, grandparent_dir)
# Above is ugly but it is what it is
from utils.measure_time import measure_time
from leagues import betway_leagues as leagues

import requests
import gspread
import time
import traceback
from datetime import datetime, timedelta
import json

from seleniumbase import Driver

sa = gspread.service_account(filename='service_account.json')
sh = sa.open("CardBot")
wks = sh.worksheet("BetwayCards")

driver = Driver(headless=False,uc=True)
driver.set_window_size(600, 600)

sh_error = sa.open("ErrorLog")
wks_error = sh_error.worksheet("Error")
wks_error_log = sh_error.worksheet("ErrorLog")



def get_headers():
    print("Getting headers...")
    driver.get("https://betway.se/en/sports")
    print("Getting cookies...")
    time.sleep(10)
    cookies = driver.get_cookies()
    cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    print("Got cookies")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Accept': 'application/json; charset=UTF-8',
        'Accept-Language': 'en-GB,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Length': '498',
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://betway.se',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://betway.se/',
        'Cookie': f'bw_BrowserId={cookies_dict["bw_BrowserId"]}; AMCV_74756B615BE2FD4A0A495EB8%40AdobeOrg={cookies_dict["AMCV_74756B615BE2FD4A0A495EB8%40AdobeOrg"]}; ens_firstVisit=1696675272908; ssc_DeviceId={cookies_dict["ssc_DeviceId"]}; ssc_DeviceId_HttpOnly={cookies_dict["ssc_DeviceId_HttpOnly"]}; userLanguage=en; ens_loginPersistant=1; lastUserLogin=sports; ens_fundsDeposited=1696685070785; ens_betPlaced=1698147946132; hash=de01084c-b934-41fd-8c22-753b6226e185; bw_SessionId={cookies_dict["bw_SessionId"]}; ens_firstPageView=false; TrackingVisitId={cookies_dict["TrackingVisitId"]}; AMCVS_74756B615BE2FD4A0A495EB8%40AdobeOrg=1; s_cc=true; StaticResourcesVersion={cookies_dict["StaticResourcesVersion"]}; ssc_btag={cookies_dict["ssc_btag"]}; SpinSportVisitId={cookies_dict["SpinSportVisitId"]}; TimezoneOffset=120; __cf_bm={cookies_dict["__cf_bm"]}; gpv_pn=%3Ase%3Asports%3Agrp%3Asoccer%3Aengland%3Apremier-league',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': "Windows",
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode':'cors',
        'Sec-Fetch-Site':'same-site',
    }
    print("Got headers")
    return headers

def get_event_ids(leagues, headers): 
    print("Getting event_ids...")
    start_time = measure_time()
    event_ids = []
    for league in leagues:
        payload = {
                "LanguageId":1,
                "ClientTypeId":2,
                "BrandId":3,
                "JurisdictionId":6,
                "ClientIntegratorId":1,
                "CategoryCName":"soccer",
                "SubCategoryCName": league['country'],
                "GroupCName": league['league'],
                "BrowserId":5,
                "OsId":3,
                "ApplicationVersion":"",
                "BrowserVersion":"118.0",
                "TerritoryId":254,
                "CorrelationId": "e6534e7d-3ee2-4729-aa55-18a7f06b115e",
                "VisitId":"c38a22cc-c7ab-464b-8bc9-fa5cb95d5261",
                "ViewName":"sports",
                "JourneyId":"2d054c5d-034d-474f-83dc-ebbcc9000bec"
                }
            
        url = f'https://sportsapi.betway.se/api/Events/v2/GetGroup'
        payload_str = json.dumps(payload, ensure_ascii=False)
        response = requests.post(url=url, headers=headers, data=payload_str.encode('utf-8'))
        if response.status_code == 200:
            data = response.json() 
            for index in range(len(data['Categories'][0]['Events'])):
                event_date = data['EventSummaries'][index]['StartTime']
                if datetime.strptime(event_date, '%Y-%m-%dT%H:%M:%S') > datetime.utcnow() + timedelta(days=1):
                    continue
                #if event['event']['state'] == 'STARTED':
                    continue
                event_id = data['Categories'][0]['Events'][index]
                event_ids.append(event_id)
            print(f"Finished getting event_ids for {league}")
        else:
            print("Failed to retrieve event_ids:", response.text)
        measure_time(start_time)
    return event_ids

def get_event_bets(event_ids, headers): # CONTINUE HERE!!! :D
    print("Getting event_bets...")
    start_time = measure_time()
    event_bets = []
    for event_id in event_ids:
        payload = {
            "EventId": event_id,
            "LanguageId": 1,
            "ClientTypeId": 2,
            "BrandId": 3,
            "JurisdictionId": 6,
            "ClientIntegratorId": 1,
            "ScoreboardRequest": {
                "ScoreboardType": 0,
                "IncidentRequest": {}
            },
            "BrowserId": 3,
            "OsId": 3,
            "ApplicationVersion": "",
            "BrowserVersion": "118.0.0.0",
            "OsVersion": "NT 10.0",
            "SessionId": "null",
            "TerritoryId": 254,
            "CorrelationId": "37f1eb5a-d6bc-4f57-981d-53e184a37574",
            "VisitId": "232b5707-9bb1-417b-bb3f-8741854a9a33",
            "ViewName": "sports",
            "JourneyId": "6aaa658a-8eb6-4817-83b0-e5ff6a409ddd"
        }
            
        url = f'https://sportsapi.betway.se/api/Events/v2/GetEventDetails'
        payload_str = json.dumps(payload, ensure_ascii=False)
        response = requests.post(url=url, headers=headers, data=payload_str.encode('utf-8'))
        if response.status_code != 200:
            print(f"Failed to retrieve events for {event_id}:", response.text)
            continue
        
        data = response.json()
        event_bets.append({
            'id': event_id,
            'match_name': data['Event']['EventName'].replace(' - ', ' v '),
            'lines': []
        })

        for market in data['Markets']:
            if 'Cards' not in market['Title']:
                continue

            outcome_ids = market['Outcomes'][0]
            outcomes = []
            for outcome_id in outcome_ids:
                try:
                    outcome_index = (next(index for index, d in enumerate(data['Outcomes']) if d['Id'] == outcome_id))
                    outcomes.append(data['Outcomes'][outcome_index])
                except StopIteration:
                    continue
            
            # 2-way
            over_odds = outcomes[0]['OddsDecimal']
            under_odds = outcomes[1]['OddsDecimal']
            if 'Total Cards' == market['Title']: 
                event_bets[-1]['lines'].append({
                    'market': "total",
                    'line': outcomes[0]['HandicapDisplay'],
                    'over_odds': over_odds,
                    'under_odds': under_odds
                })
                continue

            elif 'Team A - Total Cards' == market['Title']:
                event_bets[-1]['lines'].append({
                    'market': "Hemma",
                    'line': outcomes[0]['HandicapDisplay'],
                    'over_odds': over_odds,
                    'under_odds': under_odds
                })
                continue
            elif 'Team B - Total Cards' == market['Title']: 
                event_bets[-1]['lines'].append({
                    'market': "Borta",
                    'line': outcomes[0]['HandicapDisplay'],
                    'over_odds': over_odds,
                    'under_odds': under_odds
                })
                continue
            
            # 3-way
            home_odds = outcomes[0]['OddsDecimal']
            away_odds = outcomes[2]['OddsDecimal']

            if 'Total Cards - Handicap' == market['Title']:
                event_bets[-1]['lines'].append({
                    'market': "handicap",
                    'line': float(outcomes[0]['Handicap']) - 0.5,
                    'over_odds': home_odds,
                    'under_odds': away_odds
                })
            elif 'Team With Most Cards' == market['Title']:
                event_bets[-1]['lines'].append({
                    'market': "-0,5",
                    'line': "-0.5",
                    'over_odds': home_odds,
                    'under_odds': away_odds
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
            elif line['market'] == "handicap" :
                home_handicap = float(line['line'])
                away_handicap = -1 * float(home_handicap + 1)

                bet_arr.append([event_bet['match_name'], f"Hemma {home_handicap:+}", line["over_odds"]])
                bet_arr.append([event_bet['match_name'], f"Borta {away_handicap:+}", line["under_odds"]])
                
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
    print("---------------cards_betway Script initiated--------------------")
    headers = get_headers()
    event_ids = get_event_ids(leagues=leagues, headers=headers)
    x = 0
    while x < 500:
        print("Starting main loop")
        start_time = measure_time()
        if x % 6 == 0 and x != 0:
            print("Updating event_ids...")
            headers = get_headers()
            event_ids = get_event_ids(leagues=leagues, headers=headers) 
            print("Updated event_ids")

        event_bets = get_event_bets(event_ids=event_ids, headers=headers)
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