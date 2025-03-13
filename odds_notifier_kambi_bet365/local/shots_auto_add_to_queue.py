
from datetime import datetime, timedelta
from config import WKS_QUEUE, SA, MAIN_LOOP_ITERATIONS, WKS_STATUS, WKS_ERROR
import time
import json
import traceback

todays_date = datetime.today()

sh_shots = None
wks_shots = None

def throw_error(attempted_action="", error=""):
    WKS_ERROR.append_row([datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), attempted_action, error], table_range="A1:E1")

def find_sheet():
    global sh_shots
    global wks_shots
    for i in range(4):  # Try for 0, 1, 2 and 3 days ago
        date_to_try = todays_date - timedelta(days=i)
        try:
            sh_shots = SA.open(f"Shots {date_to_try.day}/{date_to_try.month}")
            wks_shots = sh_shots.worksheet("Fair odds basic")
            print(f"Found sheet {sh_shots.title}")
            return
        except:
            continue
    WKS_ERROR.append_row([datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "Could not open sheet for the past 3 days", ""], table_range="A1:E1")
    return "fail"

def clear_queue():
    queue = WKS_QUEUE.get_all_values()
    if len(queue) > 1:
        cell_range = WKS_QUEUE.range(f'A2:{chr(64+WKS_QUEUE.col_count)}{len(queue)}')
        for cell in cell_range:
            cell.value = ''
        WKS_QUEUE.update_cells(cell_range)

def get_fair_odds():
    print("Getting fair odds...")
    fair_odds_table = wks_shots.get_all_values()
    fair_odds = []
    for row in fair_odds_table[-80:]:
        entry = { 
            'lines': {
                'total': [],
                'home': [],
                'away': []
            }
        }
        for i, cell in enumerate(row):
            if cell == '':
                continue

            if i == 0:
                try:
                    if datetime.strptime(cell, "%Y/%m/%d").day != todays_date.day:
                        break
                except:
                    if datetime.strptime(cell, "%Y-%m-%d").day != todays_date.day:
                        break

            key = fair_odds_table[1][i]

            if i == 2:
                match_name = cell + " - " + row[i+1]
                continue
            if i == 3:
                continue
            
            if "pred_" in key:
                continue
            elif "prob_" in key:
                continue
            
            if i > 4:
                cell = float(cell.replace(',', '.'))
                if cell < 1.3 or cell > 2.3:
                    continue
                
                if "over" in key.lower():
                    line = key.lower().split("over")
                    over_under = "O"
                elif "under" in key.lower():
                    line = key.lower().split("under")
                    over_under = "U"
                  
                if "home" in key:   
                    key = "home"
                elif "away" in key:   
                    key = "away"
                else:
                    key = "total"

                entry['lines'][key].append({
                    'line': f"{over_under}{line[1]}",
                    'fair_odds': cell
                    })
            else:
                entry[key] = cell

        if entry == { 'lines': {'total': [],'home': [],'away': [] }}:
            continue
        entry['match_name'] = match_name
        fair_odds.append(entry)
    print(f"Got {len(fair_odds)} fair odds")
    return fair_odds

def add_bets_to_queue(fair_odds):
    fair_odds_to_append = []
    for fair_bet in fair_odds:
        fair_odds_to_append.append(["", "", json.dumps(fair_bet)])
    WKS_QUEUE.append_rows(fair_odds_to_append, value_input_option='USER_ENTERED', table_range="A1:D1")

def bot_loop():
    for i in range (0, MAIN_LOOP_ITERATIONS):
        if WKS_STATUS.cell(2,3).value != "TRUE":
            print("statusAutoAddToQueue is false, sleeping for 300 seconds...")
            time.sleep(300)
            continue

        status = find_sheet()
        if status == "fail":
            print("Could not find sheet, sleeping for 500 seconds...")
            time.sleep(500)
            continue

        clear_queue()

        fair_odds = get_fair_odds()
        if len(fair_odds) < 1:
            print("No new fair odds")
            time.sleep(10)
            return
        
        add_bets_to_queue(fair_odds)
        print(f"Added {len(fair_odds)} bets to queue")
        WKS_STATUS.update_cell(2, 3, "FALSE")
        WKS_QUEUE.update_cell(2, 4, "updated")

print("---------------shots_auto_add_to_queue Script initiated--------------------")
try:
    bot_loop()
except Exception:
    throw_error("Last try except", traceback.format_exc())
