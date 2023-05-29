import os
import json
import seaborn as sns
import pandas as pd
from io import BytesIO
import ast
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import base64


from flask import Flask, render_template, request, jsonify, send_file, make_response, Response, session
import openai
from openai.error import RateLimitError

app = Flask(__name__)
app.secret_key = '123'
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template('index.html')

# Split the responsibilities of the /gpt4 endpoint
@app.route('/gpt4/chat', methods=['POST'])
def gpt4_chat():
    user_input = request.get_json()['user_input']

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

    prompt = "Return text formatted as a python dictionary with the following countries: " + str(latin_american_countries) + \
             " and an associated random integer between 1 and 100. Provide only the dictionary, not the code implementation."

    messages = [{"role": "user", "content": prompt}]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )

        content = response.choices[0].message["content"]

    except RateLimitError:
        content = "The server is experiencing a high volume of requests. Please try again later."

    content = response.choices[0].message["content"]
    session['content'] = content
    return jsonify(content=content)

@app.route('/gpt4', methods=['GET'])
def gpt4_plot():
    content = session.get('content', '{}')
    country_dict = ast.literal_eval(content)
    df = pd.DataFrame(list(country_dict.items()), columns=['Country', 'Value'])
    df['Value'] = pd.to_numeric(df['Value'])

    g = sns.catplot(data=df, x='Country', y='Value', kind="bar", height=5, aspect=1.5)
    g.set_xticklabels(rotation=45, horizontalalignment='right')
    plt.xlabel("Country", size=14)
    plt.ylabel("Value", size=14)
    plt.title("Seaborn Barplot Example", size=18)
    plt.tight_layout()

    # Save plot/figure into a bytes object
    img = BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plot_url = 'data:image/png;base64,{}'.format(plot_url)
    return jsonify(plot_url=plot_url)



if __name__ == '__main__':
    app.run(debug=True)