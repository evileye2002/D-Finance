$(document).ready(function () {
  $("#id_category").change(function () {
    var selectedText = $(this).children("option:selected").text();

    if (selectedText == "Thu nợ" || selectedText == "Trả nợ")
      div_id_loan_end.hide();
    else div_id_loan_end.show();
  });

  var selectedText = $("#id_category").children("option:selected").text();
  var currentUrl = window.location.href;
  var lender_borrower_label = $("label[for='id_lender_borrower']");
  var div_id_loan_end = $("#div_id_loan_end");

  if (currentUrl.indexOf("borrow") !== -1)
    lender_borrower_label.text("Người cho vay");
  else lender_borrower_label.text("Người vay");

  if (selectedText == "Thu nợ" || selectedText == "Trả nợ")
    div_id_loan_end.hide();
  else div_id_loan_end.show();
});
