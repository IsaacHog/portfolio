let token = None // removed from repo

function getMe() {
  let response = UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/getMe");
  console.log(response.getContentText());
}

function setWebhook() { // Körs endast genom apps script
  let webAppUrl = None // removed from repo
  let response = UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/setWebhook?url=" + webAppUrl);
  console.log(response.getContentText());
}

function compareTextWithBotCommands(text, chat_id) {
  if (text.substring(0,9) === "/register") {
    sendText(chat_id, "New chat_id registered, ID: " + chat_id);
    sendText(isaac_id, "New chat_id registered, ID: " + chat_id);
  }

  else if (text.startsWith("start bot")) {
    let botStatus = SpreadsheetApp.getActive().getSheetByName("BotStatus").getRange(2, 2).getValue();
    if (botStatus) {
      sendText(chat_id, "Bot is already active, will update fair odds again within 5 min.");
      SpreadsheetApp.getActive().getSheetByName("BotStatus").getRange(2, 3).setValue(true)
    }
    else {
      SpreadsheetApp.getActive().getSheetByName("BotStatus").getRange(2, 2).setValue(true)
      SpreadsheetApp.getActive().getSheetByName("BotStatus").getRange(2, 3).setValue(true)
      sendText(chat_id, "Bot set to active");
    }
  }

  else if (text.startsWith("stop bot")) {
    let botStatus = SpreadsheetApp.getActive().getSheetByName("BotStatus").getRange(2, 2).getValue();
    if (botStatus) {
      SpreadsheetApp.getActive().getSheetByName("BotStatus").getRange(2, 2).setValue(false)
      SpreadsheetApp.getActive().getSheetByName("BotStatus").getRange(2, 3).setValue(false)
      sendText(chat_id, "Bot set to inactive");
    }
    else {
      sendText(chat_id, "Bot is already inactive");
    }
  }
  
  else {
    return
  }
}







function sendText(chat_id, text, alertObject={textType: "message"}) {
  let data = {
    method: "post",
    payload: {
      method: "sendMessage",
      chat_id: String(chat_id),
      text: text,
      parse_mode: "HTML"
    }
  };
  UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/', data);
}

function doPost(e) {
  var contents = JSON.parse(e.postData.contents);
  try{ var chat_id = contents.message.chat.id; var text = contents.message.text.toLowerCase(); } // contents object differs between channels and chats
  catch { var chat_id = contents.channel_post.chat.id; var text = contents.channel_post.text.toLowerCase()}
  
  compareTextWithBotCommands(text, chat_id);
}