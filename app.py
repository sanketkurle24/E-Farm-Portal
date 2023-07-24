from flask import Flask,request,render_template,url_for,redirect,flash,session
from flask import request
from flask_pymongo import PyMongo
from werkzeug.utils import secure_filename
import urllib.request

import os


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/project"
mongo = PyMongo(app)

UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#set app as a Flask instance 
@app.route("/")
def home():
	
	return render_template('main.html')

@app.route("/about_us")
def about_us():
	
	return render_template('about_us.html')

@app.route("/registration",methods=['GET','POST'])
def registration():
	if request.method == "POST":

					fullname = request.form.get("fullname")
					email = request.form.get("email")
					username = request.form.get("username")
					phone = request.form.get("phone")
					password = request.form.get("password")
					address = request.form.get("address")
					value= request.form.get('myCheckbox')
					user_input = {'fullname': fullname, 'email': email,'username':username,'phone':phone, 'password':password,'address':address }
					if (value=="1"):
						mongo.db.records.insert_one(user_input)
					else:
						mongo.db.buyer.insert_one(user_input)
					
			
	
	return render_template('registration.html',message1="registration successfull")
	

@app.route("/login",methods=["POST", "GET"])
def login():
			error = None
			if request.method == 'POST':
				email = request.form.get("email")
				password = request.form.get("password")
				value= request.form.get('myCheckbox')
				user_input = { 'email': email,'password':password}
				if (value=="1"):
					if not (mongo.db.records.find_one(user_input)):
							error = 'Invalid Credentials. Please try again.'
					else:
						a = mongo.db.records.find(user_input,{"username":1,"phone":1,"address":1})
						
						session['email']= email
						session['username']= a[0]["username"]
						session['phone']= a[0]["phone"]
						
						return redirect(url_for('Farmer_profileview',email=email))
				else:
					if not (mongo.db.buyer.find_one(user_input)):
							error = 'Invalid Credentials. Please try again.'
					else:
						session['email']= email
						return redirect(url_for('digital_market',email=email))
			return render_template('login.html', error=error)
			return render_template('login.html')




@app.route("/Farmer_profileview/",methods=['POST','GET'])

def Farmer_profileview():
	return render_template('Farmer_profileview.html',email=session["email"],username=session["username"],phone=session["phone"])

@app.route("/Farmer_updateProfile",methods = ['POST','GET'])
def Farmer_updateProfile():
	error = ""
	message=""
	if request.method == 'POST':		
			email= request.form.get('email')
			phone= request.form.get('phone')
			username = request.form.get("username")
			password = request.form.get("password")
			address = request.form.get("address")
			if not(mongo.db.records.find_one({'email': email})):
					error = 'no such email found!'
				
			else:
				mongo.db.records.update_one({'email':email},{"$set":{'phone':phone,'username':username, 'password':password,'address':address}})
				message= 'Updated your records successfully'
	return render_template('Farmer_updateProfile.html',error=error ,message=message)

@app.route('/upload_product', methods=['POST','GET'])
def upload_product():
		error=""
		message=""
		value= request.form.get('myCheckbox')
		if 'profile_image'in request.files:
			
			profile_image = request.files['profile_image']
		
			if profile_image  and allowed_file(profile_image.filename):
					mongo.save_file(profile_image.filename,profile_image)
					mongo.db.myproducts.insert({'username':request.form.get('username'),'product_name':request.form.get('product_name'),'product_prize':request.form.get('product_prize'),'profile_image':profile_image.filename,'product_prize':request.form.get('product_prize'),'category':request.form.get('myCheckbox')})
					
					message='File uploaded successfully'
			else:
					
					error = 'Invalid file. Allowed file extensions are jpg,png,jpeg.'
		return render_template('upload_product.html',error=error,message=message)   
  

@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)

@app.route("/view_product",methods=['post','get'])
def view_product():
		
		
		password= request.form.get('password')
		myproducts= mongo.db.myproducts.find({'password':password})
		return render_template('viewProduct.html',myproducts=myproducts)

@app.route("/category",methods=['post','get'])
def category():
		
		
		value= request.form.get('value')
		print(value)
		if(value=="fruit"):
			
			myproducts=mongo.db.myproducts.find({"category":"fruit"})
			
			return render_template('viewProduct.html',myproducts=myproducts)

		elif(value=="grain"):
			myproducts= mongo.db.myproducts.find({"category":"grain"})
			return render_template('viewProduct.html',myproducts=myproducts)
		else:
			myproducts= mongo.db.myproducts.find({"category":"vegetable"})
			return render_template('viewProduct.html',myproducts=myproducts)

		

		
	

@app.route("/delete_product/",methods=["DELETE"])
@app.errorhandler(405)
def delete_product(product_name):
		error=""
		message=""
		if request.method == 'POST':
				
				if not(mongo.db.myproducts.find_one({'product_name' : request.form.get('product_name')})):
					#return f''' value does not match
					error = 'product not found'
					
				else:
					currentCollection = mongo.db.myproducts
					currentCollection.remove({'product_name' : request.form.get('product_name')})
					#return 'data has been removed'
					message='deleted record successsfully'
		return render_template('delete_product.html',error=error,message=message)



@app.route("/digital_market")
def digital_market():
	password= request.form.get('password')
	myproducts= mongo.db.myproducts.find({'password':password})
	return render_template('Digital_market.html',myproducts=myproducts)

 




@app.route("/transaction",methods=["GET","POST"])
def transaction():
	if 'email' in session:
			return render_template('transaction.html')
	else:
		return redirect("/login")
		
		

@app.route("/logout")
def logout():
	session.clear()
	return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=True)