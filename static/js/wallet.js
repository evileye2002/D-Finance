function DeleteDialog(e) {
  var result = confirm(
    "Xác nhận xóa Ví này?\nThao tác này sẽ xóa TẤT CẢ bản ghi liên quan."
  );
  if (!result) {
    e.preventDefault();
  }
}
