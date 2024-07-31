#!/usr/bin/env python3
import pandas as pd
from bs4 import BeautifulSoup
import argparse
from deep_translator import GoogleTranslator

def parse_args():
    parser = argparse.ArgumentParser(description='Create a dataset from HTML.')
    parser.add_argument('-f', '--file', help='Path to the HTML file', required=True, type=str)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    filename = args.file

    try:
        # Read the HTML file
        with open(filename, 'r') as file:
            data = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        exit(1)

    try:
        # Parse the HTML content
        soup = BeautifulSoup(data, 'html.parser')
        sections = soup.find_all('font', face=['arial', 'helvetica'])
        data_list = []

        for section in sections:
            timestamp = section.text.strip()
            ip_tag = section.find_next('i')
            ip = ip_tag.text.strip().split()[-1] if ip_tag else 'N/A'

            # Extract table data
            table = section.find_next('table')
            if not table:
                continue
            
            table_rows = table.find_all('tr')
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

        # Create DataFrame and process data
        df = pd.DataFrame(data_list)
        if 'Comments' in df.columns:
            cdf = df[df['Comments'] != ''].reset_index(drop=True)
            filter_df = cdf[
                cdf['Comments'].str.contains(' ', na=False) & 
                (cdf['Comments'].str.len() >= 3) & 
                (cdf['Comments'].str.len() <= 2000)
            ]
            filter_df['trans'] = filter_df['Comments'].apply(
                lambda x: GoogleTranslator(source='auto', target='en').translate(x)
            )

            # Save to CSV
            output_file = f'{filename}.csv'
            filter_df.to_csv(output_file, index=False)
            print(f"CSV file saved as {output_file}")
        else:
            print("The 'Comments' column is missing in the parsed data.")

    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
