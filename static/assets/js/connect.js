// ✅ POPUP MESSAGE
const popup = document.getElementById("popup-message");
const msgData = document.getElementById("django-messages");

if (popup && msgData) {
    const messages = JSON.parse(msgData.textContent);
    if (messages.length > 0) {
        let msg = messages[0];
        popup.innerText = msg.text;

        if (msg.tags.includes("success")) {
            popup.style.background = "#2ecc71";
        } else if (msg.tags.includes("error")) {
            popup.style.background = "#e74c3c";
        } else {
            popup.style.background = "#3498db";
        }

        setTimeout(() => { popup.style.top = "20px"; }, 300);
        setTimeout(() => { popup.style.top = "-100px"; }, 4000);
    }
}

// ✅ APPROVAL NOTIFICATION BAR
const dataElement = document.getElementById("approved-data");
const bar = document.getElementById("notification-bar");

if (dataElement && bar) {
    const data = JSON.parse(dataElement.textContent);

    const newMessages = data.filter(item => {
        const key = `seen_approval_${item.name}`;
        return localStorage.getItem(key) !== "shown";
    });

    let index = 0;

    function showNextMessage() {
        if (index >= newMessages.length) return;

        const current = newMessages[index];
        bar.innerText = "Request Approved by " + current.name;
        bar.style.top = "0";

        localStorage.setItem(`seen_approval_${current.name}`, "shown");

        setTimeout(() => {
            bar.style.top = "-100px"; 
            setTimeout(() => {
                index++;
                showNextMessage();
            }, 600);
        }, 5000);
    }

    if (newMessages.length > 0) {
        setTimeout(showNextMessage, 1000);
    }
}