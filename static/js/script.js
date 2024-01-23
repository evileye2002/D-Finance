const formDialogBackdrop = $("#form-dialog-backdrop");
const formDialog = $("#form-dialog");
const formDialogBody = $("#form-dialog-body");

function closeDialog(e) {
  if (
    !formDialogBody.is(e.target) &&
    formDialogBody.has(e.target).length === 0
  ) {
    formDialogBackdrop.addClass("visually-hidden");
    formDialog.addClass("visually-hidden");
  }
}

function openDialog() {
  formDialogBackdrop.removeClass("visually-hidden");
  formDialog.removeClass("visually-hidden");
}

$(document).mouseup(closeDialog);
