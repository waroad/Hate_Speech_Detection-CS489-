chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "showResult") {
        const resultText = message.resultText;
        console.log("Received resultText:", resultText); // 디버깅용 로그
        
        if (!resultText) {
            console.error("Error: Received empty resultText");
        }

        // 선택된 텍스트의 위치 가져오기
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
      
            // 결과 박스 생성
            const resultBox = document.createElement("div");
            resultBox.innerHTML = resultText; // innerHTML 사용으로 HTML 태그를 렌더링

            //resultBox.textContent = resultText;
            resultBox.style.position = "absolute";
            resultBox.style.top = `${rect.bottom + window.scrollY}px`;
            resultBox.style.left = `${rect.left + window.scrollX}px`;
            
            // 화면 오른쪽 경계를 넘지 않도록 조정
            const screenWidth = window.innerWidth;
            const boxWidth = 300;
            if (rect.left + boxWidth > screenWidth) {
                resultBox.style.left = `${screenWidth - boxWidth - 100}px`;
            } else {
                resultBox.style.left = `${rect.left + window.scrollX}px`;
            }

            resultBox.style.backgroundColor = "#ffffff";
            resultBox.style.color = "#7000000";
            resultBox.style.border = "1px solid #dcdcdc";
            resultBox.style.borderRadius = "4px";
            resultBox.style.padding = "5px";
            resultBox.style.zIndex = "1000";
            resultBox.style.fontFamily = "Arial, sans-serif";  
                      

            document.body.appendChild(resultBox);
        }
    }
});