import numpy as np
import pandas as pd
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3

authenticator = IAMAuthenticator('3NqEGQWuRyt64R_Iz1uogCaNJxUqOzJ'
                                 '_BCo0p_GfVYMt')

tone_analyzer = ToneAnalyzerV3(
    version='2017-09-21',
    authenticator=authenticator
)
tone_analyzer.set_service_url('https://gateway-lon.watsonplatform.net/tone-analyzer/api')

df = pd.read_csv('data.csv')
df = df[['name', 'reviews.text']][:200]
tones = []
scores = []
for i in list(df['reviews.text']):
    tone_analysis = tone_analyzer.tone(
        {'text': i},
        content_type='application/json').get_result()
    tone_analysis = tone_analysis['document_tone']['tones']
    tones.append([i['tone_name'] for i in tone_analysis])
    scores.append([i['score'] for i in tone_analysis])

col_name = np.unique([j for i in tones for j in i])
analytical = [scores[i][tones[i].index('Analytical')] if 'analytical' in tones[i] else 0 for i in range(len(tones))]
Confident = [scores[i][tones[i].index('Confident')] if 'Confident' in tones[i] else 0 for i in range(len(tones))]
Joy = [scores[i][tones[i].index('Joy')] if 'Joy' in tones[i] else 0 for i in range(len(tones))]
Sadness = [scores[i][tones[i].index('Sadness')] if 'Sadness' in tones[i] else 0 for i in range(len(tones))]
Tentative = [scores[i][tones[i].index('Tentative')] if 'Tentative' in tones[i] else 0 for i in range(len(tones))]
Anger = [scores[i][tones[i].index('Anger')] if 'Anger' in tones[i] else 0 for i in range(len(tones))]
Fear = [scores[i][tones[i].index('Fear')] if 'Fear' in tones[i] else 0 for i in range(len(tones))]

df_tone = pd.DataFrame({'Hotel_name': list(df['name']), 'analytical': analytical,
                        'Confident': Confident, 'Joy': Joy,
                        'Sadness': Sadness, 'Tentative': Tentative, 'Anger': Anger, 'Fear': Fear})

df_tone = df_tone.groupby('Hotel_name').agg('mean')
df_tone.set_index('Hotel_name', inplace=True)
result = {}
for index, row in df_tone.iterrows():
    result[index] = dict(row)
pass
