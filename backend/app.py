import os
import requests
from flask import Flask
from flask import request
from flask import send_file
from flask import redirect
from flask_cors import CORS, cross_origin
from bs4 import BeautifulSoup
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO, StringIO

app = Flask(__name__)
CORS(app)

# localhost:5000/generate?spruch=Hello&link=https%3A%2F%2Fwww.galaxus.ch%2Fde%2Fs1%2Fproduct%2Fsony-playstation-4-slim-500gb-de-fr-it-en-spielkonsole-5895212

@app.route("/")
def entry():
    return redirect("/generate?spruch=Hello&link=https%3A%2F%2Fwww.galaxus.ch%2Fde%2Fs1%2Fproduct%2Fsony-playstation-4-slim-500gb-de-fr-it-en-spielkonsole-5895212")

@app.route("/generate")
@cross_origin()
def hello():
    spruch = request.args.get('spruch')
    link = request.args.get('link')
    response = "Hallo, das ist mein Spruch: <br> Galaxus für " + spruch + "<br>"
    response = response + "Und das ist mein Link : " + link
    data = getData(link)
    name = data["name"]
    brand = data["brand"]
    price = data["price"]
    imglink = data["imglink"]
    newImage = generateImage(spruch, imglink)
    print(newImage)
    response = response + "<br>" + name + "<br>" + brand + "<br>" + price + "<br>"
    return serve_pil_image(newImage)


@app.route("/image")
def image():
    filename = 'stereo.jpeg'
    return send_file(filename, mimetype='image/jpeg')

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

def generateImage(spruch, url):
    response = requests.get(url)
    background = Image.open("template.jpg")
    img = Image.open(BytesIO(response.content))
    basewidth = 500
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    draw = ImageDraw.Draw(background)
    font = ImageFont.truetype("Gibson-Regular.ttf", 150)
    background.paste(img, (300, 600))
    draw.text((100, 100), "Galaxus für", (0, 0, 0), font=font)
    draw.text((100,250), spruch, (0,0,0), font=font)
    return background

def getData(url):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        response = requests.get(url, headers={'user-agent': user_agent,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br'
        })

        result = {}
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        html = soup.find('div', attrs={'class': 'productDetail ZZcb'})
        productDetails = html.find('h1', attrs={'class': 'productName ZZcs'})
        brand = productDetails.find('strong').text
        name = productDetails.find('span').text
        price = html.find('strong', attrs={'class': 'ZZbe'}).text.strip()
        imageContainer = soup.find('picture', attrs={'class':'mediaPicture Z19y'})
        imageLink = imageContainer.find('img')
        imageLink = imageLink["src"].split("?")
        result["imglink"] = imageLink[0]
        result["name"] = name
        result["price"] = price
        result["brand"] = brand

        return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="80")