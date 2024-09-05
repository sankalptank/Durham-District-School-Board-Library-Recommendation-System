import csv
import sys
from numpy import dot
from numpy.linalg import norm

# recommends books

genre_weights = {}

with open('genre_counts.csv', encoding="utf8", mode='r') as file:
    csv_reader = csv.reader(file)
    next(csv_reader)  # skip header
    for row in csv_reader:
        genre, count, weight = row[0], int(row[1]), float(row[2])
        genre_weights[genre] = weight  # store genre weights

def cosine_similarity(X, Y, weight, weight2):
    # weight vectors
    x_weighted = X.copy()
    y_weighted = Y.copy()

    # increase the weight of the genres (genres matter more)
    x_weighted[0] *= weight
    y_weighted[0] *= weight2

    # cosine similarity calculation
    cos_sim = dot(x_weighted, y_weighted) / (norm(x_weighted) * norm(y_weighted))
    return cos_sim

with open('onlygenres.csv', encoding="utf8", mode='r') as file:
    csv_reader = csv.reader(file)
    books = list(csv_reader)

def book_search(index):
    output = []
    stop_words = {"a", "an", "the", "and", "or", "but", "on", "in", "with", "of", "for", "by", "to", ":", "/", "is", "about", "-", "book"}
    title_list = [word for word in books[index][2].lower().split(' ') if word not in stop_words]
    title_count = len(title_list)
    genre_list = books[index][8].split(',')
    genre_count = 0
    for genre in genre_list:
        genre_count += genre_weights[genre]
    books.pop(index)  # remove book being inputted

    results = []

    for book in books:
        compare_genre_list = book[8].split(',')
        overlap_genres = set(genre_list) & set(compare_genre_list)
        overlap_genres_count = 0
        for genre in overlap_genres:
            overlap_genres_count += genre_weights[genre]
        compare_title_list = book[2].lower().split(' ')
        overlap_title = set(title_list) & set(compare_title_list)
        if len(overlap_genres) > 1:
            similarity = cosine_similarity([genre_count, title_count, 1], [overlap_genres_count, len(overlap_title), 1], 0.75, 0.25)
            if similarity > 0:
                results.append((similarity, book[2], overlap_genres, len(overlap_title), book[3]))

    # sort results by similarity in descending order and get the top 10
    results.sort(reverse=True, key=lambda x: x[0])
    top_results = results[:10]

    # format output
    output = []
    for similarity, title, genres, title_overlap, author in top_results:
        output_line = f'{title} by {author} {genres}'+'\n'
        output.append(output_line)

    # output the results to stdout (gui.py)
    for line in output:
        print(line)

# gui.py stuff, takes in book index from gui, inputs it into this file
if __name__ == "__main__":
    if len(sys.argv) > 1:
        index = int(sys.argv[1])+1
        print(book_search(index))
