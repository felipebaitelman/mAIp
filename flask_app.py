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

# Split the responsibilities of the /gpt4/chat endpoint
@app.route('/gpt4/chat', methods=['POST'])
def gpt4_chat():

    user_input = request.get_json()['user_input']
    chart_type = request.get_json()['chart_type']
    region = request.get_json()['region']
    country = request.get_json().get('country', '')
    analysis_type = request.get_json()['analysis_type']
    year_start = request.get_json()['year_start']
    year_end = request.get_json()['year_end']

    print(user_input, chart_type, region, country, analysis_type, year_start, year_end)

    session['user_input'] = user_input  # Save the user's input to the session

    prompt = build_prompt(user_input, chart_type, region, country, analysis_type, year_start, year_end)

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
    print(content)

    try:
        country_dict = ast.literal_eval(content)
        if not isinstance(country_dict, dict):
            raise ValueError("Parsed content is not a dictionary.")
    except (ValueError, SyntaxError) as e:
        # Handle the parsing error and return an error response
        error_message = "Sorry! It's not possible to convert ChatGPT's answer to a chart..."
        return jsonify(error=True, message=error_message)

    df = pd.DataFrame(list(country_dict.items()), columns=['Country', 'Value'])
    df['Value'] = df['Value'].apply(lambda x: float(x.strip('%')) if isinstance(x, str) and "%" in x else float(x))

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


def build_prompt(user_input, chart_type, region, country, analysis_type, year_start, year_end):

    prompt = ""

    if analysis_type == "time-series":
        prompt = "Return text formatted as a python dictionary, where keys are years between " +\
            str(year_start) + " and " + str(year_end) + " and values represent " + user_input +\
            " in " + country + " during that period."
    elif analysis_type == "one-year":
        prompt = "Return text formatted as a python dictionary, where keys are countries from " +\
                 region + " and values represent " + user_input + " in the year " + str(year_start)

    print(prompt)
    return prompt


if __name__ == '__main__':
    app.run(debug=True)
