// function addInputEvent() {
//   let inputs = null;

//   setInterval(() => {
//     if (inputs == null) {
//       inputs = document.querySelectorAll("#signUpForm input.form-control");

//       Array.from(inputs).forEach((input) => {
//         if (!input.classList.contains("is-invalid") && input.value != "") {
//           input.classList.add("is-valid");
//         }

//         input.addEventListener("input", () => {
//           if (input.classList.contains("is-invalid")) {
//             input.classList.remove("is-invalid");
//             input.classList.add("is-valid");
//           }
//         });

//         input.addEventListener("change", () => {
//           if (input.value === "") {
//             input.classList.add("is-invalid");
//             input.classList.remove("is-valid");
//           }
//         });
//       });
//     }
//   }, 100);
// }

function addInputEvent() {
  inputs = document.querySelectorAll("#signUpForm input.form-control");

  Array.from(inputs).forEach((input) => {
    if (!input.classList.contains("is-invalid") && input.value != "") {
      input.classList.add("is-valid");
    }

    input.addEventListener("input", () => {
      if (input.classList.contains("is-invalid")) {
        input.classList.remove("is-invalid");
        input.classList.add("is-valid");
      }
    });

    input.addEventListener("change", () => {
      if (input.value === "") {
        input.classList.add("is-invalid");
        input.classList.remove("is-valid");
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  addInputEvent();
});
