import flask
from flask import Flask,request,render_template
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import logging
import pymongo
import os
logging.basicConfig(filename="imagescrap.log",level=logging.INFO)

app=Flask(__name__)

@app.route("/",methods=['POST',"GET"])
def homepage():
    return render_template("index.html")

@app.route("/review",methods=["POST","GET"])
def index():
    if request.method == "POST":
        logging.info("get successfull request")
        try:
            query= request.form['content'].replace(" ","")
            logging.info("query get")
            save_dir="images/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            logging.info("success1")
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
            response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")
            logging.info("success2")
            soup=bs(response.content,"html.parser")
            img_links=soup.find_all("img")
            logging.info("success3")    
            del img_links[0]
            img_data=[]
            for index,image_tag in enumerate(img_links):
                # get the image source URL
                image_url = image_tag['src']
                #print(image_url)
                
                # send a request to the image URL and save the image
                image_data = requests.get(image_url).content
                mydict={"Index":index,"Image":image_data}
                img_data.append(mydict)
                with open(os.path.join(save_dir, f"{query}_{img_links.index(image_tag)}.jpg"), "wb") as f:
                    f.write(image_data)

        
            client = pymongo.MongoClient("mongodb+srv://08Pratik:08Pratik@cluster0.vd8ss6z.mongodb.net/?retryWrites=true&w=majority")
            db = client['image_scraper']
            mycoll=db['scrapped_images']
            mycoll.insert_many(img_data)

            return "image loaded successfully."

        except Exception as e:
            logging.info(e)
            return e,"something went wrong."
    else :
        return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8000)