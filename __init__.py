from flask import Flask, render_template
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev")

@app.route("/")
def index():
    return render_template(
        "index.html",
        pubnub_publish_key=os.environ.get("PUBNUB_PUBLISH_KEY"),
        pubnub_subscribe_key=os.environ.get("PUBNUB_SUBSCRIBE_KEY")
    )
