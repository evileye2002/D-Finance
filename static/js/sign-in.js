// function addInputEvent() {
//   let inputs = null;

//   setInterval(() => {
//     if (inputs == null) {
//       inputs = document.querySelectorAll("#signInForm input.form-control");

//       Array.from(inputs).forEach((input) => {
//         input.addEventListener("input", () => {
//           if (input.classList.contains("is-invalid")) {
//             input.classList.remove("is-invalid");
//           }
//         });

//         input.addEventListener("change", () => {
//           if (input.value === "") {
//             input.classList.add("is-invalid");
//           }
//         });
//       });
//     }
//   }, 100);
// }

function addInputEvent() {
  inputs = $("#signInForm input.form-control");

  Array.from(inputs).forEach((input) => {
    input.addEventListener("input", () => {
      if (input.classList.contains("is-invalid")) {
        input.classList.remove("is-invalid");
      }
    });

    input.addEventListener("change", () => {
      if (input.value === "") {
        input.classList.add("is-invalid");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  addInputEvent();
});
