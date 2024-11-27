const OpenAI = require('openai');

self.addEventListener('message', async (event) => {
    const data = event.data;

    if (data.action === 'fetch_readme') {
        const repoURL = data.url;

        const readmeContent = await fetchReadme(repoURL);

        if (readmeContent) {
            // Store the README.md content in the worker for further use
            self.readmeContent = readmeContent;
            console.log(readmeContent)
            self.postMessage("README.md fetched and ready to answer questions.!");
        } else {
            self.postMessage("No !!!!! README.md found or unable to fetch.!");
        }
    } else if (data.action === 'ask_question') {
        // User asks a question based on the already fetched README.md content
        if (!self.readmeContent) {
            self.postMessage("README.md content not available.");
            return;
        }

        const responseText = await answerQuestion(data.key, self.readmeContent, data.question);
        self.postMessage(responseText);
    } else if (data.action === 'ask_question2') {
        // User asks a question based on the already fetched README.md content
        
        const responseText = await getPLMResult(data.question);
        self.postMessage(responseText);
    }

});

// Function to fetch README.md from a GitHub repo
async function fetchReadme(repoURL) {
    try {
        const match = repoURL.match(/github\.com\/([^\/]+)\/([^\/]+)/);
        if (!match) return null;

        const owner = match[1];
        const repo = match[2];

        const readmeURL = `https://raw.githubusercontent.com/${owner}/${repo}/master/README.md`;
        const response = await fetch(readmeURL);
        
        if (!response.ok) {
            console.log("Failed to fetch README.md:", response.statusText);
            return null;
        }

        return await response.text();
    } catch (error) {
        console.error("Error fetching README.md:", error);
        return null;
    }
}

// Function to answer a question based on the README.md
async function answerQuestion(key, readmeContent, question) {
    const openai = new OpenAI({
        apiKey: key,
        dangerouslyAllowBrowser: true,
    });

    const completion = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [
            { role: "system", content: "You are a helpful assistant." },
            {
                role: "user",
                content: `Here is the README.md content:\n\n${readmeContent}\n\nThe user has the following question: "${question}". Answer based on the README.`,
            },
        ],
    });

    return completion.choices[0].message.content;
}
async function getPLMResult(inputText) {
    const response = await fetch('http://localhost:5000//process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: inputText
        }),
    });

    const data = await response.json();
    console.log("Server response:", data);  // Log the server response
    return data.response;  // Return the "response" field from the JSON
}