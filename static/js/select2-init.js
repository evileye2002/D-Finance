$("select ").select2({
  theme: "bootstrap-5",
  dropdownParent: $("form.with-select2"),
  language: {
    noResults: function (params) {
      return "Không có kết quả";
    },
  },
});
