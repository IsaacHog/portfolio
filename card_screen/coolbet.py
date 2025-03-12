import os
import sys
grandparent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, grandparent_dir)
# Above is ugly but it is what it is
from utils.measure_time import measure_time
from leagues import coolbet_leagues as leagues

import requests
import gspread
import time
import traceback
from datetime import datetime, timedelta, timezone

sa = gspread.service_account(filename='service_account.json')
sh = sa.open("CardBot")
wks = sh.worksheet("CoolbetCards")

sh_error = sa.open("ErrorLog")
wks_error = sh_error.worksheet("Error")
wks_error_log = sh_error.worksheet("ErrorLog")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
    'Accept-Language': 'en-GB,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Host': 'www.coolbet.com',
    'Cookie': 'visid_incap_723517=rtcRS0fzT7iFCbdcTfjJbzij7WQAAAAAQUIPAAAAAAAfh0gWsTe+KLhuOIpjTsJM; G_ENABLED_IDPS=google; uuid=0280d940-7c83-4b08-b710-883d362e06cd; reese84=3:c1h3sSdaHuNhFA2SNCKFkg==:dGj4cm4TgwWqvIwEKuBEfEF41BsTVSi2Ad9AZzM/e7qFa9r5ZtxUntLv/bL6aZorKTdwXw278jjU/z5tvPNXC8wc0ubK0xQYPwicOMyEG8skorIALQdG4dwAMPbfJh6ZorSGY7UjDBWkfJRa6YGlx4ro2Zr/QDIigc4o8yA6SRsBP29azqScf8UdAJzYXmvGvpQ/bAHdz/A1whA6TV0pabgFTQfQpefF7wJXTt58I1dIFq4n7afp3UvIYZFu47E/f0JErAPEnPfpZ8Zn3KIX4CXsTXfnyhpdtqMWtib4igYzXwkYX61ABH+wJOIZWEcxkA/oyZEU2AE5WanPbmdrDwWtXchvCYyvHs/39QYaJjy1mKVAqIc2tVvoIz1KzMkkjvV7uvimlvpE8qTC7mSHjRmKhJRAYVlmDByC9RCiS/mS0u8+Mqk+0h+CEmIQclQbtralkQ+86652HNrIeNgjxQ==:RsY75PK4Qr1nUci2dK1jZ7Iu/Sz2261KPB7qIXOY7RA=; _cq_duid=1.1683454464.BJ3XrKU1jwuLZAc5; incap_ses_1096_723517=YPeMW8hHGziufwcVdcc1D/w1FWUAAAAASalDfE6Ld6vFQUwWOUf5Xg==; nlbi_723517=1ccwTp3q8AsVdut+mItahgAAAAB0m9FpR5rmRCZDRw2UsnyK; nlbi_723517_2147483392=UrTSShaiAy1H8RWWmItahgAAAAC4Be0bjX97nKaGvdeftAaR',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
}

def get_events(leagues):
    print("Getting events...")
    start_time = measure_time()
    events = []
    for league in leagues:
        url = f'https://www.coolbet.com/s/sbgate/sports/fo-category/?categoryId={league}&country=SE&isMobile=0&language=sv&layout=EUROPEAN&limit=6&province='
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json() 
            for event in data[0]['matches']:
                if datetime.strptime(event['match_start'], '%Y-%m-%dT%H:%M:%S%z') > datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(days=1):
                    continue
                if datetime.strptime(event['betting_end'], '%Y-%m-%dT%H:%M:%S%z') < datetime.utcnow().replace(tzinfo=timezone.utc) + timedelta(minutes=2):
                    continue
                events.append({
                    'id': event['id'],
                    'match_name': f"{event['home_team_name']} - {event['away_team_name']}"
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
        url = f"https://www.coolbet.com/s/sbgate/sports/fo-market/sidebets?country=SE&language=sv&layout=EUROPEAN&marketTypeGroupId=6&matchId={event['id']}&matchStatus=OPEN&province="
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to retrieve events for {event['match_name']}:", response.text)
            continue
        
        data = response.json()
        event_bets.append({
            'id': event['id'],
            'match_name': event['match_name'],
            'market_lines': [],
            'lines': []
        })
        for market_object in data['markets']:
            if 'Antal kort Över/Under' in market_object['market_type_name']:
                market = "total"
            elif '[Home] totalt antal kort' in market_object['market_type_name']:
                market = "Hemma"
            elif '[Away] totalt antal kort' in market_object['market_type_name']:
                market = "Borta"
            elif 'Flest kort (2-vägs)' in market_object['market_type_name']:
                market = "+0"
            elif 'Flest kort (3-vägs)' in market_object['market_type_name']:
                market = "-0.5"
            else:
                continue

            lines = []
            for line in market_object['markets']:
                if float(line['line']).is_integer():
                    line['line'] = f"{int(float(line['line']))}.0"

                if market == "-0.5": # Special case
                    lines.append({
                        'id': line['id'],
                        'line': line['line'],
                        'over_id': line['outcomes'][0]['id'],
                        'under_id': line['outcomes'][2]['id']
                    })
                    continue

                lines.append({
                    'id': line['id'],
                    'line': line['line'],
                    'over_id': line['outcomes'][0]['id'],
                    'under_id': line['outcomes'][1]['id']
                })
                
            event_bets[-1]['market_lines'].append({
                        'market': market,
                        'lines': lines,
            })
        
    print("Finished getting event_bets")
    measure_time(start_time)
    return event_bets

def get_bets(event_bets):
    for x, event_bet in enumerate(event_bets):
        ids_to_request_odds = []
        for market_line in event_bet['market_lines']:
            for line in market_line['lines']:
                ids_to_request_odds.append(line['id'])

        url = "https://www.coolbet.com/s/sb-odds/odds/current/fo"
        request_data = {"where":{"market_id":{"in":ids_to_request_odds}}}
        response = requests.post(url, headers=headers, json=request_data)
        if response.status_code != 200:
            print(f"Failed to retrieve events for {event_bet['match_name']}:", response.text)
            continue
        
        data = response.json()
        for market_line in event_bet['market_lines']:
            for line in market_line['lines']:
                for bet_object in data.items():
                    if bet_object[1]['market_id'] == line['id']:
                        if bet_object[1]['outcome_id'] == line['over_id']:
                            event_bets[x]['lines'].append({
                                'market': market_line['market'],
                                'line': line['line'],
                                'over_odds': bet_object[1]['value']
                            })
                        elif bet_object[1]['outcome_id'] == line['under_id']:
                            event_bets[x]['lines'][-1]['under_odds'] = bet_object[1]['value']
    return event_bets

def spread_bets(event_bets):
    print("Spreading bets...")
    start_time = measure_time()
    bet_arr = []
    for event_bet in event_bets:
        for line in event_bet['lines']:
            if line["over_odds"] > 3 or line["over_odds"] < 1.4:
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
            elif line['market'] == "+0" :
                bet_arr.append([ event_bet['match_name'], f"Hemma +0", line["over_odds"] ])
                bet_arr.append([ event_bet['match_name'], f"Borta +0", line["under_odds"] ])
            elif line['market'] == "-0.5" :
                bet_arr.append([ event_bet['match_name'], f"Hemma -0.5", line["over_odds"] ])
                bet_arr.append([ event_bet['match_name'], f"Borta -0.5", line["under_odds"] ])
                
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
    print("---------------cards_coolbet Script initiated--------------------")
    events = get_events(leagues)
    event_bets = get_event_bets(events) 
    x = 0
    while x < 50:
        print("Starting main loop")
        start_time = measure_time()
        if x % 6 == 0 and x != 0:
            print("Updating events and event_bets...")
            events = get_events(leagues) 
            event_bets = get_event_bets(events) 
            print("Updated events")

        bets = get_bets(event_bets)
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
