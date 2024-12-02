// 확장 프로그램이 설치,업데이트 되었을 때 컨텍스트 메뉴를 생성
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "analyzeText",
        title: "Analyze this text",
        contexts: ["selection"]
    });
});

// 컨텍스트 메뉴가 클릭되었을 때 실행되는 이벤트 리스너
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "analyzeText" && info.selectionText) {
        const selectedText = info.selectionText;

        // 서버에 텍스트를 전달하고 결과를 content.js에 보내기
        fetch('http://localhost:5000/inference', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ sentence: selectedText }),
        })
            .then((response) => response.json())
            .then((result) => {
                console.log("server response:", result) //디버깅용
                
                // Localization 데이터를 순회하여 중복 제거
                const localizationResults = Array.from(
                    new Map(
                        result.localization_list.map(([category, startIdx, endIdx]) => [
                            `${startIdx}-${endIdx}`,
                            `${result.sentence.slice(startIdx, endIdx)} : '${category}'`,
                        ])
                    ).values()
                )
                .map((entry) => `${entry}<br>`) // 줄바꿈 적용
                .join("\n");

                const resultText = localizationResults.length > 0
                    ? localizationResults
                    : "No hate expressions detected.";

                // 결과를 content.js에 전달
                chrome.tabs.sendMessage(tab.id, {
                    action: 'showResult',
                    resultText: resultText,
                });
            })
            .catch((error) => {
                const errorMessage = "Error: Could not connect to the server.";
                // 에러 메시지를 content.js에 전달
                chrome.tabs.sendMessage(tab.id, {
                    action: 'showResult',
                    resultText: errorMessage,
                });
            });
    }
});
