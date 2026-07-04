function doPost(e) {
  try {
    const data = JSON.parse(e.postData.contents);
    const ss = data.sheet_id
      ? SpreadsheetApp.openById(data.sheet_id)
      : SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName(data.sheet);
    if (!sheet) return respond({error: 'Sheet not found'});
    sheet.appendRow(data.row);
    return respond({success: true});
  } catch(err) {
    return respond({error: err.message});
  }
}

function doGet(e) {
  const action = e && e.parameter && e.parameter.action;
  const sheetId = e && e.parameter && e.parameter.sheet_id;

  if (action === 'getPlans') {
    // الباقات (Plans) دايماً في الشيت العام المشترك، بغض النظر عن sheet_id
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = ss.getSheetByName('Plans');
    if (!sheet) return respond({plans: []});
    const rows = sheet.getDataRange().getValues();
    const headers = rows[0];
    const plans = [];
    for (var i = 1; i < rows.length; i++) {
      if (!rows[i][0]) continue;
      var plan = {};
      for (var j = 0; j < headers.length; j++) {
        plan[headers[j]] = rows[i][j];
      }
      plans.push(plan);
    }
    return respond({plans: plans});
  }

  return respond({status: 'ok'});
}

function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
