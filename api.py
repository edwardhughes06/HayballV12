from flask import Flask, render_template, session, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
import requests
import json
import xmltodict
import random
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access variables
api_key = os.getenv("API_KEY")
secret_key = os.getenv("SECRET_KEY")



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
db = SQLAlchemy(app)
api = Api(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f"User(name = {self.name}, email = {self.email})"

user_args = reqparse.RequestParser()
user_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
user_args.add_argument('email', type=str, required=True, help="Email cannot be blank")

userFields = {
    'id':fields.Integer,
    'name':fields.String,
    'email':fields.String,
}

class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all()
        return users
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(name=args["name"],email=args["email"])
        db.session.add(user)
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "User not found")
        return user    
    
    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "User not found")
        user.name = args["name"]
        user.email = args["email"]
        db.session.commit()
        return user 
       
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first()
        if not user:
            abort(404, "User not found")
        db.session.delete(user)
        db.session.commit()
        user = UserModel.query.all()
        return user, 200
    

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

@app.route('/finance_products', methods=['GET', 'POST'])
def get_finance_products():
    product_details = [["Interest Free Finance (6 Months)",27,"244b3e7a-0ffb-41f2-88d5-adf78b6a3d9e"],["Interest Free Finance (10 Months)",88,"34ee414c-94d8-4cd2-8f62-fc5b8a2d2a7d"],["Interest Free Finance (12 Months)",28,"8e0bd3a9-657f-457c-b488-dbfab37fac39	"],["Interest Free Finance (18 Months)",46,"c3114266-125a-4ea1-ab10-cfb3ebd48b81"],["Interest Free Finance (24 Months)",29,"9d6fa148-eeb2-4345-b5c6-961902a8f0eb"],["Interest Free Finance (36 Months)",30,"e931ab43-b8ae-431d-ac50-812d413fb5bb"],["Interest Free Finance (36 Months)",30,"e931ab43-b8ae-431d-ac50-812d413fb5bb"],["Classic Credit 12 months 4.9%",146,"aeda558e-5406-4cf3-b05c-39eb57b19e37"],["Classic Credit 18 months 4.9%",147,"5fdc06bb-ed0b-4365-9eca-3b4c6c489dd6"],["Classic Credit 24 Months 4.9%",118,"b30bdb3c-deca-460f-9a49-6f67642da395"],["Classic Credit 36 Months 4.9%",119,"e35912b4-cb1b-40ef-a4f9-2e14b60901d4"],["Classic Credit 12 months 9.9%",162,"46aff7e0-910c-4f4d-8d36-4bc3e2a84dad"],["Classic Credit 24 Months 9.9%",54,"152fea32-be31-4b73-94d9-f23716c42aac"],["Classic Credit 36 Months 9.9%",44,"cc62bb86-f91b-4a85-97eb-94bb7ac4462f"],["Classic Credit 12 Months 15.9%",112,"bed9d208-d9c1-4d8e-a29f-decb53fd0b22"],["Classic Credit 24 Months 15.9%",64,"1401bd54-9a22-4ce7-8f7c-61a3ebb93639"],["Classic Credit 36 Months 15.9%",65,"bbe76da6-c60e-4881-83fc-328e415f0a5a"],["Classic Credit 48 Months 15.9%",66,"3fd9bcde-bc26-47d2-bd4f-df453bc6f1a1"]] 
    products = []
    id_list = []
    for item in product_details:
        products.append(item[0])
        id_list.append(item[1])

    session["products-list"] = products
    session["id-list"] = id_list

    if request.method == 'POST':
        product_id = int(request.form.get("product-dropdown"))
        cash_price = request.form.get("cash-price-input")
        deposit_amount = request.form.get("deposit-input")
        product_guid = product_details[id_list.index(product_id)][2]

        payload = {
        "Order":{
           "CashPrice":"",
           "Deposit":"",
           "DuplicateSalesReferenceMethod":"",
           "ProductGuid":"",
           "ProductId":"",
           "SalesReference":""
        },
        "Retailer":{
           "AuthenticationKey":"",
           "RetailerGuid":"",
           "RetailerId":""
        }
      }
        payload["Order"]["CashPrice"] = cash_price
        payload["Order"]["Deposit"] = deposit_amount
        payload["Order"]["ProductGuid"] = product_guid
        payload["Order"]["ProductId"] = str(product_id)
        payload["Order"]["SalesReference"] = str(random.randint(0,999999))

        payload["Retailer"]["AuthenticationKey"] = os.getenv("AuthenticationKey")
        payload["Retailer"]["RetailerGuid"] = os.getenv("RetailerGuid")
        payload["Retailer"]["RetailerId"] = os.getenv("RetailerId")

        print("PAYLOAD",payload)


        reqUrl = "https://apply.v12finance.com/latest/retailerapi/SubmitApplication"

        headersList = {
        "Accept": "*/*",
        "Content-Type": "application/json" 
        }

        response = requests.request("POST", reqUrl, json=payload,  headers=headersList)
        if response.status_code == 200:
            try:
                response_data = response.json()  # Parse the response as JSON
                application_form_url = response_data.get("ApplicationFormUrl")  # Extract the URL

                if application_form_url:
                    return redirect(application_form_url)
                else:
                    print("ApplicationFormUrl not found in the response.")
            except ValueError:
                print("Failed to parse JSON response:", response.text)
        else:
            print(f"Request failed with status code {response.status_code}: {response.text}")
        print(response.text)

    
    return render_template('finance_products.html')

@app.route('/')
def index():
    return '<h1> REST API</h1>'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 