from flask import Flask, request, render_template
import nltk
from nltk.tokenize import word_tokenize
from rdflib import Graph, Namespace

app = Flask(__name__)

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

g = Graph()
g.parse("faqs.ttl", format="ttl")

faq_ns = Namespace("http://example.org/faq#")

def find_answer(user_query):
    query_tokens = word_tokenize(user_query.lower())
    answers = []

    for token in query_tokens:
        query = f"""
        PREFIX faq: <http://example.org/faq#>
        SELECT ?answer
        WHERE {{
            ?faq a faq:FAQ .
            ?faq faq:hasQuestion ?question .
            ?faq faq:hasAnswer ?answer .
            FILTER(CONTAINS(LCASE(?question), "{token}"))
        }}
        """
        for row in g.query(query):
            answers.append(row.answer)

    if answers:
        return answers[0]  # Return the first matching answer
    return "I'm sorry, I don't have an answer for that."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.form['query']
    answer = find_answer(user_query)
    return render_template('index.html', user_query=user_query, answer=answer)

if __name__ == '__main__':
    app.run(debug=True)

