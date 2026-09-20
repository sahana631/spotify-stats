from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from main import SpotifyStats
import auth
import time
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or os.urandom(24)


@app.route("/")
def index():
    if "access_token" not in session:
        return render_template("login.html")
    return render_template("index.html")


@app.route("/login")
def login():
    return redirect(auth.build_auth_url())


@app.route("/callback")
def callback():
    code = request.args.get("code")
    error = request.args.get("error")

    if error or not code:
        return f"Login failed: {error}", 400

    token_data, status = auth.exchange_code_for_token(code)

    if status != 200:
        return f"Token exchange failed: {token_data}", 400

    session["access_token"] = token_data.get("access_token")
    session["refresh_token"] = token_data.get("refresh_token")
    session["expires_at"] = time.time() + token_data.get("expires_in", 3600)

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def get_valid_token():
    if "access_token" not in session:
        return None

    if time.time() >= session.get("expires_at", 0):
        refresh = session.get("refresh_token")
        if not refresh:
            return None

        token_data, status = auth.refresh_token(refresh)
        if status != 200:
            session.clear()
            return None

        session["access_token"] = token_data.get("access_token")
        session["expires_at"] = time.time() + token_data.get("expires_in", 3600)
        if "refresh_token" in token_data:
            session["refresh_token"] = token_data["refresh_token"]

    return session["access_token"]


@app.route("/api/data")
def data():
    token = get_valid_token()
    if token is None:
        return jsonify({"error": "Not logged in"}), 401

    stats = SpotifyStats(token)
    category = request.args.get("category", "tracks")
    time_range = request.args.get("time_range", "medium_term")
    limit = int(request.args.get("limit", 20))

    if category == "tracks":
        result = stats.get_tracks(time_range=time_range, limit=limit)
    elif category == "artists":
        result = stats.get_artists(time_range=time_range, limit=limit)
    elif category == "albums":
        result = stats.get_albums(time_range=time_range, limit=limit)
    else:
        result = []

    return jsonify(result)


@app.route("/api/taste-change")
def taste_change():
    token = get_valid_token()
    if token is None:
        return jsonify({"error": "Not logged in"}), 401

    stats = SpotifyStats(token)
    category = request.args.get("category", "tracks")

    if category == "artists":
        result = stats.get_artist_taste_change()
    elif category == "albums":
        result = stats.get_album_taste_change()
    else:
        result = stats.get_taste_change()

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5050)