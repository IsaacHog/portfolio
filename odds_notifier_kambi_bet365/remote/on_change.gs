function onChange(e) {
  var sheet = e.source.getActiveSheet();
  var editedSheet = sheet.getName()

  if (editedSheet === "ShotsQueue") {
    let shotsQueueSheet = SpreadsheetApp.getActive().getSheetByName("ShotsQueue")
    if (shotsQueueSheet.getRange(2,4).getValue() != "updated"){ return }

    var data = shotsQueueSheet.getDataRange().getValues();
    var nonEmptyRows = 0;
    for (var i = 0; i < data.length; i++) {
      if (data[i].some(cell => cell !== "")) {
        nonEmptyRows++;
      }
    }

    sendText(-4553153544, `Shots fair odds updated. Queue length: ${nonEmptyRows - 1}`)
    shotsQueueSheet.getRange(2,4).setValue("")
  }
  else if (editedSheet === "Bet365Shots") {
    console.log("run Bet365Shots()")
    Bet365Shots()
  }
  else if (editedSheet === "KambiShots") {
    console.log("run KambiShots()")
    KambiShots()
  }

}
