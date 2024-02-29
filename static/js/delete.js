function DeleteWalletDialog(e) {
  var result = confirm(
    "Xác nhận xóa Ví này?\nThao tác này sẽ xóa TẤT CẢ bản ghi liên quan."
  );
  if (!result) {
    e.preventDefault();
  }
}

function DeleteRecordDialog(e) {
  var result = confirm("Xác nhận xóa Bản Ghi này?");
  if (!result) {
    e.preventDefault();
  }
}

function DeleteDirectoryDialog(e) {
  var result = confirm(
    "Xác nhận xóa Người này?\nThao tác này sẽ xóa TẤT CẢ bản ghi liên quan."
  );
  if (!result) {
    e.preventDefault();
  }
}

function DeleteCategoryDialog(e) {
  var result = confirm(
    "Xác nhận xóa Danh Mục này?\nThao tác này sẽ xóa TẤT CẢ bản ghi liên quan."
  );
  if (!result) {
    e.preventDefault();
  }
}
