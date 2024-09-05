import pandas as pd
import openai
import csv
import time


openai.api_key = 'api_key'

# csv files for available genres to choose from
genre_counts = pd.read_csv('cleaned_genre_counts.csv')
# csv for all books that don't have genres
filtered_rows = pd.read_csv('filtered_rows.csv')

# make sure all genres are strings
genre_counts['Genre'] = genre_counts['Genre'].astype(str).fillna('')

def generate_genres(title, authors):
    genre_list = ', '.join(genre_counts['Genre'].tolist())
    prompt = f"generate 2-5 relevant genres from the following genre list based on the book titled '{title}' by '{authors}': {genre_list}, format: genre,genre,genre,genre surrounded by quotes. no explanation or no /n or numbers, just genres separated by commas"
    
    while True:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in book genres."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.7,
            )
            genres = response.choices[0].message['content'].strip()
            return genres
        # even when paying, still get rate limited alot. if you retry immediatley the program is slow asf. this just waits 7 seconds, could probably be shorter but this works.
        except openai.error.RateLimitError:
            print("rate limit. retry 7 seconds")
            time.sleep(7)
        # check for errors
        except Exception as e:
            print(f"error: {e}")
            return 'Unknown'  # handles potential other errors

# open output file
with open('output.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #define the csv writer
    fieldnames = ['#', 'Call No', 'Title', 'Authors', 'Barcode', 'Price', 'Status', 'Date Created', 'Genre']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # header
    writer.writeheader()

    # put each chatgpt output into the csv of books without genres
    for index, row in filtered_rows.iterrows():
        if pd.isna(row['Genre']):
            title = row['Title']
            authors = row['Authors']
            generated_genres = generate_genres(title, authors)
            
            # make sure chatgpt outputs are strings
            if isinstance(generated_genres, str):
                filtered_rows.at[index, 'Genre'] = generated_genres
            else:
                filtered_rows.at[index, 'Genre'] = 'Unknown'  # Handle unexpected types

        # write the entire row to the final output csv
        writer.writerow({
            '#': row['#'],
            'Call No': row['Call No'],
            'Title': row['Title'],
            'Authors': row['Authors'],
            'Barcode': row['Barcode'],
            'Price': row['Price'],
            'Status': row['Status'],
            'Date Created': row['Date Created'],
            'Genre': generated_genres
        })

print("done")