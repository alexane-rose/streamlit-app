import pandas as pd
import numpy as np
from datetime import date,  timedelta
from dateutil.relativedelta import relativedelta
import random


today = date.today()
last_year = today + relativedelta(months=-12)
df = pd.DataFrame(np.arange(last_year, today, timedelta(weeks=1)), columns=['week'])

samples = len(df['week'])

df ['usage_A'] = np.random.randint(40,85, size=samples)
df ['usage_B'] = np.random.randint(30,68, size=samples)

df ['available_A'] = np.random.randint(90,100, size=samples)
df ['available_B'] = np.random.randint(90,125, size=samples)


df.to_csv('data/input_data.csv')
