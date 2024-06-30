from flask import Flask, render_template, request, redirect, url_for
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import pandas as pd
import os

app = Flask(__name__)

schema = Schema(title=TEXT(stored=True), description=TEXT(stored=True))

if not os.path.exists("indexdir"):
    os.mkdir("indexdir")
    ix = create_in("indexdir", schema)

    df = pd.read_csv("data/books.csv", encoding="utf8")
    df = df[(df["language"] == "English") & (~df["description"].isna())]

    writer = ix.writer()
    for i in df.index:
        writer.add_document(title = df['title'][i], description = df['description'][i])
    writer.commit()

    del df
else:
    ix = open_dir("indexdir")

def add_book_to_index(title, description):
    writer = ix.writer()
    writer.add_document(title=title, description=description)
    writer.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
    title = request.form['title']
    description = request.form['description']

    add_book_to_index(title, description)

    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = []
    with ix.searcher() as searcher:
        query = QueryParser("description", ix.schema).parse(query)
        result = searcher.search(query)
        for hit in result[:50]:
            results.append({"title": hit["title"], "description": hit["description"]})
    print(results)
    return render_template('index.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)