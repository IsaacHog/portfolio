# Portfolio - Odds Notifier

A project for scraping odds (specifically team and total shots in the top 5 soccer leagues) from 2 dfferent sportsbooks. Bet365 uses **Selenium** to scrape data, Kambi uses **HTTP Requests**. Finalized February 2024.

Video demo:
[https://youtube.com/watch?v=OrSmxxhBWPM](https://www.youtube.com/watch?v=OrSmxxhBWPM)

## File Structure

The project is divided into two main folders:
- **Local**
- **Remote**

When used live, Google Sheets acts as a remote database, handling Telegram alerts.

## Goal of the project

Alert favorable bets through a Telegram bot for specific bets above a threshold (`min_odds`) across kambi and bet365 sportsbooks.

**Note:** `min_odds` is determined by an external model, which is not included in this repository.

## Challenges

**Anti-Bot**  
Bet365 features one of the most advanced anti-bot protections in the sports betting market, continuously upgraded to stay effective. Any bot-like behavior using the Chrome DevTools Protocol is swiftly identified and blocked.  
The success of this script hinges on avoiding detection by disabling Selenium during Bet365's bot checks. While this might seem like a straightforward solution, it introduces challenges such as reduced script performance. Additionally, this approach is only effective on specific sections of their sportsbook, highlighting the sophistication of their anti-bot measures.  

In contrast, Kambi employs minimal anti-bot protection, making it significantly less restrictive.

**Combining Two Data Formats into One for Comparison**  
The two sportsbooks utilize entirely different data structures, and even team names vary significantly. This challenge is overcome by generalizing the data structure and standardizing team names to achieve a unified format for comparison.


## Libraries and Tools Used

- `request`
- `gspread`
- `telegram bot API`
- `Google Apps Scripts`
- `selenium`
- `bash`
