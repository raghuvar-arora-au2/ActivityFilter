import os
from flask import Flask, flash, request, redirect, render_template
from werkzeug.utils import secure_filename
import pandas as pd

app=Flask(__name__)

app.secret_key = "secret key"
# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
	os.mkdir(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# def allowed_file(filename):
# 	 return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def upload_form():
	return render_template('upload.html')


@app.route('/', methods=['POST'])
def upload_file():
	try:
		if request.method == 'POST':
			# check if the post request has the file part
			if 'file' not in request.files:
				flash('No file part')
				return redirect(request.url)
			file = request.files['file']
			if file.filename == '':
				flash('No file selected for uploading')
				return redirect(request.url)
			if file:
				filename = secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				flash('File successfully uploaded')


				df=pd.read_csv("uploads/"+filename, delimiter=",")
				df.rename(inplace=True,columns={'Quantity Traded ':"Quantity","Trade Price / Wght. Avg. Price":"Price",'Buy / Sell':'buy/sell'})
				df["Quantity"]=df["Quantity"].str.replace(",","")
				df["Quantity"]= pd.to_numeric(df["Quantity"])
				df.loc[df["buy/sell"] == 'SELL', 'Quantity'] = -df['Quantity']
				df["Traded_Amount"]=df["Quantity"]*df["Price"]
				result=df.groupby(["Symbol"]).agg({"Price":"mean","Quantity":"sum","Traded_Amount":"sum"}).sort_values(["Traded_Amount"], ascending=False)
				result=result[result["Traded_Amount"]>1000000000]
				bystockALL=""
				for name in list(result.index):
					byStock=df[df["Symbol"]==name].groupby(["Client Name"]).agg({"Price":"mean","Quantity":"sum"})
					byStock=byStock.rename_axis(name)
					byStock=byStock[byStock["Quantity"] != 0 ]
					bystockALL=bystockALL+byStock.to_html()

				return result.to_html()+bystockALL
			else:
				flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
				return redirect(request.url)
	except:
		flash("Uh oh")

if __name__ == "__main__":
	app.run(host = '127.0.0.1',port = 5000, debug = False)