let currentTabUrl = "";
let derivedPackageName = "";

const currentUrlElement = document.getElementById("current-url");
const generateButton = document.getElementById("generate-btn");
const progressContainer = document.getElementById("progress-container");
const statusText = document.getElementById("status-text");

/**
 * Extract hostname from URL
 */
function getDomain(url) {
    try {
        return new URL(url).hostname;
    } catch {
        return "Unknown";
    }
}

/**
 * Derive package name from domain.
 *
 * Examples:
 * docs.crawl4ai.com      -> crawl4ai
 * api.openai.com         -> openai
 * dev.langchain.com      -> langchain
 * docs.python.org        -> python
 * www.fastapi.tiangolo.com -> fastapi
 */
function derivePackageName(domain) {
    const ignored = new Set(["docs", "www", "api", "dev"]);

    const parts = domain
        .toLowerCase()
        .split(".")
        .filter(Boolean);

    const meaningful = parts.find(part => !ignored.has(part));

    return meaningful || parts[0] || "documentation";
}

/**
 * Update UI to loading state
 */
function setLoadingState() {
    generateButton.disabled = true;

    progressContainer.style.display = "block";

    statusText.style.display = "block";
    statusText.style.color = "#555";
    statusText.textContent = "Generating guide...";
}

/**
 * Update UI after success
 */
function setSuccessState() {
    generateButton.disabled = false;
    progressContainer.style.display = "none";
    document.getElementById("success-state").style.display = "flex";
}

function setErrorState(message) {
    generateButton.disabled = false;
    progressContainer.style.display = "none";
    const errorState = document.getElementById("error-state");
    document.getElementById("error-message").textContent = `Error: ${message}`;
    errorState.style.display = "flex";
}
/**
 * Load current active tab
 */
async function loadCurrentTab() {
    try {
        const tabs = await chrome.tabs.query({
            active: true,
            currentWindow: true
        });

        if (!tabs.length) {
            currentUrlElement.textContent = "No active tab";
            return;
        }

        currentTabUrl = tabs[0].url || "";

        const domain = getDomain(currentTabUrl);

        derivedPackageName = derivePackageName(domain);

        currentUrlElement.textContent = domain;
    } catch (error) {
        console.error(error);
        currentUrlElement.textContent = "Unable to read page";
    }
}

/**
 * Generate Guide button click
 */
generateButton.addEventListener("click", () => {
    if (!currentTabUrl) {
        setErrorState("No active page found");
        return;
    }

    setLoadingState();

    chrome.runtime.sendMessage({
        action: "generate",
        url: currentTabUrl,
        packageName: derivedPackageName
    });
});

/**
 * Listen for updates from background.js
 */
chrome.runtime.onMessage.addListener((message) => {
    if (!message?.status) return;

    if (message.status === "done") {
        setSuccessState();
        return;
    }

    if (message.status === "error") {
        setErrorState(message.message || "Unknown error");
    }
});

/**
 * Initialize popup
 */
document.addEventListener("DOMContentLoaded", () => {
    loadCurrentTab();
});

