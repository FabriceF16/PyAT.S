#!/usr/bin/env python

"""
File name *app.py*

All functions for daily automation of Noel Chaks' tasks, using web application
"""

__author__ = "Fabrice F."
__copyright__ = "Copyright 2023, PyAT.S Project"
__credits__ = ["Fabrice F.","TBC Eric, AT.S Association etc..."]
__license__ = "GPL"
__version__ = "0.1"
__maintainer__ = "Fabrice F."
__email__ = ""
__status__ = "Development"

from flask import Flask, render_template, redirect, url_for, flash, get_flashed_messages, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import json, plotly

import pyats




app = Flask(__name__)
app.config['SECRET_KEY'] = 'pyATS-secret-key'

@app.route("/", methods=['GET', 'POST'])
@app.route("/index")
def index():
    #return "<h1>Hello,</h1> World!"    
    return render_template('index.html')

@app.route('/ats', methods=['GET', 'POST'])
@app.route('/ats/<symbol>', methods=['GET', 'POST'])
def ats(symbol=None):
    if symbol == None:
        symbol = request.form.get('symbol')
        print('Symbol '+symbol)

    name = ""

    ticker = pyats.Ticker(symbol)
    ticker.download_data_from_ticker()
    #Dowload data
    if symbol == 'DBA':
        name = "DBA"

    #Generate AT.S view and save PNG 
    s_env = pyats.EnvATS(symbol,name)
    if s_env.get_status() == 1:
        fig = s_env.create_ats_view()
        img_path = "/static/"+s_env.get_img()
        print(img_path)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('ats.html',symbol=symbol,img_path=img_path,graphJSON=graphJSON)

    return render_template('index.html')   

@app.route("/bonjour", methods=['POST'])
def bonjour():
    print("bonjour 234")
    flash('Bonjour 234')
    #return render_template('discord.html',symbol='Bonjour')
    return redirect(url_for('index'))


# @app.route("/about")
# def about():
    # return render_template('about.html', current_title='Some title')
    
##############################################################################
### Main section
##############################################################################
if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=False)