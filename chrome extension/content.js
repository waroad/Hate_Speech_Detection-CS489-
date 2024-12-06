chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("onMessage triggered:", message); // 디버깅 실행확인
    if (message.action === "showResult") {
        console.log("Message received:", message); // 디버깅 메시지 로그

        const resultText = message.resultText;
        const highlightData = message.highlightData;
        console.log("Received resultText:", resultText); // 디버깅 로그
        console.log("Received highlightData:", highlightData); // 디버깅 하이라이트 데이터

        if (!resultText || !Array.isArray(highlightData)) {
            console.error("Error: Invalid resultText or highlightData format");
            return;
        }

        // 선택된 텍스트의 위치 가져오기
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect();
            const selectedText = range.toString();
            console.log("Selected text:", selectedText); // 디버깅 드래그된 텍스트 확인

            // 결과 박스 생성
            const resultBox = document.createElement("div");
            resultBox.innerHTML = resultText; // 박스 출력용 텍스트 설정
            resultBox.style.position = "absolute";
            resultBox.style.top = `${rect.bottom + window.scrollY}px`;
            resultBox.style.left = `${rect.left + window.scrollX}px`;
            resultBox.style.backgroundColor = "#ffffff";
            resultBox.style.color = "#7000000";
            resultBox.style.border = "1px solid #dcdcdc";
            resultBox.style.borderRadius = "4px";
            resultBox.style.padding = "5px";
            resultBox.style.zIndex = "1000";
            resultBox.style.fontFamily = "Arial, sans-serif";
            resultBox.style.maxWidth = "300px";
            // 자동하이라이트 제거
            window.getSelection().removeAllRanges();
            // -1, -1 인덱스 체크
            const hasGlobalHighlight = highlightData.some(({ startIdx, endIdx }) => startIdx === -1 && endIdx === -1);

            // 클릭 카운터를 통한 결과박스, 하이라이트 제거
            let clickCounter = 0;

            // 화면 클릭 시 동작
            const handleClick = () => {
                clickCounter++;
                if (clickCounter === 1) {
                    // 첫 번째 클릭: 결과 박스 제거
                    if (resultBox.parentNode) {
                        resultBox.remove();
                        console.log("Result box removed."); // 디버깅 결과 박스 제거
                    }

                    if (!hasGlobalHighlight) {
                        const highlightedElements = document.querySelectorAll(".highlighted");
                        highlightedElements.forEach((span) => {
                            const parent = span.parentNode;
                            if (parent) {
                                const textNode = document.createTextNode(span.textContent);
                                console.log(`Restoring text: ${span.textContent}`); // 디버깅 복원할 텍스트 확인
                                parent.replaceChild(textNode, span);
                                parent.normalize();
                            }
                        });
                        console.log("Highlights removed."); // 디버깅 하이라이트 제거 확인
                    }
                    document.body.removeEventListener("click", handleClick); // 이벤트 제거
                } else if (clickCounter === 2) {
                    // 두 번째 클릭: 하이라이트 제거

                }
            };

            document.body.addEventListener("click", handleClick);
            document.body.appendChild(resultBox);
            console.log("Result box appended to body."); // 디버깅

            // -1, -1일 경우 하이라이트 건너뛰기
            if (hasGlobalHighlight) {
                console.log("Global highlight detected. Only resultBox will be shown.");
                return;
            }

            highlightData.forEach(({ category, startIdx, endIdx }) => {

                // Create the highlight span element
                const highlightSpan = document.createElement("span");
                highlightSpan.className = "highlighted";
                highlightSpan.style.backgroundColor = "yellow";
                highlightSpan.style.fontWeight = "bold";
                highlightSpan.title = category;

                // Clone the range for this specific highlight
                const highlightRange = document.createRange();

                // Adjust range for highlighting
                const { startContainer, startOffset } = range;
                let currentOffset = 0;
                let targetNode = startContainer;

                // Traverse to the right node for `startIdx`
                while (targetNode.nodeType !== Node.TEXT_NODE || currentOffset + targetNode.textContent.length <= startIdx) {
                    currentOffset += targetNode.textContent ? targetNode.textContent.length : 0;
                    targetNode = targetNode.nextSibling;
                }

                // Set start and end points for this highlight
                highlightRange.setStart(targetNode, startIdx - currentOffset);
                highlightRange.setEnd(targetNode, endIdx - currentOffset);

                // Surround the selected range with the highlight span
                try {
                    highlightRange.surroundContents(highlightSpan);
                } catch (e) {
                    console.error("Error surrounding contents:", e);
                }
            });



            // 자동하이라이트 제거
            window.getSelection().removeAllRanges();
            console.log("Highlighted text applied to selection."); // 디버깅
        } else {
            console.error("No valid text selection found."); // 디버깅
        }
    } else {
        console.warn("No valid action found in message."); // 디버깅
    }
});
