import requests
from flask import Flask
from flask import request
from flask import send_file
from bs4 import BeautifulSoup

app = Flask(__name__)

# localhost:5000/generate?spruch=Hello&link=https%3A%2F%2Fwww.galaxus.ch%2Fde%2Fs1%2Fproduct%2Fsony-playstation-4-slim-500gb-de-fr-it-en-spielkonsole-5895212

@app.route("/generate")
def hello():
    spruch = request.args.get('spruch')
    link = request.args.get('link')
    response = "Hallo, das ist mein Spruch: <br> Galaxus für " + spruch + "<br>"
    response = response + "Und das ist mein Link : " + link
    data = getData(link)
    name = data["name"]
    brand = data["brand"]
    price = data["price"]
    response = response + "<br>" + name + "<br>" + brand + "<br>" + price + "<br>"
    return response


@app.route("/image")
def image():
    filename = 'stereo.jpeg'
    return send_file(filename, mimetype='image/jpeg')

def getData(url):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        response = requests.get(url, headers={'user-agent': user_agent,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br'
        })


        result = {}
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        html = soup.find('div', href=False, attrs={'class': 'productDetail ZZcb'})
        productDetails = html.find('h1', attrs={'class': 'productName ZZcs'})
        brand = productDetails.find('strong').text
        name = productDetails.find('span').text
        price = html.find('strong', attrs={'class': 'ZZbe'}).text.strip()
        result["name"] = name
        result["price"] = price
        result["brand"] = brand

        return result

if __name__ == "__main__":
    app.run()

