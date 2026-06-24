const API_BASE_URL =
    "http://docs-to-docs-alb-256373683.eu-west-2.elb.amazonaws.com";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message?.action !== "generate") {
        return;
    }

    handleGenerate(message);

    return true;
});

async function handleGenerate(message) {
    const { url, packageName } = message;

    try {
        const response = await fetch(`${API_BASE_URL}/generate`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url,
                package_name: packageName
            })
        });

        if (!response.ok) {
            let errorMessage = `Request failed (${response.status})`;

            try {
                const errorData = await response.json();
                errorMessage =
                    errorData.detail ||
                    errorData.message ||
                    errorMessage;
            } catch {
                // Ignore JSON parsing errors
            }

            throw new Error(errorMessage);
        }

        const data = await response.json();

        const downloadUrl =
            data.download_url ||
            data.presigned_url ||
            data.url;

        if (!downloadUrl) {
            throw new Error(
                "Backend response did not include a download URL"
            );
        }

        chrome.notifications.create(
            "docs-to-docs-notification",
            {
                type: "basic",
                iconUrl: "icon.png",
                title: "Docs to Docs",
                message: "Your guide is ready — downloading now"
            }
        );

        await chrome.downloads.download({
            url: downloadUrl,
            filename: `${packageName}_guide.docx`,
            saveAs: false
        });

        try {
            chrome.runtime.sendMessage({ status: "done" });
        } catch {
            // popup was closed, that's fine
        }

    } catch (error) {
        console.error("Guide generation failed:", error);

        try {
            chrome.runtime.sendMessage({
                status: "error",
                message: error.message || "Unknown error"
            });
        } catch {
            // popup was closed, that's fine
        }
    }
}