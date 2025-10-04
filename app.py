from flask import Flask, render_template, request
import sqlite3
import difflib

app = Flask(__name__)
DB_NAME = "dictionary.db"

# -----------------------------
# Database Initialization
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create table if it doesn’t exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS words (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT UNIQUE NOT NULL,
        meaning TEXT NOT NULL,
        synonyms TEXT,
        antonyms TEXT,
        related TEXT
    )
    """)

    # Insert sample data
    sample_data = [
        ("happy", "Feeling or showing pleasure or contentment.",
        "joyful, cheerful, content",
        "sad, unhappy, miserable",
        "smile, laughter, positivity"),
        
        ("sad", "Feeling or showing sorrow; unhappy.",
        "unhappy, sorrowful, melancholy",
        "happy, joyful, cheerful",
        "cry, tears, depression"),
        
        ("fast", "Moving or capable of moving at high speed.",
        "quick, rapid, swift",
        "slow, sluggish, lethargic",
        "speed, race, velocity"),
        
        ("strong", "Having the power to move heavy weights or perform physically demanding tasks.",
        "powerful, sturdy, muscular",
        "weak, frail, feeble",
        "strength, endurance, resilience"),
        
        ("bright", "Giving out or reflecting a lot of light; intelligent.",
        "shiny, radiant, intelligent",
        "dull, dim, dark",
        "light, clever, brilliance"),
        
        ("calm", "Not showing or feeling nervousness, anger, or strong emotions.",
        "peaceful, composed, relaxed",
        "agitated, nervous, restless",
        "tranquil, serenity, patience"),
        
        ("brave", "Ready to face and endure danger or pain; showing courage.",
        "courageous, valiant, fearless",
        "cowardly, fearful, timid",
        "hero, bold, daring"),
        
        ("angry", "Feeling or showing strong annoyance, displeasure, or hostility.",
        "mad, furious, irate",
        "calm, happy, pleased",
        "rage, temper, frustration"),
        
        ("smart", "Having or showing a quick-witted intelligence.",
        "intelligent, clever, bright",
        "stupid, foolish, dull",
        "brainy, sharp, genius"),
        
        ("slow", "Moving or operating at a low speed.",
        "sluggish, unhurried, lazy",
        "fast, quick, rapid",
        "delay, gradual, crawl")
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO words (word, meaning, synonyms, antonyms, related)
    VALUES (?, ?, ?, ?, ?)
    """, sample_data)

    conn.commit()
    conn.close()


# -----------------------------
# Database Helper Functions
# -----------------------------
def query_word(word):
    """Fetch a word's details from DB"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM words WHERE word = ?", (word,))
    row = cursor.fetchone()
    conn.close()

    if row:
        # Convert to dict and split synonyms/antonyms/related into lists
        return {
            "word": row["word"],
            "meaning": row["meaning"],
            "synonyms": row["synonyms"].split(", "),
            "antonyms": row["antonyms"].split(", "),
            "related": row["related"].split(", ")
        }
    return None


def get_all_words():
    """Fetch all words from DB (for suggestions)"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM words")
    words = [row[0] for row in cursor.fetchall()]
    conn.close()
    return words


# -----------------------------
# Flask Routes
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    suggestion = None

    if request.method == "POST":
        word = request.form.get("word", "").lower().strip()
        if word:
            result = query_word(word)

            # Suggest closest match if word not found
            if not result:
                all_words = get_all_words()
                close_matches = difflib.get_close_matches(word, all_words, n=1, cutoff=0.6)
                if close_matches:
                    suggestion = close_matches[0]

    return render_template("index.html", result=result, suggestion=suggestion)


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    init_db()  # Initialize DB before running
    print("Database ready! Visit http://127.0.0.1:5000/")
    app.run(debug=True)
