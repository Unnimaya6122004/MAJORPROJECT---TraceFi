const BACKEND_URL = "http://127.0.0.1:5000";

const popupCard = document.getElementById("popupCard");
const statusBox = document.getElementById("statusBox");
const statusText = document.getElementById("statusText");
const statusIcon = document.getElementById("statusIcon");
const attackTypeEl = document.getElementById("attackType");
const confidenceEl = document.getElementById("confidence");

const icons = {
    normal: `
        <svg class="icon" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="m9 12 2 2 4-4"></path>
        </svg>
    `,
    danger: `
        <svg class="icon" viewBox="0 0 24 24">
            <path d="M12 3 2 21h20L12 3Z"></path>
            <path d="M12 9v4"></path>
            <path d="M12 17h.01"></path>
        </svg>
    `,
    warning: `
        <svg class="icon" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="9"></circle>
            <path d="M12 8v4"></path>
            <path d="M12 16h.01"></path>
        </svg>
    `
};

function setStatus(type, message) {
    statusBox.className = `status ${type}`;
    statusText.innerText = message;
    statusIcon.innerHTML = icons[type];
}

fetch(`${BACKEND_URL}/simulate`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
        attackTypeEl.innerText = data.attack_type;
        confidenceEl.innerText = data.confidence;

        if (data.prediction.includes("DDoS")) {
            setStatus("danger", "DDoS attack detected");
        } else {
            setStatus("normal", "Network operating normally");
        }
    })
    .catch(() => {
        attackTypeEl.innerText = "Unavailable";
        confidenceEl.innerText = "Unavailable";
        setStatus("warning", "Backend offline");
    });

document.getElementById("openDashboard").onclick = () => {
    window.open(`${BACKEND_URL}/dashboard`);
};

document.getElementById("downloadReport").onclick = () => {
    window.open(`${BACKEND_URL}/download-report`);
};

popupCard.addEventListener("pointermove", (event) => {
    const rect = popupCard.getBoundingClientRect();
    popupCard.style.setProperty("--pointer-x", `${event.clientX - rect.left}px`);
    popupCard.style.setProperty("--pointer-y", `${event.clientY - rect.top}px`);
});
