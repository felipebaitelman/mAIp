// static/js/index.js
window.onload = function () {
    document
        .getElementById("chat-form")
        .addEventListener("submit", function (event) {
            // Prevent the form from submitting and refreshing the page
            event.preventDefault();

            let userInput = document.getElementById("indicator").value;
            let chartType = document.getElementById("chart-type").value;
            let region = document.getElementById("region").value;
            let countryInput = document.getElementById("country-input").value;

            // Only include the country input if the "specific-country" option is selected
            let postData = (region === "specific-country") ? { user_input: userInput, chart_type: chartType, region: region, country: countryInput } : { user_input: userInput, chart_type: chartType, region: region };

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

    // Set the initial state of the radio buttons
    document.getElementById("time-series").checked = true;
    document.getElementById("region").value = "specific-country";
    document.getElementById("region").disabled = true;
    document.getElementById("year-end").disabled = false;
    document.getElementById("country-input").disabled = false;
    document.getElementById("year-end").value = "";

};

// When the user changes the radio button to "One Year", lock the year-end radio button and clear the country input
document.getElementById("one-year").addEventListener('change', function(event) {
    document.getElementById("year-end").value = "";
    document.getElementById("year-end").disabled = true;
    document.getElementById("country-input").value = "";
    document.getElementById("country-input").disabled = true;
    document.getElementById("region").disabled = false;
    let options = document.getElementById("region").options;
    for (let i = 0; i < options.length; i++) {
        if (options[i].value === "specific-country") {
            options[i].remove();
        }
    }
});

// When the user changes the radio button to "Time Series", enable the "Year End" radio button
document.getElementById("time-series").addEventListener('change', function(event) {
    document.getElementById("region").options.add(new Option("Specific Country", "specific-country"));
    document.getElementById("year-end").disabled = false;
    document.getElementById("region").value = "specific-country";
    document.getElementById("region").disabled = true;
    document.getElementById("country-input").value = "";
    document.getElementById("country-input").disabled = false;
});
