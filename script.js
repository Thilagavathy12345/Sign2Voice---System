setInterval(() => {
    fetch('/get_sentence')
    .then(res => res.json())
    .then(data => {
        document.getElementById("sentence").innerText = data.sentence;
    });
}, 1000);

function clearText() {
    fetch('/clear');
}

function speakText() {
    fetch('/speak');
}