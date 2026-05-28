const API_URL = "https://ai-agent-2-zac5.onrender.com"

async function send() {
    const input = document.getElementById("msg");
    const output = document.getElementById("output");
    const message = input.value.trim();

    if (!message) {
        output.innerText = "Please enter a message first.";
        return;
    }

    output.innerText = "Generating study plan...";

    try {
        const res = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message }),
        });

        const data = await res.json();

        if (!res.ok) {
            output.innerText = data.detail || "Request failed.";
            return;
        }

        output.innerText = data.response || "No response from agent.";
    } catch (err) {
        output.innerText =
            "Could not reach backend. Make sure uvicorn is running on http://127.0.0.1:8000";
        console.error(err);
    }
}

document.getElementById("sendBtn").addEventListener("click", send);
document.getElementById("msg").addEventListener("keydown", (e) => {
    if (e.key === "Enter") send();
});
