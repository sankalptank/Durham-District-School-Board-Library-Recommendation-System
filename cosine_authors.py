import tkinter as tk
import pandas as pd
import csv
from numpy import dot
from numpy.linalg import norm
from collections import Counter

# recommends author, no seperate gui file

genre_weights = {}

with open('genre_counts.csv', encoding="utf8", mode='r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # skips header
    for row in csv_reader:
        genre, count, weight = row[0], int(row[1]), float(row[2])
        genre_weights[genre] = weight  # store weights of genres


# Load the CSV files
df_authors = pd.read_csv('author_genres_summary.csv', encoding="utf8")

# Prepare the DataFrame for recommendations
author_genres = df_authors['Authors'].astype(str).tolist()  # make all authors strings, some authors are empty; cause errors

def cosine_similarity(X, Y, weight):
    x_weighted = X.copy()
    y_weighted = Y.copy()
    x_weighted[0] *= weight
    y_weighted[0] *= weight
    return dot(x_weighted, y_weighted) / (norm(x_weighted) * norm(y_weighted))

def get_author_index(dataframe, author_name):
    matching_indices = dataframe.index[dataframe['Authors'].str.contains(author_name, case=False, na=False)]
    if not matching_indices.empty:
        return dataframe.loc[matching_indices[0]]
    else:
        return None

def author_cosine(data, original_author_name):
    original_genres = data[1].split(',')
    genre_count = len(original_genres)
    counter1 = Counter(original_genres)
    results = []

    for _, author in df_authors.iterrows():
        author_name_normalized = normalize_name(author['Authors'])
        # skip the author being searched for
        if author_name_normalized == normalize_name(original_author_name):
            continue

        # make sure all genres are strings, also make sure it can handle n/a & NaN
        genres = str(author['Genres']) if pd.notna(author['Genres']) else ''
        author_genres_list = genres.split(',')
        total_genres = len(author_genres_list)

        # skip authors with no genres
        if total_genres == 0:
            continue

        # count the genres for the current author
        counter2 = Counter(author_genres_list)
        overlap = list((counter1 & counter2).elements())
        overlap_genres_count = 0

        # get the number for the overlap (the sum of the genres' weights)
        for genre in overlap:
            overlap_genres_count += genre_weights.get(genre, 0)

        # if there is no overlap; skips author
        if overlap_genres_count == 0:
            continue

        # normalize the genre counts and overlap count
        normalized_genre_count = sum(genre_weights.get(genre, 0) for genre in original_genres) / genre_count
        normalized_overlap_count = overlap_genres_count / total_genres

        # calculate similarity
        similarity = cosine_similarity([normalized_genre_count, 0], [normalized_overlap_count, 1], 0.25)
        
        if similarity > 0.10 and int(author['Number Of Books']) > 10:
            results.append((similarity, author['Authors'], author['Number Of Books']))  # Include overlap genres

    # sort results by similarity in descending order
    results.sort(reverse=True, key=lambda x: x[0])
    
    # return the top 10 results excluding the original author
    return results[:10]




def normalize_name(name):
    return name.strip().lower()

def search_author():
    author_name = entry.get()
    if author_name:
        # clear previous search results
        results_text.delete(1.0, tk.END)
        listbox.delete(0, tk.END)
        
        # find the author and calculate similarities
        author_data = get_author_index(df_authors, author_name)
        if author_data is not None:
            results = author_cosine(author_data, author_name)
            for _, author, count in results:
                results_text.insert(tk.END, f"{author}, {count} books in Library\n")
        else:
            results_text.insert(tk.END, "Author not found.")
    else:
        results_text.delete(1.0, tk.END)



def update_recommendations(event):
    query = entry.get().lower()
    recommendations = [author for author in author_genres if query in author.lower()]
    listbox.delete(0, tk.END)
    for rec in recommendations:
        listbox.insert(tk.END, rec)

# tkinter guiS
root = tk.Tk()
root.title("Author Similarity Finder")
root.geometry("2000x1500")  # window size 2.5 times orginal

frame = tk.Frame(root, padx=10, pady=10, bg="#E6E6FA")  # light purple background
frame.pack(fill=tk.BOTH, expand=True)

tk.Label(frame, text="Enter Author Name:", font=("Arial", 18), bg="#E6E6FA").grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)
entry = tk.Entry(frame, width=70, font=("Arial", 18))
entry.grid(row=0, column=1, padx=10, pady=10, sticky=tk.W+tk.E)
entry.bind('<KeyRelease>', update_recommendations)

search_button = tk.Button(frame, text="Find Similar Authors", command=search_author, font=("Arial", 18), bg="#D8BFD8", relief=tk.RAISED)
search_button.grid(row=1, column=0, columnspan=2, pady=20)

results_text = tk.Text(frame, height=15, width=90, font=("Arial", 14))
results_text.grid(row=2, column=0, columnspan=2, pady=20, padx=10, sticky=tk.W+tk.E)

listbox = tk.Listbox(frame, width=70, font=("Arial", 14))
listbox.grid(row=0, column=2, rowspan=3, padx=20, pady=10, sticky=tk.N+tk.S)

# make the window resize kind of nice, lowkey needs some work
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
