import numpy as np
import pandas as pd
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3

authenticator = IAMAuthenticator('3NqEGQWuRyt64R_Iz1uogCaNJxUqOzJ_BCo0p_GfVYMt')
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
    tone_analysis = tone_analysis.pop('document_tone').pop('tones')
    tones.append([i['tone_name'] for i in tone_analysis])
    scores.append([i['score'] for i in tone_analysis])

col_name = np.unique([j for i in tones for j in i])
# analytical = [scores[i][j] if tones[i][j] == 'Analytical' else 0 for i in range(len(tones)) for j in
#               range(len(tones[i]))]
# Confident = [scores[i][j] if tones[i][j] == 'Confident' else 0 for i in range(len(tones)) for j in
#              range(len(tones[i]))]
Joy = [scores[i][tones[i].index('Joy')] if 'Joy' in tones[i] else 0 for i in range(len(tones))]
Sadness = [scores[i][j] if tones[i][j] == 'Sadness' else 0 for i in range(len(tones)) for j in
           range(len(tones[i]))]
Tentative = [scores[i][j] if tones[i][j] == 'Tentative' else 0 for i in range(len(tones)) for j in
             range(len(tones[i]))]
Anger = [scores[i][j] if tones[i][j] == 'Anger' else 0 for i in range(len(tones)) for j in
             range(len(tones[i]))]
Fear = [scores[i][j] if tones[i][j] == 'Fear' else 0 for i in range(len(tones)) for j in
             range(len(tones[i]))]


df_tone = pd.DataFrame({'Hotel_name': list(df['name']), 'analytical': analytical,
                        'Confident': Confident, 'Joy': Joy,
                            'Sadness': Sadness, 'Tentative': Tentative,'Anger':Anger,'Fear':Fear})

pass
