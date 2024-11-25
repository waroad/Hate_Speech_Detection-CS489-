const button = document.getElementById('generate');
const response = document.getElementById('response');

//서버에 'Seltected text'전송 -> 'Result text'수령.
button.onclick = async function () {
    const selectedText = "사용자가 선택한 텍스트"; // 선택 텍스트 대체
    try {
        const response = await fetch('https://api.example.com/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: selectedText })
        });
        const result = await response.json();
        document.getElementById("response").textContent = result.message; // 결과 표시
    } catch (error) {
        document.getElementById("response").textContent = "Error: " + error.message;
    }
};