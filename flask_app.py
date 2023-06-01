import os
import json
import seaborn as sns
import pandas as pd
from io import BytesIO
import ast
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.font_manager as fm
from matplotlib import rcParams
matplotlib.use('Agg')
import base64


from flask import Flask, render_template, request, jsonify, send_file, make_response, Response, session
import openai
from openai.error import RateLimitError

app = Flask(__name__)
app.secret_key = '123'
openai.api_key = os.getenv("OPENAI_API_KEY")

# Add the font directory to the font manager path
font_dir = './fonts'  # directory where your fonts are
font_files = fm.findSystemFonts(fontpaths=font_dir)
for font_file in font_files:
    fm.fontManager.addfont(font_file)

@app.route('/')
def index():
    return render_template('index.html')

# Split the responsibilities of the /gpt4 endpoint
@app.route('/gpt4/chat', methods=['POST'])
def gpt4_chat():
    user_input = request.get_json()['user_input']
    session['user_input'] = user_input  # Save the user's input to the session
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

    # Change font of Seaborn chart
    font_path = './fonts/Montserrat-Regular.ttf'  # replace with your .ttf file
    font_prop = matplotlib.font_manager.FontProperties(fname=font_path, family='Montserrat')
    matplotlib.rcParams['font.family'] = 'Montserrat'

    content = session.get('content', '{}')
    country_dict = ast.literal_eval(content)
    df = pd.DataFrame(list(country_dict.items()), columns=['Country', 'Value'])
    df['Value'] = pd.to_numeric(df['Value'])

    g = sns.catplot(data=df, x='Country', y='Value', kind="bar", height=7, aspect=1.5)
    g.set_xticklabels(rotation=45, horizontalalignment='right')
    user_input = session.get('user_input', 'Default Title')  # Retrieve the user's input from the session
    plt.xlabel("Country", size=15, fontproperties=font_prop)
    plt.ylabel("Value", size=15, fontproperties=font_prop)

    plt.tight_layout()

    g.fig.suptitle(user_input, size=25, y=1, fontproperties=font_prop)

    for ax in g.axes.flat:  # g.axes gives the list of all AxesSubplot objects
        for label in ax.get_xticklabels():
            label.set_fontproperties(font_prop)
        for label in ax.get_yticklabels():
            label.set_fontproperties(font_prop)

    # Save plot/figure into a bytes object
    img = BytesIO()

    # Set the background to be transparent
    matplotlib.rcParams['savefig.transparent'] = True

    plt.savefig(img, format='png', dpi=300)
    plt.close()
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plot_url = 'data:image/png;base64,{}'.format(plot_url)
    return jsonify(plot_url=plot_url)



if __name__ == '__main__':
    app.run(debug=True)