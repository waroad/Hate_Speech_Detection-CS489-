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
        console.log("Selected text:", selectedText);
        
        // 여기에 선택한 텍스트를 머신에 넣고, 결과값을 반환하는 로직.
        // 배포서버? openai api?
    }
});
