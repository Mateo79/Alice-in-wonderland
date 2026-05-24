# Bookworm — NLP Book Card Engine

Bookworm is a lightweight CLI tool built for the **Through the Looking-Glass** startup prototype.
It fetches books from [Project Gutenberg](https://www.gutenberg.org/) and runs a full NLP pipeline on them to generate structured **book cards** — compact metadata sheets that give editors and publishers a quick overview of any book without reading it entirely.

The tool covers: lexical analysis, topic modeling, named entity recognition, summarization, and book similarity ranking. Expensive operations are automatically cached to avoid redundant computation.

---

## Commands

### --lexdiv \<ID\>
Computes vocabulary richness metrics for a book: total tokens, unique types, hapax legomena, type-token ratio, mean word length, and mean word frequency.

```bash
python bookworm.py --lexdiv 11
```

### --topics \<ID\>
Extracts the main themes from each section of a book as a list of top 10 keywords per topic.

```bash
python bookworm.py --topics 11
```

### --entities \<ID\>
Identifies characters and locations mentioned throughout the book using Named Entity Recognition.

```bash
python bookworm.py --entities 11
```

### --summarize \<ID\>
Condenses the book into a few sentences using an extractive summarization approach.

```bash
python bookworm.py --summarize 11
```

### --similar \<ID\>
Returns the 5 most similar books from the catalog, ranked by decreasing similarity using TF-IDF and cosine similarity.

```bash
python bookworm.py --similar 11
```

### --card \<ID\>
Aggregates all of the above into a single structured book card dictionary.

```bash
python bookworm.py --card 11
```

---

## Installation

**Prerequisites:** Python 3.12+

Clone the repository and set up a virtual environment:

```bash
git clone <your-repo-url>
cd Alice_in_borderland

python -m venv .venv
source .venv/bin/activate      # Linux / macOS
.venv\Scripts\activate         # Windows

pip install -r requirements.txt
```

---

## Usage Examples

Get the lexical diversity metrics for *Alice's Adventures in Wonderland* (ID 11):
```bash
python bookworm.py --lexdiv 11
```

Find the 5 books most similar to *Dracula* (ID 345):
```bash
python bookworm.py --similar 345
```

Generate a full book card for *Frankenstein* (ID 84):
```bash
python bookworm.py --card 84
```

Launch the interactive Streamlit frontend:
```bash
streamlit run streamlit.py
```

---
