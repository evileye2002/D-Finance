$(document).ready(function () {
  $("#id_category").change(function () {
    var value = $(this).children("option:selected").text();
    var lender_borrower_label = $("label[for='id_lender_borrower']");
    var div_id_loan_end = $("#div_id_loan_end");

    if (value == "Đi vay" || value == "Trả nợ")
      lender_borrower_label.text("Người cho vay");
    else lender_borrower_label.text("Người vay");

    if (value == "Thu nợ" || value == "Trả nợ") {
      div_id_loan_end.hide();
    } else {
      div_id_loan_end.show();
    }
  });
});
