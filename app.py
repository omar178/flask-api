import numpy as np
import pandas as pd
import requests
from elasticsearch import Elasticsearch
from flask import Flask, jsonify, render_template, request
from flask_restful import Api
from flask_socketio import SocketIO
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3

app = Flask(__name__)
api = Api(app=app)
app.config['SESSION_TYPE'] = 'filesystem'
socketio = SocketIO(app=app)

clients = []

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


@socketio.on('generate')
def get_tone(client_id):
    """
    :return: hotel reviews scores
    """
    authenticator = IAMAuthenticator('Bt_7ZXX7zc-nG_NWrRaNMwQTO3VD5je1F-4tJ7WIsad3')
    tone_analyzer = ToneAnalyzerV3(
        version='2017-09-21',
        authenticator=authenticator
    )
    tone_analyzer.set_service_url('https://gateway-lon.watsonplatform.net/tone-analyzer/api')

    df = pd.read_csv('data.csv')
    df = df[['name', 'reviews.text']]
    tones = []
    scores = []
    for i in list(df['reviews.text']):
        tone_analysis = tone_analyzer.tone({'text': i}, content_type='application/json').get_result()
        tone_analysis = tone_analysis['document_tone']['tones']
        tones.append([i['tone_name'] for i in tone_analysis])
        scores.append([i['score'] for i in tone_analysis])

    col_name = np.unique([j for i in tones for j in i])
    analytical = [scores[i][tones[i].index('Analytical')] if 'analytical' in tones[i] else 0 for i in
                  range(len(tones))]
    Confident = [scores[i][tones[i].index('Confident')] if 'Confident' in tones[i] else 0 for i in
                 range(len(tones))]
    Joy = [scores[i][tones[i].index('Joy')] if 'Joy' in tones[i] else 0 for i in range(len(tones))]
    Sadness = [scores[i][tones[i].index('Sadness')] if 'Sadness' in tones[i] else 0 for i in range(len(tones))]
    Tentative = [scores[i][tones[i].index('Tentative')] if 'Tentative' in tones[i] else 0 for i in
                 range(len(tones))]
    Anger = [scores[i][tones[i].index('Anger')] if 'Anger' in tones[i] else 0 for i in range(len(tones))]
    Fear = [scores[i][tones[i].index('Fear')] if 'Fear' in tones[i] else 0 for i in range(len(tones))]

    df_tone = pd.DataFrame({'Hotel_name': list(df['name']), 'analytical': analytical,
                            'Confident': Confident, 'Joy': Joy,
                            'Sadness': Sadness, 'Tentative': Tentative, 'Anger': Anger, 'Fear': Fear})
    df_tone.to_csv('tones.csv')

    df_tone = df_tone.groupby('Hotel_name').agg('mean')
    result = {}
    for index, row in df_tone.iterrows():
        result[index] = dict(row)
    socketio.emit('my response', {'data': jsonify(result)}, room=client_id)
    print('generating tones for client {}'.format(client_id))


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    clients.append(request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)


@app.route('/index/')
def get_index():
    """

    :return: perform elastic search
    """
    tone_df = pd.read_csv('tone.csv')
    tone_df.drop('Hotel_name', inplace=True, axis=1)
    main_df = pd.read_csv('data.csv')
    frames = [tone_df, main_df]
    main_df = pd.concat(frames, axis=1)
    main_df.to_csv('data.csv')
    csvfile = pd.read_csv('data.csv', iterator=True, encoding="utf8")
    r = requests.get('http://localhost:9200')
    for i, df in enumerate(csvfile):
        records = df.where(pd.notnull(df), None).T.to_dict()
    list_records = [records[it] for it in records]
    try:
        for j, i in enumerate(list_records):
            es.index(index='index_name', doc_type='data frame', id=j, body=i)
    except IndexError:
        print('error to index data')


@app.route('/index/<string:hotel_name>')
def filter(hotel_name):
    res = es.search(index='index_name', body={'query': {'match': {'name': hotel_name}}})
    return jsonify(res['hits']['hits'])


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    socketio.run(app(debug=True))
