import os
import json
import seaborn as sns
import pandas as pd
import io
import ast
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('Agg')
matplotlib.use('TkAgg')

from flask import Flask, render_template, request, jsonify, send_file, make_response
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
             " and an associated random integer between 1 and 100. Provide only the dictionary, not the code implementation."

    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        # Get response, convert to dictionary and initiate DataFrame
        content = response.choices[0].message["content"]
        country_dict = ast.literal_eval(content)
        custom_palette = sns.color_palette("Greens", 6)
        df = pd.DataFrame(list(country_dict.items()), columns=['Country', 'Value'])
        df['Value'] = pd.to_numeric(df['Value'])
        print(df)


        sns.catplot(data=df, x='Country', y='Value', kind="bar", height=5, aspect=1.5)
        plt.xlabel("Country", size=14)
        plt.ylabel("Value", size=14)
        plt.title("Seaborn Barplot Example", size=18)
        plt.tight_layout()
        plt.set_xticklabels(rotation=45, horizontalalignment='right')


        # Save plot/figure into a bytes object TODO
        #bytes_image = io.BytesIO()
        #plt.savefig(bytes_image, format='png')
        #bytes_image.seek(0)
        #return send_file(bytes_image, download_name='plot.png', mimetype='image/png')

        return jsonify(content=content)

    except RateLimitError:
        content = "The server is experiencing a high volume of requests. Please try again later."
        return jsonify(content=content)


if __name__ == '__main__':
    app.run(debug=True)