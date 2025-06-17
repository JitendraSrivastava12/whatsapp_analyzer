import zipfile
import os
import re
import pandas as pd

def get_data(zip_path=None, txt_file=None, output_dir='unzipped_chat'):
    if zip_path:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        chat_file = next(
            (os.path.join(output_dir, f) for f in os.listdir(output_dir) if f.endswith('.txt')),
            None
        )
        if not chat_file:
            raise FileNotFoundError("No .txt file found in ZIP archive!")

        with open(chat_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

    elif txt_file:
        lines = txt_file.read().decode('utf-8').splitlines()

    else:
        raise ValueError("Provide either a zip_path or txt_file.")

    df = preprocess(lines)
    return modify(df)

def preprocess(data):
    # Join lines in case messages span multiple lines
    text = ''.join(data)

    # Pattern for WhatsApp messages (24-hour format)
    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - (.*?): (.*?)(?=\n\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2} - |$)'
    matches = re.findall(pattern, text, re.DOTALL)

    df = pd.DataFrame(matches, columns=['Date', 'Time', 'Sender', 'Message'])
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    df['Message'] = df['Message'].str.strip()

    return df

def modify(df):
    system_keywords = ['added', 'removed', 'changed', 'created', 'pinned', 'left', 'deleted', 'joined']

    df_cleaned = df[
        (~df['Sender'].str.lower().str.contains('|'.join(system_keywords))) &
        (~df['Sender'].str.contains('~')) &
        (~df['Sender'].str.contains('changed their phone number')) &
        (~df['Sender'].str.contains('this group'))
    ].copy()


    df_cleaned.reset_index(drop=True, inplace=True)
    df_cleaned['month'] = df_cleaned['Date'].dt.month_name()
    df_cleaned['day'] = df_cleaned['Date'].dt.day
    df_cleaned['Time'] = pd.to_datetime(df_cleaned['Time'], format='%H:%M')
    df_cleaned['Hour'] = df_cleaned['Time'].dt.hour
    df_cleaned['Minute'] = df_cleaned['Time'].dt.minute
    df_cleaned['month_num'] = df_cleaned['Date'].dt.month
    df_cleaned['year'] = df_cleaned['Date'].dt.year
    df_cleaned['Weekday'] = df_cleaned['Date'].dt.day_name()

    return df_cleaned

# Example usage
if __name__ == "__main__":
    df = get_data()
    print("📬 Messages Loaded:", len(df))
    print("👥 Participants:", df['Sender'].nunique())
    print(df.head())