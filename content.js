chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "getVideoId") {
    const urlParams = new URLSearchParams(window.location.search);
    const videoId = urlParams.get("v");
    console.log("content.js got videoId:", videoId);
    sendResponse({ videoId });
  }
  return true;
});
