import os
import gspread

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'shots_alert', 'service_account.json')

# Bet365 Configuration
BET365_URL = 'https://www.bet365.com/#/AC/B1/C1/D1002/G10166/J99/I1/Q1/F^3/'
COOKIE_ACCEPT_XPATH = "//div[@class='ccm-CookieConsentPopup_Accept ']"
OPEN_LEAGUE_XPATH = ".//div[contains(@class, 'suf-CompetitionMarketGroup_Open')]"
LEAGUE_TEXT_XPATH = ".//div[@class='suf-CompetitionMarketGroupButton_Text ']"
TEAM_NAMES_XPATH = ".//div[@class='src-ParticipantFixtureDetailsHigher_TeamNames']/div"
MATCH_TIME_XPATH = "//div[@class='src-ParticipantFixtureDetailsHigher_BookCloses ']"
MARKETS_XPATH = "//div[@class='gl-MarketGroupPod gl-MarketGroup ']"

# Spreadsheet Configuration
SA = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)

SH = SA.open("IsaacScraper")
WKS_365SHOTS = SH.worksheet("Bet365Shots")
WKS_KAMBISHOTS = SH.worksheet("KambiShots")
WKS_QUEUE = SH.worksheet("ShotsQueue")
WKS_STATUS = SH.worksheet("BotStatus")

SH_AUTO_BETTOR = SA.open("kambi auto_bettor")
WKS_ERROR = SH_AUTO_BETTOR.worksheet("Error")

# Selenium Configuration
CHROME_USER_DATA_DIR = "C:/Users/Isaac/Documents/GitHub/Selenium/UserData"

# Timing Configuration
WAIT_TIMES = {
    'short': 0.2,
    'medium': 1,
    'long': 3,
    'extra_long': 5
}
NEW_TAB_WAIT = 3
CLOSE_TAB_WAIT = 0.3
LEAGUE_CLICK_WAIT = 0.3
MAIN_LOOP_ITERATIONS = 50

# League Configuration
class League:
    def __init__(self, bet365_name, kambi_name):
        self.bet365_name = bet365_name
        self.kambi_name = kambi_name

LEAGUES = [
    League("England - Premier League", "england/premier_league"),
    League("Frankrike - Ligue 1", "france/ligue_1"),
    League("Spanien - La Liga", "spain/la_liga"),
    League("Italien - Serie A",  "italy/serie_a"),
    League("Tyskland - Bundesliga I",  "germany/bundesliga")
]

# Fairodds / kambi teamname differences
KAMBI_TEAM_NAMES_TO_CONVERT = [
    {
    'betoffer_name': "Sevilla",
    'convert_to_name': "FC Sevilla"
    },
    {
    'betoffer_name': "FC Barcelona",
    'convert_to_name': "Barcelona"
    },
    {
    'betoffer_name': "Parma",
    'convert_to_name': "Parma Calcio"
    },
    {
    'betoffer_name': "VfL Bochum",
    'convert_to_name': "Bochum"
    },
    {
    'betoffer_name': "Holstein Kiel",
    'convert_to_name': "Kiel"
    },
    {
    'betoffer_name': "RB Leipzig",
    'convert_to_name': "Leipzig"
    },
    {
    'betoffer_name': "FC St. Pauli",
    'convert_to_name': "St. Pauli"
    },
    {
    'betoffer_name': "Marseille",
    'convert_to_name': "Ol. Marseille"
    },
    {
    'betoffer_name': "AC Milan",
    'convert_to_name': "Milan"
    },
    {
    'betoffer_name': "VfL Bochum",
    'convert_to_name': "Bochum"
    },
    {
    'betoffer_name': "Borussia Dortmund",
    'convert_to_name': "Dortmund"
    },
    {
    'betoffer_name': "1. FC Union Berlin",
    'convert_to_name': "Berlin"
    },
    {
    'betoffer_name': "Borussia Monchengladbach",
    'convert_to_name': "B. Monchengladbach"
    },
    {
    'betoffer_name': "SC Freiburg",
    'convert_to_name': "Freiburg"
    },
    {
    'betoffer_name': "VfB Stuttgart",
    'convert_to_name': "Stuttgart"
    },
    {
    'betoffer_name': "VfL Wolfsburg",
    'convert_to_name': "Wolfsburg"
    },
    {
    'betoffer_name': "Bayer Leverkusen",
    'convert_to_name': "Leverkusen"
    },
    {
    'betoffer_name': "Bayern Munchen",
    'convert_to_name': "B. Munich"
    },
    {
    'betoffer_name': "Paris SG",
    'convert_to_name': "PSG"
    },
    {
    'betoffer_name': "Leicester City",
    'convert_to_name': "Leicester"
    },
    {
    'betoffer_name': "Ipswich Town",
    'convert_to_name': "Ipswich"
    },
    {
    'betoffer_name': "Nottingham Forest",
    'convert_to_name': "Nottingham"
    },
    {
    'betoffer_name': "Manchester City",
    'convert_to_name': "Man City"
    },
    {
    'betoffer_name': "Newcastle United",
    'convert_to_name': "Newcastle"
    },
    {
    'betoffer_name': "Crystal Palace",
    'convert_to_name': "C Palace"
    },
    {
    'betoffer_name': "Athletic Bilbao",
    'convert_to_name': "Bilbao"
    },
    {
    'betoffer_name': "UD Las Palmas",
    'convert_to_name': "Las Palmas"
    },
    {
    'betoffer_name': "Real Betis",
    'convert_to_name': "Betis"
    },
    {
    'betoffer_name': "Werder Bremen",
    'convert_to_name': "Bremen"
    },
    {
    'betoffer_name': "TSG Hoffenheim",
    'convert_to_name': "Hoffenheim"
    },
    {
    'betoffer_name': "Eintracht Frankfurt",
    'convert_to_name': "Frankfurt"
    },
    {
    'betoffer_name': "Holstein Kiel",
    'convert_to_name': "Kiel"
    },
    {
    'betoffer_name': "1. FC Heidenheim",
    'convert_to_name': "Heidenheim"
    },
    {
    'betoffer_name': "Mainz 05",
    'convert_to_name': "1. FSV Mainz 05"
    },
    {
    'betoffer_name': "Manchester United",
    'convert_to_name': "Man Utd"
    },
    {
    'betoffer_name': "Rayo Vallecano",
    'convert_to_name': "Vallecano"
    },
    {
    'betoffer_name': "Atletico Madrid",
    'convert_to_name': "Atletico"
    },
    {
    'betoffer_name': "FC Augsburg",
    'convert_to_name': "Augsburg"
    },
    {
    'betoffer_name': "Borussia Mönchengladbach",
    'convert_to_name': "B. Monchengladbach"
    },
    {
    'betoffer_name': "Brest",
    'convert_to_name': "Brestois"
    }
]



BET365_TEAM_NAMES_TO_CONVERT = [
    # PREMIER LEAGUE
    {
    'bet365_name': "Nottm Forest",
    'convert_to_name': "Nottingham"
    },
    {
    'bet365_name': "Crystal Palace",
    'convert_to_name': "C Palace"
    },
    {
    'bet365_name': "Wolverhampton",
    'convert_to_name': "Wolves"
    },
    # La Liga
    {
    'bet365_name': "CD Alaves",
    'convert_to_name': "Alaves"
    },
    {
    'bet365_name': "Atletico Madrid",
    'convert_to_name': "Atletico"
    },
    {
    'bet365_name': "Athletic Bilbao",
    'convert_to_name': "Bilbao"
    },
    {
    'bet365_name': "Sevilla",
    'convert_to_name': "FC Sevilla"
    },
    {
    'bet365_name': "Real Betis",
    'convert_to_name': "Betis"
    },
    {
    'bet365_name': "Rayo Vallecano",
    'convert_to_name': "Vallecano"
    },
    # Serie A
    {
    'bet365_name': "Verona",
    'convert_to_name': "Hellas Verona"
    },
    {
    'bet365_name': "Parma",
    'convert_to_name': "Parma Calcio"
    },
    # Bundesliga
    {
    'bet365_name': "Eintracht Frankfurt",
    'convert_to_name': "Frankfurt"
    },
    {
    'bet365_name': "Bayer Leverkusen",
    'convert_to_name': "Leverkusen"
    },
    {
    'bet365_name': "TSG Hoffenheim",
    'convert_to_name': "Hoffenheim"
    },
    {
    'bet365_name': "RB Leipzig",
    'convert_to_name': "Leipzig"
    },
    {
    'bet365_name': "Borussia Dortmund",
    'convert_to_name': "Dortmund"
    },
    {
    'bet365_name': "Union Berlin",
    'convert_to_name': "Berlin"
    },
    {
    'bet365_name': "Borussia M'gladbach",
    'convert_to_name': "B. Monchengladbach"
    },
    {
    'bet365_name': "St Pauli",
    'convert_to_name': "St. Pauli"
    },
    {
    'bet365_name': "SC Freiburg",
    'convert_to_name': "Freiburg"
    },
    {
    'bet365_name': "VfB Stuttgart",
    'convert_to_name': "Stuttgart"
    },
    {
    'bet365_name': "Bayern München",
    'convert_to_name': "B. Munich"
    },
    {
    'bet365_name': "Werder Bremen",
    'convert_to_name': "Bremen"
    },
    {
    'bet365_name': "Holstein Kiel",
    'convert_to_name': "Kiel"
    },
    {
    'bet365_name': "Mainz",
    'convert_to_name': "1. FSV Mainz 05"
    },
    # Ligue 1
    {
    'bet365_name': "Brest",
    'convert_to_name': "Brestois"
    },
    {
    'bet365_name': "Marseille",
    'convert_to_name': "Ol. Marseille"
    },
    {
    'bet365_name': "St Etienne",
    'convert_to_name': "Saint-Etienne"
    },
    {
    'bet365_name': "Monaco",
    'convert_to_name': "AS Monaco"
    }
]