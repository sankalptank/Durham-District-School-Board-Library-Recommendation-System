import requests
import csv

# gets book genres from openbooks api

def get_book_genre(title, timeout=10):
    url = f'https://openlibrary.org/search.json'
    
    params = {
        'title': title
    }
    
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()  # raise HTTPError if request unsuccessful
        data = response.json()
        
        if 'docs' not in data or len(data['docs']) == 0:
            return None
        
        book = data['docs'][0]
        
        if 'subject' in book:
            genres = book['subject']
            return genres
        
        return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")
        return None

with open('onlygenres.csv', encoding="utf8", mode='r') as file:
    csv_reader = csv.reader(file)

    with open('genre file.txt', 'w', encoding="utf8") as genre_file:
        try:
            for lines in csv_reader:
                book_title = str(lines[2])
                genre = get_book_genre(book_title)
                if genre:
                    genre_info = ', '.join(genre)
                else:
                    genre_info = 'n/a'
                
                genre_file.write(f"\"{genre_info}\" \n")
        
        except Exception as e:
            print(f"error: {e}")
        finally:
            print("done")
            genre_file.close()



while True:
    pass
