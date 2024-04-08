function toggleVisibility(event) {
  if (!e) var e = window.event;
  e.cancelBubble = true;
  if (e.stopPropagation) e.stopPropagation();

  var parentDiv = $(event).closest("#money");

  var icon = parentDiv.find("i");
  var fakeTotal = parentDiv.find("#fakeTotal");
  var walletTotal = parentDiv.find("#walletTotal");

  icon.toggleClass("fa-eye").toggleClass("fa-eye-slash");
  fakeTotal.toggleClass("visually-hidden");
  walletTotal.toggleClass("visually-hidden");
}

function gotoChange(e) {
  var parentDiv = $(e).closest("#wallet");
  var walletID = parentDiv.find("#walletID");

  location.href = `wallet/${walletID.text()}/change`;
}
