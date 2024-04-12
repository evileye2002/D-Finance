$("select ").select2({
  theme: "bootstrap-5",
  dropdownParent: $("form"),
  language: {
    noResults: function (params) {
      return "Không có kết quả";
    },
  },
});
