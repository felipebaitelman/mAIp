// static/js/index.js
window.onload = function () {
    document
        .getElementById("chat-form")
        .addEventListener("submit", function (event) {
            // Prevent the form from submitting and refreshing the page
            event.preventDefault();

            let userInput = document.getElementById("user-input").value;
            let url = '/gpt4/chat';

            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ user_input: userInput }),
            })
                .then((response) => response.json())
                .then((data) => {
                    let content = data.content;
                    // let resultDiv = document.getElementById("result");
                    // resultDiv.innerHTML = content;

                    fetch('/gpt4')
                        .then((response) => response.json())
                        .then((data) => {
                            let seabornPlotDiv = document.getElementById("seaborn-plot");
                            seabornPlotDiv.innerHTML = `<img src="${data.plot_url}" alt="Seaborn Plot">`;
                        })
                        .catch((error) => {
                            console.error("Error fetching Seaborn Plot:", error);
                        });
                })
                .catch((error) => {
                    console.error("Error fetching GPT-4 response:", error);
                });
        });
};
