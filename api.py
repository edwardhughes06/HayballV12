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

    product_details = json.loads(os.getenv("PRODUCT_DETAILS"))

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
    app.run(host='127.0.0.1', port=8000, debug=False)
 