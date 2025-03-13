let token = None # removed as the repo is public

function getMe() {
  let response = UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/getMe");
  console.log(response.getContentText());
}

function setWebhook() { // Körs endast genom apps script
  let webAppUrl = None # removed as the repo is public
  let response = UrlFetchApp.fetch("https://api.telegram.org/bot" + token + "/setWebhook?url=" + webAppUrl);
  console.log(response.getContentText());
}

let isaac_id = None # removed as the repo is public
let sako_id = None # removed as the repo is public

function sendText(chat_id, text) {
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
  try{ var chat_id = contents.message.chat.id; var text = contents.message.text; } // contents object differs between channels and chats
  catch { var chat_id = contents.channel_post.chat.id; var text = contents.channel_post.text} 
}