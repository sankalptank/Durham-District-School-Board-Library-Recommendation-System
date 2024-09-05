import tkinter as tk
from tkinter import ttk
import pandas as pd
import subprocess

#gui for cosine (book recommendation)

# csv file of all books, genres, authors
df = pd.read_csv('onlygenres.csv')

class BookSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Find Similar Books")

        # layout
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # search entry and label (right_frame)
        self.search_var = tk.StringVar()
        self.search_label = ttk.Label(self.right_frame, text="Search for Books", font=('Arial', 14))
        self.search_label.pack(padx=20, pady=(20, 10))  # Added padding to position label

        self.search_entry = ttk.Entry(self.right_frame, textvariable=self.search_var, font=('Arial', 14))
        self.search_entry.pack(padx=20, pady=(0, 20), fill=tk.X)  # Adjusted padding

        # search results label
        self.results_label = ttk.Label(self.left_frame, text="Books in Library", font=('Arial', 14))
        self.results_label.pack(padx=20, pady=10)

        # listbox for search suggestions
        self.suggestion_listbox = tk.Listbox(self.left_frame, font=('Arial', 12))
        self.suggestion_listbox.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        self.suggestion_listbox.bind('<<ListboxSelect>>', self.on_suggestion_select)

        # recommended books label
        self.recommendations_label = ttk.Label(self.right_frame, text="Recommended Books", font=('Arial', 14))
        self.recommendations_label.pack(padx=20, pady=10)

        # text area for ouput of cosine.py
        self.output_text = tk.Text(self.right_frame, font=('Arial', 12))
        self.output_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # bind the search entry to update suggestions
        self.search_var.trace("w", self.update_suggestions)

    def update_suggestions(self, *args):
        search_term = self.search_var.get().lower()
        self.suggestion_listbox.delete(0, tk.END)
        suggestions = [title for title in df['Title'] if search_term in title.lower()]
        for suggestion in suggestions:
            self.suggestion_listbox.insert(tk.END, suggestion)

    def on_suggestion_select(self, event):
        selected_indices = self.suggestion_listbox.curselection()
        if selected_indices:
            selected_index = selected_indices[0]  # get first selected index
            selected_title = self.suggestion_listbox.get(selected_index)
            index = df[df['Title'] == selected_title].index[0]

            # run cosine.py with the selected index
            result = subprocess.run(['python', 'cosine.py', str(index)], capture_output=True, text=True)

            # display result in output area
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, result.stdout)
        else:
            # if no item selected
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "No book selected. Please select a book from the list.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookSearchApp(root)
    root.mainloop()
