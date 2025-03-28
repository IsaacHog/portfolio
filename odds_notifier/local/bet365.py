import os
import sys
grandparent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, grandparent_dir)
# Above is ugly but it is what it is

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import traceback
from utils.measure_time import measure_time
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import Driver
from config import *
import json

driver = Driver(headless=True, uc=True, user_data_dir=CHROME_USER_DATA_DIR)

wait_0_2 = WebDriverWait(driver, WAIT_TIMES['short'])
wait_1 = WebDriverWait(driver, WAIT_TIMES['medium'])
wait_3 = WebDriverWait(driver, WAIT_TIMES['long'])
wait_5 = WebDriverWait(driver, WAIT_TIMES['extra_long'])
new_tab_wait = WebDriverWait(driver, NEW_TAB_WAIT)

def throw_error(attempted_action="", error=""):
    WKS_ERROR.append_row([datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), attempted_action, error], table_range="A1:E1")

# driver manager functions
def close_current_tab():
    driver.execute_script("window.close();")
    time.sleep(CLOSE_TAB_WAIT)
    driver.switch_to.window(driver.window_handles[0])

def enter_main_page():
    driver.execute_script(f"""setTimeout(() => window.open('{BET365_URL}','_blank'), 100)""")
    driver.service.stop()
    driver.reconnect()
    driver.switch_to.window(driver.window_handles[1])
    print(f"Entered {BET365_URL}")

def accept_cookies():
    try:
        wait_3.until(EC.element_to_be_clickable((By.XPATH, COOKIE_ACCEPT_XPATH))).click()
        print("Clicked accept cookies")
    except:
        driver.switch_to.window(driver.window_handles[0]) # Ugly fix
        try:
            wait_3.until(EC.element_to_be_clickable((By.XPATH, COOKIE_ACCEPT_XPATH))).click()
        except:
            print("No cookies to accept")

def handle_league_tabs(bet365_leagues):
    print("Handleing league tabs...")
    try:
        open_leagues = wait_1.until(EC.presence_of_all_elements_located((By.XPATH, OPEN_LEAGUE_XPATH)))
    except:
        try:
            driver.switch_to.window(driver.window_handles[0]) # Ugly fix
            open_leagues = wait_1.until(EC.presence_of_all_elements_located((By.XPATH, OPEN_LEAGUE_XPATH)))
        except:
            return False
        
    for open_league in open_leagues:
        open_league.click()
        print("Closed league tab")
        time.sleep(LEAGUE_CLICK_WAIT)

    league_elements = wait_5.until(EC.presence_of_all_elements_located((By.XPATH, LEAGUE_TEXT_XPATH)))
    for league in league_elements:
        for interesting_league in bet365_leagues:
            if league.text == interesting_league:
                league.click()
                print("Openend league tab")
                time.sleep(LEAGUE_CLICK_WAIT)
    print("Finished handleing league tabs")
    return True

# bet collection functions
def get_leagues():
    bet365_leagues = []
    for league in LEAGUES:
        if league.bet365_name is not None:
            bet365_leagues.append(league.bet365_name)
    print(f"Got {len(bet365_leagues)} bet365_leagues")
    return bet365_leagues

def collect_team_names():
    try:
        team_names = [element.text for element in wait_3.until(EC.presence_of_all_elements_located((By.XPATH, TEAM_NAMES_XPATH)))]
    except:
        return "missing team_names"
    
    match_names = []
    i = 0
    while (i + 2 <= len(team_names)):
        match_names.append(team_names[i] + " - " + team_names[i+1]) 
        i += 2
    
    def convert_match_name(match_names):
        for i, match_name in enumerate(match_names):
            for team in BET365_TEAM_NAMES_TO_CONVERT:
                if team['bet365_name'] in match_name:
                    match_names[i] = match_names[i].replace(team['bet365_name'], team['convert_to_name'])
        return match_names
    
    match_names = convert_match_name(match_names)
    print("Collected match names")
    return match_names

def enter_specials_page(match_info):
    js_code = f"setTimeout(() => window.open('{match_info['url']}','_blank'), 200);"
    driver.execute_script(js_code)
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[1])

def get_match_infos(match_names):
    print("Gathering match infos")
    start_time = measure_time()
    match_infos = []
    for i in range(len(match_names)):
        matches = wait_5.until(EC.presence_of_all_elements_located((By.XPATH, MATCH_TIME_XPATH)))
        match_times = [element.text for element in matches]
        matches[i].click() # ugly but fuck XPATHS :D
        if '/I0' or '/I1' not in driver.current_url:
            url = driver.current_url + "I9"
        else:
            url = driver.current_url.replace("I0", "I9").replace("I1", "I9")
        
        hour, minute = map(int, match_times[i].split(":"))

        match_datetime = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        formatted_match_datetime = match_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

        match_infos.append({"url": url, "match_name": match_names[i], "starts": formatted_match_datetime})
        driver.back()
    
    close_current_tab()
    print("Gathered match infos")
    measure_time(start_time)
    return match_infos

def collect_bets(match_info):
    match_name = match_info['match_name']
    print(f"Collecting bets for {match_name}...")
    start_time = measure_time()
    bet_arr = {
        'match_name': match_name,
        'lines': {
            'total': [],
            'home': [],
            'away': []
        }
    }

    driver.save_screenshot("error.png")
    try:
        markets = wait_3.until(EC.presence_of_all_elements_located((By.XPATH, MARKETS_XPATH)))
    except:
        close_current_tab()
        enter_specials_page(match_info)
        try:
            markets = wait_1.until(EC.presence_of_all_elements_located((By.XPATH, MARKETS_XPATH)))
        except:
            print(f"failed to find markets in {match_name}, match probably started.")
            close_current_tab()
            return "failed to find markets"
    
    for market in markets:
        text = market.text
        if "Skott i matchen" in market.text:
            text = text.split('\n')
            bet_arr['lines']["total"].append({"line": f"O{text[2].replace(' ', '')}", "odds": text[4]})
            bet_arr['lines']["total"].append({"line": f"U{text[2].replace(' ', '')}", "odds": text[6]})
        elif "Lag - Skott" in market.text and "Lag - Skott på mål" not in market.text:
            text = text.split('\n')
            bet_arr['lines']["home"].append({"line": f"{text[3].replace('Över ', 'O')}", "odds": text[4]})
            bet_arr['lines']["home"].append({"line": f"{text[5].replace('Under ', 'U')}", "odds": text[6]})
            bet_arr['lines']['away'].append({"line": f"{text[8].replace('Över ', 'O')}", "odds": text[9]})
            bet_arr['lines']['away'].append({"line": f"{text[10].replace('Under ', 'U')}", "odds": text[11]})

    print(f"Collected bets for {match_name}")
    measure_time(start_time)
    close_current_tab()
    if bet_arr['lines'] == {'total': [],'home': [],'away': [] }:
        print(f"No shots markets found in {match_name}")
        return ""
    
    return json.dumps(bet_arr)

def re_get_match_infos(bet365_leagues):
    print("Getting match_infos again...")
    enter_main_page()
    
    is_league_tabs_handeled = handle_league_tabs(bet365_leagues=bet365_leagues)
    if not is_league_tabs_handeled:
        return "no league tabs found"
    
    match_names = collect_team_names()
    if match_names == "missing team_names":
        return "missing team_names"
    return get_match_infos(match_names)

def add_bets_to_wks365_shots(bet_data_to_append):
    rows_to_append = [[bet] for bet in bet_data_to_append]
    WKS_365SHOTS.append_rows(rows_to_append, value_input_option='USER_ENTERED', table_range="A1:D1")
    print("bet_data spreaded")
    return []

# Main bot loop
def bot_loop(is_first_run, bet365_leagues):
    def wait_for_league_tabs_to_be_found():
        is_league_tabs_handeled = False
        attempts = 0
        while not is_league_tabs_handeled:
            attempts += 1
            if attempts % 12 == 0:
                throw_error("handle_no_league_tabs", "Failed to handle league tabs after 12 attempts")

            if WKS_STATUS.cell(2,2).value != "TRUE":
                close_current_tab()
                return "status = false"
            print("No league tabs found, sleeping for 300 seconds...")
            time.sleep(300)
            is_league_tabs_handeled = handle_league_tabs(bet365_leagues=bet365_leagues)
    
    print("Starting main loop")
    start_time = measure_time()
    get_match_infos_again = True

    if is_first_run:
        enter_main_page()
        accept_cookies()
        is_league_tabs_handeled = handle_league_tabs(bet365_leagues=bet365_leagues)
        if not is_league_tabs_handeled:
            status = wait_for_league_tabs_to_be_found()
            if status == "status = false":
                return
        
        match_names = collect_team_names()
        if match_names == "missing team_names":
            match_infos = "missing team_names"
            while match_infos == "missing team_names":
                print("No interesting matches within 3h, sleeping for 120 seconds...")
                close_current_tab()
                time.sleep(120)
                match_infos = re_get_match_infos(bet365_leagues)
        match_infos = get_match_infos(match_names)
        
        get_match_infos_again = False

    if get_match_infos_again:
        match_infos = re_get_match_infos(bet365_leagues)
        if match_infos == "no league tabs found":
            status = wait_for_league_tabs_to_be_found()
            if status == "status = false":
                return
            match_infos = re_get_match_infos(bet365_leagues) 

    bet_data_to_append = []
    get_match_infos_again = False
    for i, match_info in enumerate(match_infos):
        if (datetime.strptime(match_info['starts'], '%Y-%m-%dT%H:%M:%SZ') > datetime.now() + timedelta(minutes=65)):
            if i + 1 == len(match_infos) and len(bet_data_to_append) > 0:
                bet_data_to_append = add_bets_to_wks365_shots(bet_data_to_append)
            continue
        enter_specials_page(match_info)
        bet_arr = collect_bets(match_info)

        if bet_arr == "failed to find markets":
            get_match_infos_again = True
            print("---- get_match_infos_again = true  ----")
            continue

        bet_data_to_append.append(bet_arr)
        print("collect_bets done")
    
        if (i + 1) % 4 == 0 or i + 1 == len(match_infos): # reduce request to gspread and apps scripts
            bet_data_to_append = add_bets_to_wks365_shots(bet_data_to_append)
    
    if bet_data_to_append != []:
        bet_data_to_append = add_bets_to_wks365_shots(bet_data_to_append)
    
    measure_time(start_time)  
    print("Finished main loop, sleeping for 40 seconds...") 
    time.sleep(40)




# Instance to run
print("---------------shots_365 Script initiated--------------------")
try:
    is_first_run = True
    for x in range (0, MAIN_LOOP_ITERATIONS):
        if WKS_STATUS.cell(2,2).value != "TRUE":
            print("statusSakoShots is false, sleeping for 300 seconds...")
            time.sleep(300)
            continue

        bet365_leagues = get_leagues()
        bot_loop(is_first_run, bet365_leagues)
        is_first_run = False
except Exception:
    driver.save_screenshot("error.png")
    throw_error("Last try except", traceback.format_exc())

print("Quitting driver")
driver.quit()

