function GetBookieCardData(sheet) { // same as GetBookieBasketballLiveData
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) {
    return null;
  }
 const matchNames = sheet.getRange(1, 1, lastRow).getValues().flat();
  const lines = sheet.getRange(1, 2, lastRow).getValues().flat();
  const odds = sheet.getRange(1, 3, lastRow).getValues().flat();

  const data = [];
  for (let i = 0; i < lastRow; i++) {
    if (matchNames[i] !== "") {
      const matchData = {
        matchName: matchNames[i],
        line: lines[i],
        odds: odds[i]
      };
      data.push(matchData);
    }
  }
  console.log("Gathered bookie card data, data.length = " + data.length);
  return data;
}

function GetCardsCachedData(sheet) { // Same as GetBasketballLiveCachedData
  const lastRow = sheet.getLastRow();
  const matchNames = sheet.getRange(2, 1, lastRow).getValues().flat();
  const lines = sheet.getRange(2, 2, lastRow).getValues().flat();
  const softOdds = sheet.getRange(2, 3, lastRow).getValues().flat();

  const data = [];
  for (let i = 0; i < lastRow; i++) {
    const matchData = {
      matchName: matchNames[i],
      line: lines[i],
      softOdds: softOdds[i]
    };
    data.push(matchData);
  }
  data.pop()
  return data;
}

function testCards() {
  Cards("KambiCards", "Cards_list_kambi")
}

function Cards(sheet, list_sheet) {
  const softSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheet);

  cardsListSheet = SpreadsheetApp.getActive().getSheetByName(list_sheet);
  lastRow = cardsListSheet.getLastRow();

  const softDataArr = GetBookieCardData(softSheet);
  if (softDataArr == null) {
    console.log("softDataArr == null")  
    return
  }
  softSheet.clear();

  var lastMatchName = ''
  var lastIndex = 0
  var chachedDataArrStartIndex = 0
  const chachedDataArr = GetCardsCachedData(cardsListSheet);
  var newBetsToAppend = []
  for (let x = 0; x < softDataArr.length; x++) {
    if (softDataArr[x].matchName === "") { // Weird bug, probably fixed but keeping as fail-safe
      console.log("softDataArr[x].matchName === ''")
      continue
    }

    if (softDataArr[x].matchName === lastMatchName && lastIndex >= 32) {
      console.log("softDataArr[x].matchName === lastMatchName && lastIndex >= 32")
      chachedDataArrStartIndex = lastIndex - 30
    }
    else {
      chachedDataArrStartIndex = 0
    }

    var isFoundInChachedSheet = false
    for (let i = chachedDataArrStartIndex; i < chachedDataArr.length; i++) {
      if (softDataArr[x].matchName.startsWith("END")) {
        continue
      }
      if (softDataArr[x].matchName === chachedDataArr[i].matchName) {
        if (softDataArr[x].line === chachedDataArr[i].line) {
          console.log(`Found ${softDataArr[x].matchName} in chachedData (row ${i + 2})`)
          isFoundInChachedSheet = true
          cardsListSheet.getRange(i + 2, 4).setValue(new Date())
          if (softDataArr[x].odds !== chachedDataArr[i].softOdds) {
            cardsListSheet.getRange(i + 2, 3).setValue(softDataArr[x].odds)
            console.log("New odds found, updated softOdds")
          }
          lastMatchName = softDataArr[x].matchName
          lastIndex = i
          break
        }
      }
    }
    if (!isFoundInChachedSheet) {
      if (!softDataArr[x].matchName.startsWith("END")) {
        console.log(`Failed to find ${softDataArr[x].matchName} in cachedData`)
        newBetsToAppend.push([softDataArr[x].matchName, softDataArr[x].line, softDataArr[x].odds, new Date()])
      }
    }
  }
  if (newBetsToAppend.length > 0) {
    cardsListSheet.getRange(lastRow + 1,1,newBetsToAppend.length, newBetsToAppend[0].length).setValues(newBetsToAppend);
    console.log(`Appended new bets to Cards sheet\n ${newBetsToAppend}`)
  }
  else {
    console.log("No new bets to append")
  }
}
