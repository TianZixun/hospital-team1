document.querySelectorAll(".button-stack .control-button").forEach((button) => {
  button.addEventListener("click", () => {
    button.classList.add("pressed");
    window.setTimeout(() => button.classList.remove("pressed"), 180);
  });
});
