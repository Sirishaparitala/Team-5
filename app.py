"""Flask API entry point for the Sports Quiz Generator."""

from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from services.quiz_service import generate_sports_quiz

# Validate configuration on startup
Config.validate()

app = Flask(__name__)
CORS(app)


@app.route("/sports", methods=["GET"])
def get_sports():
    """Return the list of supported sports."""
    return jsonify({"sports": Config.SPORTS})


@app.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    """
    Generate a new sports quiz.

    Expects JSON body: { "sport": "cricket", "difficulty": "medium" }
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    sport = data.get("sport", "").lower().strip()
    difficulty = data.get("difficulty", "").lower().strip()

    # Validate sport
    valid_sport_ids = [s["id"] for s in Config.SPORTS]
    if sport not in valid_sport_ids:
        return jsonify({
            "error": f"Invalid sport '{sport}'. Valid options: {valid_sport_ids}"
        }), 400

    # Validate difficulty
    if difficulty not in Config.DIFFICULTIES:
        return jsonify({
            "error": f"Invalid difficulty '{difficulty}'. Valid options: {Config.DIFFICULTIES}"
        }), 400

    try:
        quiz = generate_sports_quiz(sport, difficulty)
        return jsonify(quiz)
    except Exception as e:
        print(f"[API] Error generating quiz: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/regenerate", methods=["POST"])
def regenerate_quiz():
    """
    Regenerate a quiz with the same parameters but fresh questions.

    Same payload as /generate-quiz. Performs a new web search
    to pull different content and generates new questions.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    sport = data.get("sport", "").lower().strip()
    difficulty = data.get("difficulty", "").lower().strip()

    valid_sport_ids = [s["id"] for s in Config.SPORTS]
    if sport not in valid_sport_ids:
        return jsonify({
            "error": f"Invalid sport '{sport}'. Valid options: {valid_sport_ids}"
        }), 400

    if difficulty not in Config.DIFFICULTIES:
        return jsonify({
            "error": f"Invalid difficulty '{difficulty}'. Valid options: {Config.DIFFICULTIES}"
        }), 400

    try:
        quiz = generate_sports_quiz(sport, difficulty)
        quiz["regenerated"] = True
        return jsonify(quiz)
    except Exception as e:
        print(f"[API] Error regenerating quiz: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("\nSports Quiz Generator API")
    print("=" * 40)
    print(f"  Sports: {[s['name'] for s in Config.SPORTS]}")
    print(f"  Difficulties: {Config.DIFFICULTIES}")
    print("=" * 40)
    app.run(debug=True, port=5000)
