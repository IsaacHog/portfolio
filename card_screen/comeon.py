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
import gspread
from utils.measure_time import measure_time
from selenium.webdriver.support.wait import WebDriverWait
from seleniumbase import Driver
from leagues import comeon_leagues as league_urls

if __name__ == "__main__":
    sa = gspread.service_account(filename='service_account.json')
    sh = sa.open("CardBot")
    wks = sh.worksheet("ComeonCards")
    
    sh_error = sa.open("ErrorLog")
    wks_error = sh_error.worksheet("Error")
    wks_error_log = sh_error.worksheet("ErrorLog")
    
    driver = Driver(headless=True,uc=True)
    
    wait_0_2 = WebDriverWait(driver, 0.2)
    wait_1 = WebDriverWait(driver, 1)
    wait_3 = WebDriverWait(driver, 3)
    wait_5 = WebDriverWait(driver, 5)
    new_tab_wait = WebDriverWait(driver, 3)
    close_tab_wait = 0.3

    def accept_cookies():
        try:
            wait_1.until(EC.element_to_be_clickable((By.XPATH, "//button[.='Godkänn']"))).click()
            print("Clicked accept cookies")
        except: 
            print("No cookies to accept")

    def format_match_names(team_names):
        filtered_team_names = [item for item in team_names if len(item) > 2] # Remove live scores
        match_names = []
        i = 0
        while (i + 2 <= len(filtered_team_names)):
            match_names.append(filtered_team_names[i] + " - " + filtered_team_names[i+1]) 
            i += 2
        return match_names
    
    def contains_number(string):
        return any(char.isdigit() for char in string)

    def get_match_infos():
        match_date_categories = [element.text for element in wait_3.until(EC.presence_of_all_elements_located((By.XPATH, ".//h5[contains(@class, 'typography__LabelBold-sc-13m3q03-6 sportsbook-game-card-list-header__Title-sc-gd3v2e-4 gwKHZe bwAtFG')]")))]
        match_infos = []
        for match_date_category in match_date_categories:
            if "Idag" in match_date_category:
                match_urls = [element.get_attribute("href") for element in wait_1.until(EC.presence_of_all_elements_located((By.XPATH, f".//div[contains(@class, 'sportsbook-column-layout__ColumnLayoutContainer-sc-')]/div[1]/ul[1]/div//a[contains(@class, 'sportsbook-event-scoreboard__ScoreboardContainer-sc-')]")))]
                team_names = [element.text for element in wait_1.until(EC.presence_of_all_elements_located((By.XPATH, f".//div[contains(@class, 'sportsbook-column-layout__ColumnLayoutContainer-sc-')]/div[1]/ul[1]/div//a[contains(@class, 'sportsbook-event-scoreboard__ScoreboardContainer-sc-')]//p")))]
                match_names = format_match_names(team_names)
                for match_url, match_name in zip(match_urls, match_names):
                    if contains_number(match_name):
                        continue
                    match_infos.append({
                        'match_name': match_name,
                        'url': match_url
                    })
        return match_infos

    def collect_bets(match_infos):
        bets = []
        for match_info in match_infos:
            print(f"Collecting bets for {match_info['match_name']}")
            driver.get(match_info['url'])
            try:
                bookings_href = wait_3.until(EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'market-group=12')]"))).get_attribute("href")
                driver.get(bookings_href)
            except:
                print(f"Failed to find bookings tab in {match_info['match_name']}")
                continue
            time.sleep(0.3)

            markets = [element.text for element in wait_3.until(EC.presence_of_all_elements_located((By.XPATH, f".//small[contains(@class, 'sportsbook-market-base__StyledCaption-sc-')]")))]
            bets.append({
                    'match_name': match_info['match_name'],
                    'url': match_info['url'],
                    'lines': []
            })
            try:
                for x, market in enumerate(markets):
                    if "Booking 1x2" in market or "Kort 1x2" in market:
                        lines_odds = [element.text for element in wait_1.until(EC.presence_of_all_elements_located((By.XPATH, f".//div[contains(@class, 'sportsbook-column-layout__ColumnLayoutContainer-sc-')]/div[1]//div[contains(@class, 'sportsbook-market-base__MarketWrapper-sc-')][{x+1}]//small")))]
                        bets[-1]['lines'].append({
                            'line': "Hemma -0.5",
                            'odds': lines_odds[2]
                        })
                        bets[-1]['lines'].append({
                            'line': "Borta -0.5",
                            'odds': lines_odds[6]
                        })
                    elif "Total bookings" in market or "Totalt antal kort" in market:
                        lines_odds = [element.text for element in wait_1.until(EC.presence_of_all_elements_located((By.XPATH, f".//div[contains(@class, 'sportsbook-column-layout__ColumnLayoutContainer-sc-')]/div[1]//div[contains(@class, 'sportsbook-market-base__MarketWrapper-sc-')][{x+1}]//small")))]
                        lines_odds.pop(0) # New layout makes the line name a small element too so need to remove it
                        lines_arr = lines_odds[::2]
                        odds_arr = lines_odds[1::2]

                        for odds, line in zip(odds_arr, lines_arr):
                            bets[-1]['lines'].append({
                                'line': line.replace("över ", "Ö").replace("under ", "U"),
                                'odds': odds
                            })
            except:
                print(f"Failed to collect bets for {match_info['match_name']}")
                continue
        
        return bets

    def spread_bets(event_bets):
        print("Spreading bets...")
        start_time = measure_time()
        bet_arr = []
        for event_bet in event_bets:
            for line in event_bet['lines']:
                if float(line["odds"]) > 3 or float(line["odds"]) < 1.4:
                    continue
                bet_arr.append([ event_bet['match_name'], line['line'], line["odds"] ])
                    
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

    def ScrapeLoop():
        print("Getting match_infos...")
        match_infos = []
        for league_url in league_urls:
            driver.get(league_url)
            accept_cookies()
            match_infos.extend(get_match_infos())
        print("Got match_infos")

        x = 0
        while x < 50:
            print("Starting main loop")
            start_time = measure_time()

            bets = collect_bets(match_infos)
            spread_bets(bets)

            print("Finished main loop")
            elapsed_time = measure_time(start_time)
            
            if elapsed_time < 30:
                print("Sleeping for 20 seconds...")
                time.sleep(20)
            x += 1

    
    
    
# Instance to run
    print("---------------cards_comeon Script initiated--------------------")
    try: 
        ScrapeLoop()
    except Exception:
        driver.save_screenshot("error.png")
        error = traceback.format_exc()
        wks_error.append_row([error], table_range="A1:E1")
        wks_error_log.append_row([error], table_range="A1:E1")

    print("Quitting driver")
    driver.quit()