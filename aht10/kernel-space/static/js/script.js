function updateClock() {
    const now = new Date();

    const time = now.toLocaleTimeString("en-GB", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
    });

    document.getElementById("current-time").textContent = time;
}

updateClock();
setInterval(updateClock, 1000);

function update() {
    fetch("/sensor-data")
        .then(response => response.json())
        .then(data => {
            const light = document.getElementById("status-light");
            const text = document.getElementById("status-text");

            if (data.ok) {
                document.getElementById("temperature-value").textContent =
                    data.temperature.toFixed(2) + " °C";

                document.getElementById("humidity-value").textContent =
                    data.humidity.toFixed(2) + " %";

                document.getElementById("temperature-status").textContent =
                    data["temperature-status"];

                document.getElementById("humidity-status").textContent =
                    data["humidity-status"];

                light.style.backgroundColor = "green";
                text.textContent = 'Sensor is availble.'
            } else {
                light.style.backgroundColor = "red";
                text.textContent = 'Sensor is not available: ' + data.error;
            }
        })
        .catch(err => console.error("Error fetching env:", err));
}

// Update every 1 second
setInterval(update, 1000);

// Run immediately on page load
update();
