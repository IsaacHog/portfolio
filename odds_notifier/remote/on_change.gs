function onChange(e) {
	var sheet = e.source.getActiveSheet();
	var editedSheet = sheet.getName()
	
	// lazy
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
  
	const sheetMapping = {
	  Bet365Shots: { name: "Bet365", param: 1 },
	  KambiShots: { name: "Kambi", param: 2 },
	  DsobShots: { name: "Dsob", param: 3 }
	};

	if (editedSheet in sheetMapping) {
	  const { name, param } = sheetMapping[editedSheet];
	  console.log(`run ShotsSheet("${name}", ${param})`);
	  ShotsSheet(name, param);
	}
}
