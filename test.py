from flask_restful.representations import json
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import ToneAnalyzerV3
import pandas as pd
text = 'Team, I know that times are tough! Product sales have been disappointing for the past three quarters. We have a competitive product, but we need to do a better job of selling it!'

authenticator = IAMAuthenticator('oB3n1wOVx-4CMOjFm-gVVuCdrY5xy9cC_04dW_SZ-R0G')
tone_analyzer = ToneAnalyzerV3(
    version='2019-07-03',
    authenticator=authenticator
)
tone_analyzer.set_service_url('https://gateway-lon.watsonplatform.net/tone-analyzer/api')
tone_analysis = tone_analyzer.tone(
    {'text': text},
    content_type='application/json').get_result()

df = pd.read_csv('data.csv')
df = df[['name', 'reviews.text']]
for i in list(df['reviews.text']):
    pass
