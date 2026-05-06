const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const chatMessages = document.getElementById('chat-messages');

const STREAM_API_URL = '/chat/stream';
const STATUS_API_URL = '/status';
const SESSION_ID = 'user_' + Math.random().toString(36).substr(2, 9);

// Fetch Knowledge Base Status
async function updateStatus() {
    try {
        const res = await fetch(STATUS_API_URL);
        const data = await res.json();
        document.getElementById('last-updated').innerText = `Last Updated: ${data.last_updated}`;
    } catch (e) {
        document.getElementById('last-updated').innerText = `Last Updated: Offline`;
    }
}
updateStatus();

function createMessageBubble(sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    const now = new Date();
    const timeStr = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    
    messageDiv.innerHTML = `
        <div class="message-bubble"></div>
        <div class="message-meta">${timeStr}</div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return messageDiv.querySelector('.message-bubble');
}

function updateBubble(bubble, text) {
    // Convert markdown-style URLs to clickable links
    const formattedText = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank" style="color: #60a5fa;">$1</a>');
    bubble.innerHTML = formattedText.replace(/\n/g, '<br>');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const query = userInput.value.trim();
    if (!query) return;

    // Add user message
    const userBubble = createMessageBubble('user');
    updateBubble(userBubble, query);
    userInput.value = '';

    // Create bot bubble for streaming
    const botBubble = createMessageBubble('bot');
    botBubble.innerHTML = '<span class="loading-dots">...</span>';

    try {
        const response = await fetch(STREAM_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, session_id: SESSION_ID }),
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = '';
        botBubble.innerHTML = ''; // Clear loading

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            updateBubble(botBubble, fullText);
        }
    } catch (error) {
        updateBubble(botBubble, 'Error: Could not connect to the backend. Ensure Phase 4 server is running.');
        console.error('API Error:', error);
    }
});

