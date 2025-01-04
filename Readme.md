# STIR Assignment 01/2024 - Twitter Top Trending Scrapper

**Working Video Demo and Explanation Link :-**

> This repository is for submission of the assignment given by STIR as a part of Internship selection process.
> Please read the instructions below to use the tool.

## Environment Variables

`.env` file structure is provided below


> Note: The provided twitter credentials are of a dummy disposable account so you can use it as is.
> Kindly update the `PROXY_MESH_USERNAME` and `PROXY_MESH_PORT` variables with your own
> `TWITTER_USERNAME` environment variable is used to bypass the Phone/Username verification challenge presented by Twitter

```txt
TWITTER_EMAIL=johntester@yopmail.com
TWITTER_USERNAME=tester_johnstir
TWITTER_PASSWORD=JohnTester@81
PROXY_MESH_HOSTNAME=<PROXY_MESH_USERNAME>
PROXY_MESH_PORT=<PROXY_MESH_PORT>
CHROME_PROFILE_DIR=Default
CHROME_USER_DATA_DIR=C:\Users\gauta\AppData\Local\Google\Chrome\User Data
MONGO_URI=mongodb://localhost:27017/twitterTrending
```

## **Requirements**

* Chrome Web Browser
* Python 3.x
* MongoDB

## Steps to use the program?

1. Clone the repo using `git clone https://gautamgiri-dev/twitter-trending-scraper-stir`
2. Navigate to local cloned directory and create a virtual env (if you like) then install required libraries `pip install -r requirements.txt`
3. Run `python app.py` to run the application
4. You can use the application at `http://localhost:5000`
5. To use local Chrome Profile you must update the `CHROME_*` environment variables. I have kept the my system's values for example
6. To use proxy feature you must whitelist your current ip address from **ProxyMesh** dashboard
7. Ensure that `MONGO_URI` correctly refers to your instance of MongoDB server you want to use and update it's value accordingly