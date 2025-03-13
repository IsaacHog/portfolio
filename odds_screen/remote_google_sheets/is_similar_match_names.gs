const levenshteinDistance = (s, t) => {
  if (!s.length) return t.length;
  if (!t.length) return s.length;
  const arr = [];
  for (let i = 0; i <= t.length; i++) {
    arr[i] = [i];
    for (let j = 1; j <= s.length; j++) {
      arr[i][j] =
        i === 0
          ? j
          : Math.min(
              arr[i - 1][j] + 1,
              arr[i][j - 1] + 1,
              arr[i - 1][j - 1] + (s[j - 1] === t[i - 1] ? 0 : 1)
            );
    }
  }
  let distance = arr[t.length][s.length]
  //console.log(`Distance: ${distance}\n${s}\n${t}\n`)
  return distance
};

function IsSimilarMatchNames(matchName1, matchName2) {
  // special case :(
  if (matchName1.includes("Man C") && matchName2.includes("Manchester City")) {
    matchName1 = "Manchesterccccciiiittttyyyyyyy"
    matchName2 = "Manchesterccccciiiittttyyyyyyy"
  }
  else if (matchName1.includes("Man U") && matchName2.includes("Manchester United")) {
    matchName1 = "Manchesteruuunnnniiittteeeeeeddd"
    matchName2 = "Manchesteruuunnnniiittteeeeeeddd"
  }

  // special case :(
  if (matchName1.includes("Man C") && matchName2.includes("Manchester City")) {
    matchName1 = "Manchesterccccciiiittttyyyyyyy"
    matchName2 = "Manchesterccccciiiittttyyyyyyy"
  }
  else if (matchName1.includes("Man U") && matchName2.includes("Manchester United")) {
    matchName1 = "Manchesteruuunnnniiittteeeeeeddd"
    matchName2 = "Manchesteruuunnnniiittteeeeeeddd"
  }

  // special case :(
  if (matchName1.includes("PSG")) {
    matchName1 = "Paris SG"
  }

  const removeDiacritics = (str) => {
    return str.normalize('NFD').replace(/[\u0300-\u036f]/g, "");
  };

  let replaceWords = ["City", "Town", "United", "Club"]
  let thresholdMatchNameWords = matchName1.split(" ");
  let cardWords = matchName2.split(" ");
  thresholdMatchNameWords = thresholdMatchNameWords.filter(word => !replaceWords.includes(word));
  cardWords = cardWords.filter(word => !replaceWords.includes(word));

  thresholdMatchNameWords = thresholdMatchNameWords
    .filter(word => !replaceWords.includes(word))
    .map(removeDiacritics);

  cardWords = cardWords
      .filter(word => !replaceWords.includes(word))
      .map(removeDiacritics);

  let isFound = false
  let breakLoop = false
  let distanceTreshold = 11

  for (let j = 0; j < thresholdMatchNameWords.length; j++) {
    for (let k = 0; k < cardWords.length; k++) {
      if (thresholdMatchNameWords[j].toLowerCase() === cardWords[k].toLowerCase()) {
        if (thresholdMatchNameWords[j].length < 3) { // Prevent matches on "KK" or "BK" and so on
          breakLoop = true
          break
        }

        breakLoop = false
        
        if (levenshteinDistance(thresholdMatchNameWords.join(" "), cardWords.join(" ")) > distanceTreshold) { // Extra check
          //console.log(`levenshteinDistance failed\n${matchName1}\n${matchName2}`)
          breakLoop = true
          break
        }
        
        isFound = true 
        break
      }
      if (breakLoop) {
        break
      }
    }
    if (isFound) { 
      return true  
    }
  }
  return false
}
