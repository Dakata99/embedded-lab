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

/*
    Later, when you connect this to Flask, you can replace the static
    values with data from your backend, for example:

    fetch("/sensor-data")
        .then(response => response.json())
        .then(data => {
            document.getElementById("temperature-value").textContent = data.temperature;
            document.getElementById("humidity-value").textContent = data.humidity;
        });
*/

function updateEnv() {
    fetch("/api/env")
        .then(response => response.json())
        .then(data => {
            document.getElementById("temperature-value").textContent =
                data.temperature.toFixed(2) + " °C";

            document.getElementById("humidity-value").textContent =
                data.humidity.toFixed(2) + " %";
        })
        .catch(err => console.error("Error fetching env:", err));
}

// Update every 1 second
setInterval(updateEnv, 1000);

// Run immediately on page load
updateEnv();
