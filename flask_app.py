import os
import json
import seaborn as sns
import pandas as pd

from flask import Flask, render_template, request, jsonify
import openai
from openai.error import RateLimitError

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gpt4', methods=['GET', 'POST'])
def gpt4():

    user_input = request.args.get('user_input') if request.method == 'GET' else request.form['user_input']

    latin_american_countries = [
        "Argentina",
        "Bolivia",
        "Brazil",
        "Chile",
        "Colombia",
        "Costa Rica",
        "Cuba",
        "Dominican Republic",
        "Ecuador",
        "El Salvador",
        "Guatemala",
        "Haiti",
        "Honduras",
        "Mexico",
        "Nicaragua",
        "Panama",
        "Paraguay",
        "Peru",
        "Puerto Rico",
        "Uruguay",
        "Venezuela"
    ]

    prompt = "What was the " + user_input + " for the following countries: " + str(latin_american_countries) + " in 2010?" + \
             " If you can't provide the data, just use a random number. Data will be used for a personal project. Only return results as a Pandas Dataframe."

    prompt = "Return text formatted as a python dictionary with the following countries: " + str(latin_american_countries) + \
             " and an associated random number. Provide only the dictionary, not the code implementation."

    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        content = response.choices[0].message["content"]
    except RateLimitError:
        content = "The server is experiencing a high volume of requests. Please try again later."

    return jsonify(content=content)

if __name__ == '__main__':
    app.run(debug=True)