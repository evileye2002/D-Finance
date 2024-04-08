function toggleVisibility(e) {
  var parentDiv = $(e).closest(".text-center");

  var icon = parentDiv.find("i");
  var fakeTotal = parentDiv.find("#fakeTotal");
  var walletTotal = parentDiv.find("#walletTotal");

  icon.toggleClass("fa-eye").toggleClass("fa-eye-slash");
  fakeTotal.toggleClass("visually-hidden");
  walletTotal.toggleClass("visually-hidden");
}
