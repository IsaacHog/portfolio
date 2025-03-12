function onChange(e) {
  var sheet = e.source.getActiveSheet();
  var editedSheet = sheet.getName()
  
  if (editedSheet === "KambiCards") {
    console.log("run Cards(KambiCards, Cards_list_kambi)")
    Cards("KambiCards", "Cards_list_kambi")
  }
  else if (editedSheet === "BetssonCards") {
    console.log("run Cards(BetssonCards, Cards_list_betsson)")
    Cards("BetssonCards", "Cards_list_betsson")
  }
  else if (editedSheet === "CoolbetCards") {
    console.log("run Cards(CoolbetCards, Cards_list_coolbet)")
    Cards("CoolbetCards", "Cards_list_coolbet")
  }
  else if (editedSheet === "ComeonCards") {
    console.log("run Cards(ComeonCards, Cards_list_comeon)")
    Cards("ComeonCards", "Cards_list_comeon")
  }
  else if (editedSheet === "BetiniaCards") {
    console.log("run Cards(BetiniaCards, Cards_list_betinia)")
    Cards("BetiniaCards", "Cards_list_betinia")
  }
  else if (editedSheet === "BetwayCards") {
    console.log("run Cards(BetwayCards, Cards_list_betway)")
    Cards("BetwayCards", "Cards_list_betway")
  }
}
