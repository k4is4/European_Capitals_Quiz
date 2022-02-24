from flask_pymongo import PyMongo

def get_flashcards(db):
    """Get countries and capitals from the database and return them in a dictionary."""
    flashcards = {}
    for document in db.Flashcards.find({}):
        flashcards[document["country"]] = document["capital"]
    return flashcards

def check_highscore(score, app):
    """Get high scores from the database and check if a high score was made."""
    scores = get_highscores(app)
    if score > scores[0][1]:
        return True
    return False

def save_highscore(name, score, app):
    """Insert a new high score and delete the lowest score from the database."""
    mongo = PyMongo(app)
    db = mongo.db
    db.Highscore.insert_one({"name":name, "score":score})
    scores = get_highscores(app)
    min_score = scores[0][1]
    db.Highscore.delete_one({"score":min_score})
    

def get_highscores(app):
    """Get high scores from the database and return them in a sorted list of tuples."""
    mongo = PyMongo(app)
    db = mongo.db
    scores = []
    for document in db.Highscore.find({}):
        scores.append((document["name"], int(document["score"])))
        scores.sort(key=lambda x:x[1])
    return scores