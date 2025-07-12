document.getElementById("ask-btn").addEventListener("click", async () => {
  const question = document.getElementById("question").value;
  const responseBox = document.getElementById("response-box");
  const responseText = document.getElementById("response");
  const loadingText = document.getElementById("loading");

  responseBox.style.display = "none";
  loadingText.style.display = "block";
  responseText.textContent = "";

  // Get current YouTube videoId
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.tabs.sendMessage(tab.id, { action: "getVideoId" }, async (res) => {
    if (!res || !res.videoId) {
      responseText.textContent = "Could not detect YouTube video.";
      loadingText.style.display = "none";
      responseBox.style.display = "block";
      return;
    }

    // Call backend API
    try {
      const backendRes = await fetch("http://localhost:5000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ videoId: res.videoId, question }),
      });

      const data = await backendRes.json();
      responseText.textContent = data.answer || "No answer received.";
    } catch (err) {
      responseText.textContent = "Error: Could not connect to backend.";
    } finally {
      loadingText.style.display = "none";
      responseBox.style.display = "block";
    }
  });
});
