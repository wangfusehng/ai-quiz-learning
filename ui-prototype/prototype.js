function setupInput(root) {
  const ta = root.querySelector("[data-material]");
  const count = root.querySelector("[data-count]");
  const alert = root.querySelector("[data-alert]");
  const form = root.querySelector("[data-input-form]");
  if (!ta || !form) return;
  const paint = () => {
    count.textContent = `${ta.value.trim().length} / 建议≥200`;
  };
  ta.addEventListener("input", paint);
  paint();
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const n = ta.value.trim().length;
    if (n < 200) {
      alert.classList.add("is-on");
      alert.focus();
      return;
    }
    alert.classList.remove("is-on");
  });
}

function setupQuiz(root) {
  const opts = [...root.querySelectorAll("[data-opt]")];
  const submit = root.querySelector("[data-submit]");
  const after = root.querySelector("[data-after]");
  if (!opts.length || !submit) return;
  opts.forEach((btn) => {
    btn.addEventListener("click", () => {
      opts.forEach((o) => o.classList.remove("is-on"));
      btn.classList.add("is-on");
      submit.disabled = false;
    });
  });
  submit.addEventListener("click", () => {
    const chosen = opts.find((o) => o.classList.contains("is-on"));
    if (!chosen) return;
    opts.forEach((o) => {
      o.classList.remove("is-on");
      if (o.dataset.opt === "wrong") o.classList.add("is-wrong");
      else if (o.dataset.opt === "right") o.classList.add("is-right");
      else o.classList.add("is-fade");
    });
    after.hidden = false;
    submit.textContent = "下一题";
    submit.disabled = false;
    const okBar = root.querySelector("[data-okbar]");
    if (okBar) {
      const right = chosen.dataset.opt === "right";
      okBar.textContent = right ? "答对了！" : "这题没答对";
      okBar.classList.toggle("is-miss", !right);
    }
  });
}

function setupScreens(root) {
  const chips = [...root.querySelectorAll("[data-show]")];
  const screens = [...root.querySelectorAll("[data-screen]")];
  if (!chips.length) return;
  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chips.forEach((c) => c.classList.remove("is-on"));
      chip.classList.add("is-on");
      screens.forEach((s) => s.classList.toggle("is-on", s.dataset.screen === chip.dataset.show));
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-phone-input]").forEach(setupInput);
  document.querySelectorAll("[data-phone-quiz]").forEach(setupQuiz);
  document.querySelectorAll("[data-switcher]").forEach(setupScreens);
});
