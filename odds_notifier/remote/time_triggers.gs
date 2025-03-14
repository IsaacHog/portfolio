function every_10_min_trigger() {
  // Shots bot auto off
  let currentDate = new Date();
  let botStatusSheet = SpreadsheetApp.getActive().getSheetByName('BotStatus');
  let statusSakoShots = botStatusSheet.getRange(2, 2).getValue();

  let endTime = parseTimeToToday(botStatusSheet.getRange(2, 1).getValue());

  if (currentDate > endTime) {
    if (statusSakoShots) { 
      botStatusSheet.getRange(2, 2).setValue(false);
      botStatusSheet.getRange(2, 3).setValue(false);
      sendText(-4553153544, "---- Turned off shots bot at auto off time ----")
      console.log("Set botStatuses to false")
    }
  }
  else {
    console.log("No botStatus change")
  }

  function parseTimeToToday(timeStr) {
    let parts = timeStr.split(":"); // Expecting "HH:MM"
    let today = new Date();
    today.setHours(parseInt(parts[0]), parseInt(parts[1]), 0, 0); // Set to HH:MM today
    return today;
  }

  if (statusSakoShots) {
    AlertShots()
  }
}
