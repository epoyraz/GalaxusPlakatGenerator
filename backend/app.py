from flask import Flask
from flask import request
from flask import send_file
app = Flask(__name__)

@app.route("/generate")
def hello():
    spruch = request.args.get('spruch')
    link = request.args.get('link')
    response = "Hallo, das ist mein Spruch: <br> Galaxus für " + spruch + "<br>"
    response = response + "Und das ist mein Link : " + link
    return response


@app.route("/image")
def image():
    filename = 'stereo.jpeg'
    return send_file(filename, mimetype='image/jpeg')

if __name__ == "__main__":
    app.run()