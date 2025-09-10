let mode = 'view';
let currentIndex = 0;
let drinkConfigs = {};
let originalDrinkConfigs = {};
let originalProportions = {};
let pouring = false;
let pourAnimationFrame = null;
var systemConfig;
const DEFAULT_SIZE = 750;
const socket = io();

// Listen for pouring state
socket.on("pour_state", (data) => {
  const { active, drink, progress } = data;
  const pouringBanner = document.getElementById("pouring-banner");

  if (active) {
    pouringBanner.textContent = `Currently Pouring: ${drink}`;
    pouringBanner.style.display = "block";

    // disable all start buttons
    document.querySelectorAll(".startBtn").forEach(btn => {
      btn.disabled = true;
      btn.classList.add("disabled");
    });
    document.querySelectorAll(".stopBtn").forEach(btn => {
      btn.disabled = false; // allow stopping
    });

    // update progress
    const slide = document.getElementsByClassName("carousel-slide")[currentIndex];
    if (Object.values(drinkConfigs)[currentIndex].name === drink) {
      const fills = slide.querySelectorAll(".fill");
      fills.forEach(f => f.style.height = progress + "%");
    }
  } else {
    pouringBanner.style.display = "none";
    document.querySelectorAll(".startBtn").forEach(btn => {
      btn.disabled = false;
      btn.classList.remove("disabled");
    });
    document.querySelectorAll(".stopBtn").forEach(btn => {
      btn.disabled = true;
    });
  }
});


async function fetchConfigs() {
  try {
    const response = await fetch("/api/getconfigs");
    if (!response.ok) throw new Error("Network error");
    const data = await response.json();
    drinkConfigs = data;
  } catch (e) {
    console.error("Fetch error:", e);
  }
}

async function fetchSystemConfig() {
  try {
    const response = await fetch("/api/getsystemconfig");
    if (!response.ok) throw new Error("Network error");
    systemConfig = await response.json();
  } catch (e) {
    console.error("Fetch error:", e);
  }
}

async function initApp() {
  await fetchConfigs();
  await fetchSystemConfig();
  if (Object.keys(drinkConfigs).length > 0) {
    renderSlides();
    updateSlidePosition();
  } else {
    console.warn("No configurations found to display.");
  }
}

async function fetchOtp() {
  try {
    const response = await fetch("/api/otp");
    if (!response.ok) throw new Error("Failed to fetch OTP");
    const data = await response.json();
    document.getElementById("otpDisplay").textContent = data.otp || "N/A";
  } catch (err) {
    console.error("OTP fetch failed:", err);
    document.getElementById("otpDisplay").textContent = "Error";
  }
}

function generateNewId() {
  const keys = Object.keys(drinkConfigs).map(Number);
  const nextId = keys.length ? Math.max(...keys) + 1 : 1;
  return nextId.toString();
}

function renderSlides() {
  const keys = Object.keys(drinkConfigs);
  const carouselTrack = document.getElementById("carouselTrack");
  carouselTrack.innerHTML = '';

  keys.forEach((key, index) => {
    const drink = drinkConfigs[key];
    const slide = document.createElement("div");
    slide.className = "carousel-slide";

    const title = document.createElement("div");
    title.className = "drink-name";

    if (mode === 'edit' || mode === 'create') {
      const nameInput = document.createElement("input");
      nameInput.value = drink.name;
      nameInput.type = "text";
      nameInput.className = "drink-name-input";
      nameInput.addEventListener("focus", () => showKeyboard("full", nameInput));
      nameInput.addEventListener("input", (e) => drink.name = e.target.value);
      title.appendChild(nameInput);
    } else {
      title.textContent = drink.name;
    }

    slide.appendChild(title);

    const container = document.createElement("div");
    container.className = "cartridge-container";

    for (let j = 1; j <= 4; j++) {
      const wrapper = document.createElement("div");
      wrapper.className = "cartridge-wrapper";

      const cartridge = document.createElement("div");
      cartridge.className = "cartridge";

      const fill = document.createElement("div");
      fill.className = "fill";

      const ml = drink.proportions[j.toString()] || 0;
      const percent = (ml / DEFAULT_SIZE) * 100;
      fill.style.height = percent + "%";

      cartridge.appendChild(fill);
      wrapper.appendChild(cartridge);

      const label = document.createElement("div");
      label.className = "cartridge-label";
      label.textContent = "Cartridge " + j;
      wrapper.appendChild(label);

      let input = null;
      if (mode === 'edit' || mode === 'create') {
          input = document.createElement("input");
          input.type = "number";
          input.value = ml;
          input.className = "ml-input";
          input.addEventListener("focus", () => showKeyboard("numbers", input));
          input.addEventListener("input", (e) => {
              const newML = parseFloat(e.target.value) || 0;
              drink.proportions[j.toString()] = newML;
              fill.style.height = (newML / DEFAULT_SIZE) * 100 + "%";
          });
          wrapper.appendChild(input);

          // DRAG LOGIC
          fill.style.cursor = 'ns-resize';
          let startY, startHeight;

          function onPointerDown(e) {
            e.preventDefault();
            startY = e.clientY || e.touches?.[0]?.clientY;
            startHeight = parseFloat(fill.style.height) || 0;

            document.addEventListener('mousemove', onPointerMove);
            document.addEventListener('mouseup', onPointerUp);
            document.addEventListener('touchmove', onPointerMove, { passive: false });
            document.addEventListener('touchend', onPointerUp);
          }

          function onPointerMove(e) {
            e.preventDefault();
            const currentY = e.clientY || e.touches?.[0]?.clientY;
            const deltaY = startY - currentY;
            let newPercent = Math.min(100, Math.max(0, startHeight + deltaY / 2));
            fill.style.height = newPercent + "%";
            const newML = Math.round((newPercent / 100) * DEFAULT_SIZE);
            drink.proportions[j.toString()] = newML;
            if (input) input.value = newML;
          }

          function onPointerUp() {
            document.removeEventListener('mousemove', onPointerMove);
            document.removeEventListener('mouseup', onPointerUp);
            document.removeEventListener('touchmove', onPointerMove);
            document.removeEventListener('touchend', onPointerUp);
          }

          // ✅ Attach to cartridge, not fill
          cartridge.addEventListener('mousedown', onPointerDown);
          cartridge.addEventListener('touchstart', onPointerDown, { passive: false });

      } else {
          const mlLabel = document.createElement("div");
          mlLabel.className = "ml-label";
          mlLabel.textContent = ml + " mL";
          wrapper.appendChild(mlLabel);
    } 
    container.appendChild(wrapper);
  }


    slide.appendChild(container);

    const actions = document.createElement("div");
    actions.className = "slide-actions";

    if (mode === 'edit' || mode === 'create') {
      const saveBtn = document.createElement("button");
      saveBtn.textContent = "Save";
      saveBtn.type = "submit";
      saveBtn.onclick = (e) => {
        e.preventDefault();
        const configToSave = drinkConfigs[key];
        configToSave.configNo = key;
        if (mode === 'edit') {
          fetch("/api/editconfig", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(configToSave)
          }).then(_ => {
            mode = 'view';
            renderSlides();
            updateSlidePosition();
          });
        } else if (mode === "create") {
          fetch("/api/configcreate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(configToSave)
          }).then(_ => {
            mode = 'view';
            renderSlides();
            updateSlidePosition();
          })
        }
      };
      actions.appendChild(saveBtn);

      const cancelBtn = document.createElement("button");
      cancelBtn.textContent = "Cancel";
      saveBtn.type = "button";
      cancelBtn.onclick = () => {
        const originalConfig = originalDrinkConfigs[key];
        if (originalConfig) {
          drinkConfigs[key] = { ...originalConfig };
        }

        // Hide keyboard and clear input reference
        document.getElementById("keyboard").style.display = "none";
        currentInput = null;

        mode = 'view';
        renderSlides();
        updateSlidePosition();
      };

      actions.appendChild(cancelBtn);
    }

    if (mode === 'delete') {
      const deleteBtn = document.createElement("button");
      deleteBtn.textContent = "Delete";
      deleteBtn.type = "button";
      deleteBtn.onclick = () => {
        fetch("/api/configremove", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({"name":key})
          }).then(_ => {
            delete drinkConfigs[key];
            const newKeys = Object.keys(drinkConfigs);
            currentIndex = Math.min(currentIndex, newKeys.length - 1);
            mode = 'view';
            renderSlides();
            updateSlidePosition();
          })
      };
      actions.appendChild(deleteBtn);
    }

    if (mode === 'view') {
      const startBtn = document.createElement("button");
      startBtn.textContent = "Start";
      startBtn.type = "button";
      startBtn.className = "startBtn";
      startBtn.dataset.index = index;   // so we know which slide
      startBtn.onclick = async () => {
        try {
          await fetch("/api/start", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "configNo": key })
          });
          startPouring(drink);
        } catch (err) {
          console.error("Failed to start pouring:", err);
        }
      };

      const stopBtn = document.createElement("button");
      stopBtn.textContent = "Stop";
      stopBtn.type = "button";
      stopBtn.className = "stopBtn";
      stopBtn.dataset.index = index;
      stopBtn.onclick = async () => {
        try {
          await fetch("/api/stop", { method: "POST" });
          stopPouring();
        } catch (err) {
          console.error("Failed to stop pouring:", err);
        }
      };

      actions.appendChild(startBtn);
      actions.appendChild(stopBtn);
    }

    slide.appendChild(actions);
    carouselTrack.appendChild(slide);
  });
}

function updateSlidePosition() {
  const offset = -currentIndex * 100;
  document.getElementById("carouselTrack").style.transform = `translateX(${offset}%)`;
}

function setMode(newMode) {
  mode = newMode;

  if (mode === 'create') {
    const newId = generateNewId();
    creating = true;
    drinkConfigs[newId] = {
      name: "New Drink",
      proportions: { "1": 0, "2": 0, "3": 0, "4": 0 }
    };
    currentIndex = Object.keys(drinkConfigs).length - 1;
  }

  if (mode === 'edit') {
    originalDrinkConfigs = JSON.parse(JSON.stringify(drinkConfigs));
  }

  renderSlides();
  updateSlidePosition();
}

function startPouring(drink) {
  if (pouring) return;

  const slide = document.getElementsByClassName("carousel-slide")[currentIndex];
  const fills = slide.querySelectorAll(".fill");

  originalProportions = { ...drink.proportions };
  pouring = true;
  const startTime = performance.now();

  function animatePouring(timestamp) {
    const elapsed = (timestamp - startTime) / 1000;
    let allEmpty = true;

    fills.forEach((fill, index) => {
      const cartNum = (index + 1).toString();
      const originalML = originalProportions[cartNum] || 0;
      let flow_rate = parseFloat(systemConfig[`pump${cartNum}_flow_rate_l_s`]) * 1000
      const remainingML = Math.max(originalML - flow_rate * elapsed, 0);
      const percent = (remainingML / DEFAULT_SIZE) * 100;
      // nabl fix
      fill.style.height = percent - 1 + "%";
      if (remainingML > 0) allEmpty = false;
    });

    if (allEmpty) {
      pouring = false;
      // pour complete
      showGreenTick();
      resetBars(drink);
      return;
    }

    pourAnimationFrame = requestAnimationFrame(animatePouring);
  }

  pourAnimationFrame = requestAnimationFrame(animatePouring);
}



function stopPouring() {
  if (!pouring) return;
  cancelAnimationFrame(pourAnimationFrame);
  pouring = false;

  const drink = Object.values(drinkConfigs)[currentIndex];
  resetBars(drink);
}

function resetBars(drink) {
  const slide = document.getElementsByClassName("carousel-slide")[currentIndex];
  const fills = slide.querySelectorAll(".fill");

  fills.forEach((fill, index) => {
    const cartNum = (index + 1).toString();
    const ml = drink.proportions[cartNum] || 0;
    const percent = (ml / DEFAULT_SIZE) * 100;
    fill.style.height = percent + "%";
  });
}

function showGreenTick(message = 'Done!') {
  // Create popup container
  const popup = document.createElement('div');
  popup.className = 'tick-popup';
  popup.setAttribute('role', 'status');
  popup.setAttribute('aria-live', 'polite');

  // Card with icon + text
  popup.innerHTML = `
    <div class="tick-card">
      <svg class="tick-icon" viewBox="0 0 24 24" aria-hidden="true">
        <circle cx="12" cy="12" r="11" fill="rgba(255,255,255,0.18)"></circle>
        <path d="M20 6L9 17l-5-5" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>${message}</span>
    </div>
  `;

  // Remove on click or after 3s
  const remove = () => {
    if (!popup.isConnected) return;
    popup.addEventListener('animationend', () => popup.remove(), { once: true });
    // If fadeOut animation was already scheduled via CSS, just ensure removal at end
    popup.style.pointerEvents = 'none';
  };

  document.body.appendChild(popup);

  // Auto-remove at 3s (matches CSS fade timing)
  const t = setTimeout(() => remove(), 2000);

  // Optional: allow dismiss on click or Esc
  popup.addEventListener('click', () => {
    clearTimeout(t);
    remove();
  });
  document.addEventListener('keydown', function onKey(e) {
    if (e.key === 'Escape') {
      clearTimeout(t);
      remove();
      document.removeEventListener('keydown', onKey);
    }
  }, { once: true });
}

document.getElementById("nextBtn").addEventListener("click", () => {
  if (pouring || mode === "create" || mode === "edit") {
    return
  }
  const keys = Object.keys(drinkConfigs);
  currentIndex = (currentIndex + 1) % keys.length;
  updateSlidePosition();
});

document.getElementById("prevBtn").addEventListener("click", () => {
  if (pouring || mode === "create" || mode === "edit") {
    return
  }
  const keys = Object.keys(drinkConfigs);
  currentIndex = (currentIndex - 1 + keys.length) % keys.length;
  updateSlidePosition();
});

document.getElementById("refreshOtpBtn").addEventListener("click", fetchOtp);

// Touch/swipe navigation
let touchStartX = 0;
let touchEndX = 0;
const carouselContainer = document.getElementById("carouselContainer");

carouselContainer.addEventListener("touchstart", e => {
  touchStartX = e.changedTouches[0].screenX;
});

carouselContainer.addEventListener("touchend", e => {
  touchEndX = e.changedTouches[0].screenX;
  handleSwipe();
});

document.addEventListener("keydown", function(event) {
  const ctrl = event.ctrlKey;
  const alt = event.altKey;

  if (ctrl && alt) {
    switch (event.key) {
      case "s": // Start current
        document.querySelectorAll(".carousel-slide")[currentIndex]
          .querySelector(".startBtn")
          ?.click();
        break;
      case "x": // Stop current
        document.querySelectorAll(".carousel-slide")[currentIndex]
          .querySelector(".stopBtn")
          ?.click();
        break;
      case "ArrowLeft":
        document.getElementById("prevBtn").click();
        break;
      case "ArrowRight":
        document.getElementById("nextBtn").click();
        break;
    }
  }
});

document.addEventListener("keydown", (e) => {
  if (e.altKey && e.key === "1") {
    document.querySelectorAll(".carousel-slide")[currentIndex]
      .querySelector(".startBtn")
      ?.click();
  }
  if (e.altKey && e.key === "2") {
    document.querySelectorAll(".carousel-slide")[currentIndex]
      .querySelector(".stopBtn")
      ?.click();
  }
  if (e.altKey && e.key === "q") document.getElementById("prevBtn").click();
  if (e.altKey && e.key === "w") document.getElementById("nextBtn").click();
});


function handleSwipe() {
  if (pouring || mode === "create" || mode === "edit") {
    return
  }
  const threshold = 30;
  const keys = Object.keys(drinkConfigs);
  if (touchEndX < touchStartX - threshold) {
    currentIndex = (currentIndex + 1) % keys.length;
  } else if (touchEndX > touchStartX + threshold) {
    currentIndex = (currentIndex - 1 + keys.length) % keys.length;
  }
  updateSlidePosition();
}

window.onload = initApp;
window.addEventListener("load", fetchOtp);

let keyboard = null;
let currentInput = null;

let keyboardEnabled = true;

// Update when checkbox changes
document.getElementById("keyboardToggle").addEventListener("click", function () {
  keyboardEnabled = !keyboardEnabled;

  // Update button label
  this.textContent = keyboardEnabled ? "Disable Keyboard" : "Enable Keyboard";

  // Hide keyboard if disabling
  if (!keyboardEnabled) {
    hideKeyboard();
  }
});

function showKeyboard(layout = "default", inputEl) {
  if (!keyboardEnabled) return;

  currentInput = inputEl;

  if (!keyboard) {
    keyboard = new window.SimpleKeyboard.default({
      onChange: input => {
        if (currentInput) {
          currentInput.value = input;

          // Fire a real input event so your existing listener runs
          currentInput.dispatchEvent(new Event("input", { bubbles: true }));
        }
      },
      layout: {
        default: [
          "q w e r t y u i o p",
          "a s d f g h j k l",
          "{shift} z x c v b n m {bksp}",
          "{space} {enter}"
        ],
        shift: [
          "Q W E R T Y U I O P",
          "A S D F G H J K L",
          "{shift} Z X C V B N M {bksp}",
          "{space}"
        ],
        numbers: [
          "1 2 3 {up} {bksp}",
          "4 5 6 {down} {enter}",
          "7 8 9 0 ."
        ]
      },
      display: {
        "{bksp}": "⌫",
        "{space}": "␣",
        "{shift}": "⇧",
        "{enter}": "↵",
        "{up}" : "⬆",
        "{down}" : "⬇"
      },
      onKeyPress: button => {
        if (button === "{shift}") handleShift();
        else if (button === "{bksp}") {
          currentInput.value = currentInput.value.slice(0, -1);
          keyboard.setInput(currentInput.value);

          // Fire input event again after backspace
          currentInput.dispatchEvent(new Event("input", { bubbles: true }));
        }
        else if (button === "{enter}") hideKeyboard();
        else if (button === "{up}") {
            currentInput.value = parseFloat(currentInput.value) + 1;
        }
        else if (button === "{down}") {
            if (parseFloat(currentInput.value) >= 1) {
                currentInput.value = parseFloat(currentInput.value) - 1;
            }
        }
        currentInput.dispatchEvent(new Event("input", { bubbles: true }));
      }
    });
  }

  const layoutName = layout === "numbers" ? "numbers" : "default";
  keyboard.setOptions({ layoutName });
  keyboard.setInput(currentInput.value || "");
  document.getElementById("keyboard").style.display = "block";

  // Ensure blur handler is only added once per input
  inputEl.addEventListener("blur", handleBlur);
  inputEl._hasKeyboardBlurHandler = true;
}

function handleBlur(e) {
  setTimeout(() => {
    const keyboardEl = document.getElementById("keyboard");

    // Get the element that was clicked/tapped
    let lastClickTarget = window._lastClickTarget;

    if (
      !lastClickTarget ||
      (!keyboardEl.contains(lastClickTarget) &&
      lastClickTarget.tagName !== 'INPUT' &&
      lastClickTarget.contentEditable !== 'true')
    ) {
      hideKeyboard();
    }
  }, 100);
}

// Track last clicked/tapped element globally
document.addEventListener("mousedown", e => {
  window._lastClickTarget = e.target;
});
document.addEventListener("touchstart", e => {
  window._lastClickTarget = e.target;
});


function hideKeyboard() {
  document.getElementById("keyboard").style.display = "none";
  currentInput = null;
}



function handleShift() {
  const current = keyboard.options.layoutName;
  if (current === "numbers") return; // don't shift numbers
  const newLayout = current === "default" ? "shift" : "default";
  keyboard.setOptions({ layoutName: newLayout });
}

document.getElementById("shutdownBtn").addEventListener("click", async () => {
  if (!confirm("Are you sure you want to shutdown the ADMD?")) return;

  try {
    const res = await fetch("/api/shutdown", { method: "POST" });
    if (res.ok) {
      alert("Shutdown command sent. The Raspberry Pi will power off shortly.");
    } else {
      alert("Failed to send shutdown command.");
    }
  } catch (err) {
    console.error("Shutdown error:", err);
    alert("Error while sending shutdown request.");
  }
});
