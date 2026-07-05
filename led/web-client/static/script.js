const API_URL = "/api/leds/action";

function writeLog(title, payload) {
    const time = new Date().toLocaleTimeString();

    console.log(
        `[${time}] ${title}\n` +
        JSON.stringify(payload, null, 2) +
        "\n"
    );
}

function getLedContext(element) {
    const card = element.closest(".led-card");

    if (!card) {
        return null;
    }

    return {
        card: card,
        ledId: card.dataset.ledId,
        gpioPin: Number(card.dataset.gpioPin)
    };
}

function updateCardEnabledState(card, enabled) {
    card.classList.toggle("is-disabled", !enabled);

    const toggleText = card.querySelector(".enable-toggle .toggle-text");
    if (toggleText) {
        toggleText.textContent = enabled ? "Enabled" : "Disabled";
    }

    const commandButtons = card.querySelectorAll(".command-button[data-command]");

    commandButtons.forEach(function (button) {
        const command = button.dataset.command;

        // Keep Quit available even when the LED is disabled.
        if (command !== "quit") {
            button.disabled = !enabled;
        }
    });
}

async function postJson(payload) {
    writeLog("Posting JSON", payload);

    const response = await fetch(API_URL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const result = await response.json();
    writeLog("Server response", result);
    return result;
}

document.addEventListener("click", async function (event) {
    const globalButton = event.target.closest("button[data-scope='all'][data-command]");

    if (globalButton) {
        const payload = {
            scope: "all",
            command: globalButton.dataset.command
        };

        await postJson(payload);
        return;
    }

    const ledButton = event.target.closest(".led-card button[data-command]");

    if (!ledButton) {
        return;
    }

    const context = getLedContext(ledButton);

    if (!context) {
        console.warn("Clicked LED button is not inside a .led-card.");
        return;
    }

    const payload = {
        scope: "led",
        led_id: context.ledId,
        gpio_pin: context.gpioPin,
        command: ledButton.dataset.command
    };

    await postJson(payload);
});

document.addEventListener("change", async function (event) {
    const enableInput = event.target.closest(
        ".led-card input[type='checkbox'][data-command='enable']"
    );

    if (!enableInput) {
        return;
    }

    const context = getLedContext(enableInput);

    if (!context) {
        console.warn("Changed enable input is not inside a .led-card.");
        return;
    }

    const enabled = enableInput.checked;

    updateCardEnabledState(context.card, enabled);

    const payload = {
        scope: "led",
        led_id: context.ledId,
        gpio_pin: context.gpioPin,
        command: "enable",
        enabled: enabled
    };

    await postJson(payload);
});