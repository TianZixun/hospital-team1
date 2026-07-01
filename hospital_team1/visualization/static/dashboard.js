document.querySelectorAll(".button-grid button").forEach((button) => {
  button.addEventListener("click", () => {
    button.classList.add("pressed");
    window.setTimeout(() => button.classList.remove("pressed"), 180);
  });
});
