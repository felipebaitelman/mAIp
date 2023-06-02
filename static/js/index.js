// static/js/index.js
window.onload = function () {
    document.getElementById("chat-form").addEventListener("submit", function (event) {
        // Prevent the form from submitting and refreshing the page
        event.preventDefault();

        let userInput = document.getElementById("indicator").value;
        let chartType = document.getElementById("chart-type").value;
        let region = document.getElementById("region").value;
        let countryInput = document.getElementById("country-input").value;
        let analysisType = document.querySelector('input[name="analysis_type"]:checked').value;
        let yearStart = document.getElementById("year-start").value;
        let yearEnd = document.getElementById("year-end").value;

        let postData = {
            user_input: userInput,
            chart_type: chartType,
            region: region,
            country: countryInput,
            analysis_type: analysisType,
            year_start: yearStart,
            year_end: yearEnd
        };

        let url = '/gpt4/chat';

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(postData),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                // Display the error message to the user
                let errorDiv = document.getElementById("error-message");
                errorDiv.innerText = data.message;
                errorDiv.style.display = "block";
            } else {
                // Clear any previous error message
                let errorDiv = document.getElementById("error-message");
                errorDiv.innerText = "";
                errorDiv.style.display = "none";

                fetch('/gpt4')
                .then((response) => response.json())
                .then((data) => {
                    let seabornPlotDiv = document.getElementById("seaborn-plot");
                    if (data.error) {
                        // Display the error message in the HTML
                        seabornPlotDiv.innerHTML = `<div class="error-message">${data.message}</div>`;
                    } else {
                        seabornPlotDiv.innerHTML = `<img src="${data.plot_url}" alt="Seaborn Plot">`;
                    }
                })
                .catch((error) => {
                    console.error("Error fetching Seaborn Plot:", error);
                    // Display a generic error message to the user
                    let errorDiv = document.getElementById("error-message");
                    errorDiv.innerText = "An error occurred while fetching the Seaborn Plot.";
                    errorDiv.style.display = "block";
                });
            }
        })
        .catch((error) => {
            console.error("Error fetching GPT-4 response:", error);
            // Display a generic error message to the user
            let errorDiv = document.getElementById("error-message");
            errorDiv.innerText = "An error occurred while fetching the GPT-4 response.";
            errorDiv.style.display = "block";
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
