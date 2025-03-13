function TrackCardThresholds(bookie, sheetColumn) {
  console.log(`Tracking card thresholds for ${bookie}..."`)
  cardThresholdSheet = SpreadsheetApp.getActive().getSheetByName('ThresholdsCards')
  var thresholdLastRow = cardThresholdSheet.getLastRow();
  let thresholdMatchNames = cardThresholdSheet.getRange(2, 1, thresholdLastRow).getValues().flat();
  let thresholdOdds = cardThresholdSheet.getRange(2, 2, thresholdLastRow).getValues().flat();
  let thresholdAlerted = cardThresholdSheet.getRange(2, sheetColumn, thresholdLastRow).getValues().flat();

  cardsSheet = SpreadsheetApp.getActive().getSheetByName(`Cards_list_${bookie.toLowerCase()}`);
  var cardsLastRow = cardsSheet.getLastRow();
  let cardsMatchNames = cardsSheet.getRange(2, 1, cardsLastRow - 1).getValues().flat();
  let cardsLines = cardsSheet.getRange(2, 2, cardsLastRow - 1).getValues().flat();
  let cardsBookieOdds = cardsSheet.getRange(2, 3, cardsLastRow - 1).getValues().flat();
  let cardsTimes = cardsSheet.getRange(2, 4, cardsLastRow - 1).getValues().flat();

  cardThresholdObjectsSheet = SpreadsheetApp.getActive().getSheetByName('ThresholdsCardsObjects')

  for (let i = 0; i < thresholdMatchNames.length; i++) {
    if (thresholdMatchNames[i] === "") {
      continue
    }
    for (let x = 0; x < cardsMatchNames.length; x++) { 
      const last_updated = new Date() - new Date(cardsTimes[x])
      if ( last_updated > 10 * 60 * 1000 ) {// more than 10 minutes ago
        continue
      }

      let thresholdMatchName = thresholdMatchNames[i].replace(",", ".").split(" - ")
      let thresholdLine = thresholdMatchName[1]
      thresholdMatchName = thresholdMatchName[0].replace(" v ", " - ")
      try {
        thresholdLine = thresholdLine.split("(")
      }
      catch {
        thresholdLine = thresholdLine
      }
      thresholdLine = thresholdLine[0].replace(" kort", "")
      
      if (!IsSimilarMatchNames(thresholdMatchName, cardsMatchNames[x])) {
        continue
      }

      if (thresholdLine !== cardsLines[x]) { // same odds
        continue
      }

      if (cardThresholdSheet.getRange(i+2, sheetColumn + 1).getValue() !== cardsBookieOdds[x]) { // New odds
        cardThresholdSheet.getRange(i+2, sheetColumn + 1).setValue(cardsBookieOdds[x])
        if (bookie === "Kambi") {
          cardThresholdObjectsSheet.getRange(i+2, 3).setValue(new Date())
          cardThresholdSheet.getRange(i+2, sheetColumn + 1).setBackground('yellow');
        }
        else {
          cardThresholdSheet.getRange(i+2, sheetColumn + 1).setBackground('gray');
        }
        
      }

      if (cardsBookieOdds[x] < thresholdOdds[i] - 0.01) { // < min odds
        if (thresholdAlerted[i] === "x") {
          cardThresholdSheet.getRange(i+2, sheetColumn).setValue("")
        }
        continue
      }
      
      if (thresholdAlerted[i] === "x") { // already alerted
        continue
      }
      
      cardThresholdSheet.getRange(i+2, sheetColumn).setValue("x") // above min not alerted
      const message = `${bookie}\n${thresholdMatchName} - ${thresholdLine}\n@${cardsBookieOdds[x]}`;
      sendText(isaac_id, message)
      sendText(sako_id, message)
      console.log(`sendText for ${thresholdMatchNames[i]}`)
      break
    }
  }
}