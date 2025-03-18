function loadJsonFromSheet(sheet, column, startRow) {
  let data = sheet.getDataRange().getValues();
  let unpackedData = []
  for (var i = startRow; i < data.length; i++) {
    try {
      unpackedData.push(JSON.parse(data[i][column]))
    } catch (e) {
      Logger.log("Error parsing row " + (i + 1) + ": " + e.message);
    }
  }
  if (sheet.getName() != "ShotsQueue") {
    sheet.clear()
  }
  return unpackedData
}

function compareOdds(queueData, bookieBetData, queueSheet, bookieColumn) {
    let results = [];
    
    queueData.forEach((match, index) => {
        console.log(`Processing match: ${match.match_name}`);
        let result = { lines: { total: [], home: [], away: [] }, match_name: match.match_name };
        
        let bookieLines = bookieBetData.find(bet => bet.match_name === match.match_name)?.lines || {};
        if (Object.keys(bookieLines).length > 0) {
            console.log(`Found matching bookie data for: ${match.match_name}`);
        }
        
        function findOdds(bookieLines, category, line) {
            let market = bookieLines[category] || [];
            for (let bet of market) {
                  if (bet.line === line) {
                      console.log(`Matched line: ${line} in category: ${category} with odds: ${bet.odds}`);
                      return parseFloat(bet.odds);
                }
            }
            return null;
        }
        
        let isFound = false;
        ["total", "home", "away"].forEach(category => {
          match.lines[category].forEach(bet => {
            let fairOverLine = bet.line.startsWith("O") ? bet.line : null;
            let fairOverOdds = bet.line.startsWith("O") ? bet.fair_odds : null;
            let fairUnderLine = bet.line.startsWith("U") ? bet.line : null;
            let fairUnderOdds = bet.line.startsWith("U") ? bet.fair_odds : null;
            
            let overOdds = findOdds(bookieLines, category, fairOverLine)
            let underOdds = findOdds(bookieLines, category, fairUnderLine)
            if (overOdds) {
              result.lines[category].push({line: fairOverLine, odds: overOdds, ev: (overOdds / fairOverOdds).toFixed(3)}) 
              isFound = true
            }
            if (underOdds) {
              result.lines[category].push({line: fairUnderLine, odds: underOdds, ev: (underOdds / fairUnderOdds).toFixed(3)}) 
              isFound = true
            }
          });
        });
        
        if (isFound) {
          queueSheet.getRange(index+2, bookieColumn).setValue(JSON.stringify(result))
          results.push(result);
        }
        
    });
    
    return results;
}

function ShotsSheet(bookie, output_column) {
  const bookieShotsSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(`${bookie}Shots`);
  const bookieBetData = loadJsonFromSheet(bookieShotsSheet, 0, 0);
  if (bookieBetData == []) {
    console.log(`${bookie}BetData == []`)  
    return
  }

  const shotsQueueSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('ShotsQueue');
  const queueDataFairOdds = loadJsonFromSheet(shotsQueueSheet, 3, 1);

  let output = compareOdds(queueDataFairOdds, bookieBetData, shotsQueueSheet, output_column);
  console.log(output);
}

function AlertShots() {
  console.log("Looking for shots bets to alert...")
  const shotsQueueSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('ShotsQueue');

  function loadBookieOddsJson(data) {
    let unpackedData = [];
    
    for (let i = 1; i < data.length; i++) {
      let bet365JsonString = data[i][0] ? JSON.parse(data[i][0]) : null;
      let kambiJsonString = data[i][1] ? JSON.parse(data[i][1]) : null;
      let dsobJsonString = data[i][2] ? JSON.parse(data[i][2]) : null;
      
      if (data[i][5] == "x") {
        continue
      }
      

      if (bet365JsonString) {
        var matchName = bet365JsonString.match_name
      }
      else if (kambiJsonString) {
        var matchName = kambiJsonString.match_name
      }
      else {
        continue
      }
      unpackedData.push({ matchName: matchName, bet365: bet365JsonString, kambi: kambiJsonString, dsob: dsobJsonString, queueIndex: i });
    }

    return unpackedData;
  }

  const data = shotsQueueSheet.getDataRange().getValues();
  const unpackedData = loadBookieOddsJson(data);

  if (unpackedData.length === 0) {
    console.log("unpackedData is empty");
    return;
  }
  
  function findBetsToAlert() {
    var betsToAlert = [];
    unpackedData.forEach(data => {
      let matchName = data.matchName;
      let queueIndex = data.queueIndex
      let bet365Lines = data.bet365 ? data.bet365.lines : null;
      let kambiLines = data.kambi ? data.kambi.lines : null;
      let dsobLines = data.dsob ? data.dsob.lines : null;

      // Helper function to find or create a bet alert entry
      function findOrCreateBetAlert(matchName) {
        let existingBet = betsToAlert.find(bet => bet.matchName === matchName);
        if (!existingBet) {
          existingBet = { matchName: matchName, bet365: { total: [], home: [], away: [] }, kambi: { total: [], home: [], away: [] }, dsob: { total: [], home: [], away: [] } };
          betsToAlert.push(existingBet);
        }
        return existingBet;
      }

      // Process bet365Lines
      if (bet365Lines) {
        for (let market in bet365Lines) {
          let markets = bet365Lines[market];
          for (let i = 0; i < markets.length; i++) {
            if (markets[i].ev > 1.1) {
              let betAlert = findOrCreateBetAlert(matchName);
              betAlert.bet365[market].push( { line: markets[i].line, odds: markets[i].odds, ev: markets[i].ev } );
              shotsQueueSheet.getRange(queueIndex+1, 6).setValue("x")
            }
          }
        }
      }

      // Process kambiLines
      if (kambiLines) {
        for (let market in kambiLines) {
          let markets = kambiLines[market];
          for (let i = 0; i < markets.length; i++) {
            if (markets[i].ev > 1.1) {
              let betAlert = findOrCreateBetAlert(matchName);
              betAlert.kambi[market].push( { line: markets[i].line, odds: markets[i].odds, ev: markets[i].ev } );
              shotsQueueSheet.getRange(queueIndex+1, 6).setValue("x")
            }
          }
        }
      }

      // Process dsobLines
      if (dsobLines) {
        for (let market in dsobLines) {
          let markets = dsobLines[market];
          for (let i = 0; i < markets.length; i++) {
            if (markets[i].ev > 1.1) {
              let betAlert = findOrCreateBetAlert(matchName);
              betAlert.dsob[market].push( { line: markets[i].line, odds: markets[i].odds, ev: markets[i].ev } );
              shotsQueueSheet.getRange(queueIndex+1, 6).setValue("x")
            }
          }
        }
      }
    });

    return betsToAlert
  }
  
  var betsToAlert = findBetsToAlert()

  function sendAlerts(betsToAlert) {
    betsToAlert.forEach(bet => {
      let message = `${bet.matchName}\n\n`;

      ["total", "home", "away"].forEach(market => {
        if (bet.bet365[market].length === 0 && bet.kambi[market].length === 0 && bet.dsob[market].length === 0){
          return
        } 

        message += `${market} shots:\n`;
        if (bet.bet365[market].length > 0) {
          message += `-- Bet365:\n${bet.bet365[market].map(betDetail => `${betDetail.line} @${betDetail.odds} EV: ${betDetail.ev}\n`).join('')}`;
        }
        if (bet.kambi[market].length > 0) {
          message += `-- Kambi:\n${bet.kambi[market].map(betDetail => `${betDetail.line} @${betDetail.odds} EV: ${betDetail.ev}\n`).join('')}`;
        }
        if (bet.dsob[market].length > 0) {
          message += `-- Greek:\n${bet.dsob[market].map(betDetail => `${betDetail.line} @${betDetail.odds} EV: ${betDetail.ev}\n`).join('')}`;
        }

        message += `\n`;
        sendText(null, message);
      });
    });
  }
  sendAlerts(betsToAlert)
}
