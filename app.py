import re

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import chardet
import matplotlib.pyplot as plt
import numpy as np
import base64
import sqlite3
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.json_encoder = LazyJSONEncoder
swagger_template = dict(
    info = {
        'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling')
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json'
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
    "enableCORS": False,
}
swagger = Swagger(app, template=swagger_template,config=swagger_config)

def get_db_connection():
    conn = sqlite3.connect('db/list_data.db')
    conn.row_factory = sqlite3.Row
    return conn

@cross_origin()

@swag_from("docs/getlist.yml", methods=['GET'])
@app.route('/getlist', methods=['GET'])

def getlist():
    conn = get_db_connection()
    posts = pd.read_sql_query("SELECT slang, formal FROM KamusAlay", conn)
    conn.close()
    dictionary = dict(zip(posts.slang, posts.formal))
    return dictionary

@swag_from("docs/cleaningdata.yml", methods=['POST'])
@app.route('/cleaningdata', methods=['POST'])
def cleaningdata():
    if 'file' in request.files:   
        file = request.files['file']
        filename = 'data.csv'
        file.save(filename)
        result_file = pd.read_csv(filename, encoding=checkDataType(filename), sep='~!~')
        cleaned_data = []
        for index, row in result_file.iterrows():
            cleaned_text = clean_text(row['Tweet'])
            cleaned_data.append(cleaned_text)
        chartImage = createChart(result_file)
        return jsonify({'text': '\n'.join(cleaned_data), 'image': chartImage.decode('utf-8')})
    else:
        print(request.form)
        cleanedText = clean_text(request.form['textvalue'])
        return cleanedText

def cleanText(text):
    text = text.lower()
    text = text.strip()
    text = re.sub('\n', ' ', text)
    text = re.sub('[^0-9a-zA-Z]+', ' ', text)
    text = re.sub('user|rt', ' ', text)
    text = re.sub('x[a-z0-9]{2}', ' ', text)
    text = re.sub(' +', ' ', text)
    return text

def clean_text(text):
    text = cleanText(text)
    conn = get_db_connection()
    posts = pd.read_sql_query("SELECT slang, formal FROM KamusAlay", conn)
    conn.close()
    dictionary = dict(zip(posts.slang, posts.formal))
    words = []
    for word in text.split(' '):
        if word in dictionary.keys():
            word = dictionary[word]
        words.append(word)
    return ' '.join(words)

def checkDataType(file):
    with open(file, 'rb') as rawdata:
        data_type = chardet.detect(rawdata.read(100000))
        return data_type['encoding']

def createChart(df):

    abusive = df["Abusive"].tolist()
    count_abusive = pd.DataFrame(abusive).sum()[0]

    hs_individual = df["HS_Individual"].tolist()
    count_hs_individual = pd.DataFrame(hs_individual).sum()[0]

    hs_group = df["HS_Group"].tolist()
    count_hs_group = pd.DataFrame(hs_group).sum()[0]

    hs_religion = df["HS_Religion"].tolist()
    count_hs_religion = pd.DataFrame(hs_religion).sum()[0]

    hs_race = df["HS_Race"].tolist()
    count_hs_race = pd.DataFrame(hs_race).sum()[0]

    hs_physical = df["HS_Physical"].tolist()
    count_hs_physical = pd.DataFrame(hs_physical).sum()[0]

    hs_gender = df["HS_Gender"].tolist()
    count_hs_gender = pd.DataFrame(hs_gender).sum()[0]

    hs_other = df["HS_Other"].tolist()
    count_hs_other = pd.DataFrame(hs_other).sum()[0]

    hs_weak = df["HS_Weak"].tolist()
    count_hs_weak = pd.DataFrame(hs_weak).sum()[0]

    hs_moderate = df["HS_Moderate"].tolist()
    count_hs_moderate = pd.DataFrame(hs_moderate).sum()[0]

    hs_strong = df["HS_Strong"].tolist()
    count_hs_strong = pd.DataFrame(hs_strong).sum()[0]

    headers = ['Abusive', 'Individual','Group','Religion','Race','Physical','Gender','Other','Weak','Moderate','Strong']
    values = [count_abusive, count_hs_individual, count_hs_group, count_hs_religion, count_hs_race, count_hs_physical, count_hs_gender, count_hs_other, count_hs_weak, count_hs_moderate, count_hs_strong ]
   
    plt.barh(headers, values, height = 0.1)
    plt.savefig('chart.png', bbox_inches='tight')
    return encodeFile('chart.png')

def encodeFile(fileName):
    with open(fileName, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string

if __name__ == '__main__':
    app.run(debug=True)