window.addEventListener("scroll", () => {
  isUserAtBottom =
    window.innerHeight + window.scrollY >= document.body.offsetHeight;
  if (isUserAtBottom) {
    var searchParams = new URLSearchParams(window.location.search);
    var currentPage = searchParams.get("page");
    var nextPage = parseInt(currentPage) + 1;
    searchParams.set("page", nextPage);
    var newURL = window.location.pathname + "?" + searchParams.toString();

    window.location.href = newURL;
  }
});
