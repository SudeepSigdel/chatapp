let ws = null

function router() {
    const hash = window.location.hash

    document.getElementById("login-view").classList.add("hidden")
    document.getElementById("chat-view").classList.add("hidden")
    document.getElementById("register-view").classList.add("hidden")

    if (hash === "#/chat") {
        document.getElementById("chat-view").classList.remove("hidden");
        connectWebSocket();
    } else if (hash === "#/login" || hash === "") {
        document.getElementById("login-view").classList.remove("hidden");
        disconnectWebSocket();
    }
    else if (hash === "#/register") {
        document.getElementById("register-view").classList.remove("hidden");
        disconnectWebSocket();
    }
}

window.addEventListener("hashchange", router)
window.addEventListener("load", router)


async function register(event) {
    event.preventDefault()
    const email = document.getElementById("email-register").value;
    const password = document.getElementById("password-register").value;
    const name = document.getElementById("name-register").value;
    try {
        const response = await fetch("http://127.0.0.1:8000/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email,
                password: password,
                name: name
            })
        });

        if (!response.ok) {
            const error = await response.json();
            alert(error.detail || "Register failed");
            return;
        }

        const result = await response.json();

        currentuser = result.name;
        console.log("Registered as:", currentuser);

        window.location.hash = "#/login";

    } catch (error) {
        console.error("Network error:", error);
        alert("Server unreachable");
    }
}


async function login(event) {
    event.preventDefault()
    const username = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    try {
        const response = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: {
                'accept': 'application/json',
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });

        if (!response.ok) {
            const error = await response.json();
            alert(error.detail || "Login failed");
            return;
        }

        const result = await response.json();

        const token = result.access_token;
        console.log("Access Token:", token);
        // document.cookie= `access_token: ${token}`
        localStorage.setItem("access_token",token)
        window.location.hash = "#/chat";

    } catch (error) {
        console.error("Network error:", error);
        alert("Server unreachable");
    }
}


function logout() {
    window.location.hash = "#/login"
    localStorage.removeItem("access_token")
    disconnectWebSocket()
}

function to_register() {
    window.location.hash = "#/register"
}

function connectWebSocket() {
    const token = localStorage.getItem("access_token")
    if (!token) { window.location.hash = "#/login" };
    ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
    ws.onmessage = function (event) {
        var messages = document.getElementById("messages")
        var message = document.createElement("li")
        var content = document.createTextNode(event.data)
        message.appendChild(content)
        messages.appendChild(message)
    };
}

function disconnectWebSocket() {
    if (ws) {
        ws.close()
        ws = null
    }
}

function SendMessage(event) {
    var input = document.getElementById("MessageBox")
    if (ws && input.value.trim()) {
        ws.send(input.value)
        input.value = '';
        event.preventDefault()
    }
};