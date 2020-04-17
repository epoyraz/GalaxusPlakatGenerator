import os
import requests
import random
import numpy
import re
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
    data = getData(link)
    imglink = data["imglink"]
    brand = data["brand"]
    name = re.match(r"(.*)(\(.*\))",data["name"]).group(1) if "(" in data["name"] else data["name"]
    price = data["price"].strip()
    color = random_color()
    newImage = generateImage(color, price, brand, name, spruch, imglink)
    return serve_pil_image(newImage)

def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg')

def random_color():
    color = list(numpy.random.choice(range(256), size=3))
    return tuple(color)

def generateImage(color, price, brand, name, spruch, url):
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    response = requests.get(url, headers={'user-agent': user_agent,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br'
        })
    background = Image.open("template.jpg")
    img = fitSize(Image.open(BytesIO(response.content)))
    draw = ImageDraw.Draw(background)  
    fontSlogan = ImageFont.truetype("Gibson-Regular.ttf", 150)
    fontInner = ImageFont.truetype("Gibson-Regular.ttf", 30)
    fontBrand = ImageFont.truetype("Gibson-Bold.ttf", 30)
    img_w, img_h = img.size
    bg_w, bg_h = background.size
    img_ratio = img.size[0] / float(img.size[1])
    offset = ((bg_w - img_w) // 2, ((bg_h - img_h) // 2)+80)
    background.paste(img, offset)
    if img_ratio < 1:
        draw.text((100, 0), "Galaxus für", (0, 0, 0), font=fontSlogan)
        draw.text((100,150), fitText(spruch), (0,0,0), font=fontSlogan)
        draw.text((700,500), price, (0,0,0), font=fontInner)
        draw.text((700,530), brand, color, font=fontBrand)
        draw.text((700,560), name, color, font=fontInner)
    else:
        draw.text((100, 0), "Galaxus für", (0, 0, 0), font=fontSlogan)
        draw.text((100,150),  fitText(spruch), (0,0,0), font=fontSlogan)
        draw.text((400,1100), price, (0,0,0), font=fontInner)
        draw.text((400,1130), brand, color, font=fontBrand)
        draw.text((400,1160), name, color, font=fontInner)
    return background

def fitText(spruch):
    if len(spruch) > 13:
        newText = spruch[0:13] + "\n" + spruch[12:]
    else:
        newText = spruch
    return newText

def fitSize(pil_img):
    img_ratio = pil_img.size[0]/ float(pil_img.size[1])
    if img_ratio < 1:
        baseheight = 600
        wpercent = baseheight/pil_img.size[1]
        width= int((float(pil_img.size[0])*float(wpercent)))
        pil_img = pil_img.resize((width,baseheight), Image.ANTIALIAS)
    else:
        basewidth = 500
        wpercent = basewidth/pil_img.size[0]
        height = int((float(pil_img.size[1])*float(wpercent)))
        pil_img = pil_img.resize((basewidth,height), Image.ANTIALIAS)
    return pil_img

def getProductName(productNameAndBrand):
    return productNameAndBrand.find('span').text

def getBrand(productNameAndBrand):
    return productNameAndBrand.find('strong').text

def getProductNameAndBrand(html):
        pageContent = html.find('main', attrs={'id': 'pageContent'})
        productNameAndBrand = pageContent.find('h1', attrs={'class': 'productName'})
        return productNameAndBrand

def getData(url):
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
        response = requests.get(url, headers={'user-agent': user_agent,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br'
        })

        result = {}
        content = response.content
        soup = BeautifulSoup(content, "html.parser")
        nameAndBrand = getProductNameAndBrand(soup)
        brand = getBrand(nameAndBrand)
        name = getProductName(nameAndBrand)
        price = soup.find('div', attrs={'class': 'productDetail'}).find('strong').text
        imageContainer = soup.find('picture', attrs={'class':'mediaPicture'})
        imageLink = imageContainer.find('img')
        imageLink = imageLink["src"].split("?")
        result["imglink"] = imageLink[0]
        result["name"] = name
        result["price"] = price
        result["brand"] = brand

        return result

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="80")