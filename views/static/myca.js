const chatButton = document.getElementById("myca-button");
const chatBox = document.getElementById("myca-chatbox");
const chatMessages = document.getElementById("chat-messages");
const sendButton = document.getElementById("send-button");
const userInput = document.getElementById("user-message");

chatButton.onclick = () => {
  chatBox.style.display = chatBox.style.display === "none" ? "flex" : "none";
};

sendButton.onclick = sendMessage;
userInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") sendMessage();
});

// Load saved chat history on page load
window.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("chatHistory");
  if (saved) {
    chatMessages.innerHTML = saved;
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
});

// Save chat history during session
function saveMessages() {
  localStorage.setItem("chatHistory", chatMessages.innerHTML);
}

function formatText(text) {
  return text
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")  // Bold
    .replace(/\*(?!\*)(.*?)\*/g, "<em>$1</em>");       // Italic
}

function appendMessage(sender, text) {
  const message = document.createElement("div");
  message.classList.add("message");
  message.classList.add(sender === "You" ? "user-message" : "bot-message");

  message.innerHTML = `<strong>${sender}:</strong> ${formatText(text)}`;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  saveMessages();
}

async function sendMessage() {
  const userText = userInput.value.trim();
  if (!userText) return;

  appendMessage("You", userText);
  userInput.value = "";

  appendMessage("Myca", "Typing...");

  try {
    const res = await fetch("/myca-chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userText }),
    });

    const data = await res.json();
    chatMessages.lastChild.remove(); // Removes the placeholder "Typing..."
    appendMessage("Myca", data.reply);
  } catch (err) {
    chatMessages.lastChild.remove();
    appendMessage("Myca", "Sorry, I'm currently unable to respond. Please try again later.");
  }
}

// Deletes messages/prompts upon logging out
const logoutLink = document.querySelector('a.logout-btn[href="/logout"]');

logoutLink?.addEventListener("click", function (e) {
  localStorage.removeItem("chatHistory");
});

