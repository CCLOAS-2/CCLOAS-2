#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import argparse
from deep_translator import GoogleTranslator

def parse_args():
    parser = argparse.ArgumentParser(description='Create a dataset.')
    parser.add_argument('-f', '--file', help='filename', required=True, type=str)
    args = parser.parse_args()
    return(args)

if __name__== "__main__" :
    args = parse_args()

flilie = args.file

with open(flilie, 'r') as file:
    data = file.read()

soup = BeautifulSoup(data, 'html.parser')
sections = soup.find_all('font', face=['arial', 'helvetica'])
data_list = []

for section in sections:
    timestamp = section.text.strip()
    ip = section.find_next('i').text.strip().split()[-1]
    
    # Extract table data
    table_rows = section.find_next('table').find_all('tr')
    table_data = {}

    for row in table_rows:
        columns = row.find_all('td')
        if len(columns) == 2:
            key = columns[0].text.strip()
            value = columns[1].text.strip()
            table_data[key] = value

    # Combine all data into a dictionary
    entry = {
        'Timestamp': timestamp,
        'IP': ip,
        **table_data
    }

    data_list.append(entry)

df = pd.DataFrame(data_list)
cdf = df[df['Comments'] != ''].reset_index()
filter = cdf[cdf['Comments'].str.contains(' ') & (cdf['Comments'].str.len() >= 3) & (cdf['Comments'].str.len() <= 2000)]
filter['trans'] = filter['Comments'].apply(lambda x: GoogleTranslator(source= 'auto', target='en').translate(x))

filter.to_csv(f'{flilie}.csv')
