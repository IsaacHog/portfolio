# Portfolio - Odds Notifier

A project for scraping odds (specifically team and total shots in the top 5 soccer leagues) from 2 dfferent sportsbooks. Finalized February 2024.

## File Structure

The project is divided into two main folders:
- **Local**
- **Remote**

When used live, Google Sheets acts as a remote database, handling Telegram alerts.

## Issue to Solve

The goal is to:
Alert favorable bets through a Telegram bot for specific bets above a threshold (`min_odds`) across kambi and bet365 sportsbooks.

**Note:** `min_odds` is determined by an external model, which is not included in this repository.

## Libraries Used

The following libraries and tools are utilized in this project:
- `request`
- `gspread`
- `telegram bot API`
- `Google Apps Scripts`
- `selenium`
- `bash`
