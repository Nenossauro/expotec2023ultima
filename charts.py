# Import necessary modules from Flask, pymongo, and os
from flask import Flask, render_template, request, redirect, session, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo as mongo
import os, datetime, altair, pandas

# MongoDB connection URL
url = "mongodb+srv://admin:admin@cluster0.blievi7.mongodb.net/?retryWrites=true&w=majority"
# Create a MongoClient instance with the specified URL and ServerApi version
client = MongoClient(url, server_api=ServerApi('1'))

# Access the 'expotec' database and its collections
db = client["expotec"]
col_users = db["users"]
col_charts = db["charts"]
col_topics = db["topics"]
col_questions = db["questions"]

def desimplify_topics(info):
    if info == "stt":
        return "Estado onde mora"
    elif info == "hair":
        return "Cor do Cabelo"
    elif info == "shoe":
        return "Numero do Calçado"
    elif info == "cty":
        return "Cidade onde mora"
    else:
        return info
def simplify_topics(info):
    if info == "Estado onde mora":
        return "stt"
    elif info == "Cor de cabelo":
        return "hair"
    elif info == "Numero do calçado":
        return "shoe"
    elif info == "Cidade onde mora":
        return "cty"
    else:
        return info
# Define a user object class to represent user data
class user_obj:
    def __init__(self,user,name,email,pwrd,pwrdconf,cnt,stt,cty,hair,shoe,ava_topics):
        self.user = user
        self.name = name
        self.email = email
        self.pwrd = pwrd
        self.pwrdconf = pwrdconf
        self.cnt = cnt
        self.stt = stt
        self.cty = cty
        self.hair = hair        
        self.shoe = shoe
        self.ava_topics = ava_topics

    # Define methods to convert user object to dictionary (JSON) format
    def __dict_user__(self):
        return {
            'email': self.email,
            'user': self.user,
            'password': self.pwrd,
            'name': self.name,
            'cnt': self.cnt,
            'stt': self.stt,
            'cty': self.cty,
            'hair': self.hair,
            'shoe': self.shoe,
            'ava_topic': self.ava_topics
        }
    def __dict__(self):
        return {
            
        }




# Function to retrieve user information based on specified field
def get_your_info(info_want,session):
    # Search the 'users' collection in the database for a user with the specified session (username)
    personal_info = col_users.find({'user':session})
    # Iterate over the search results (usually just one user document)
    for info in personal_info:
        aux_name = info['name']
        aux_country = info['cnt']
        aux_state = info['stt']
        aux_city = info['cty']
        aux_hair = info['hair']
        aux_shoe = info['shoe']
    # Use a switch-case structure to determine which information to return based on 'info_want'
    match(info_want):
        case "name":
            return aux_name
        case "country":
            return aux_country
        case "state":
            return aux_state
        case "city":
            return aux_city
        case "hair":
            return aux_hair
        case "shoe":
            return aux_shoe
# Clear console screen for better visualisation
os.system("cls")

# Create a Flask app instance and set a secret key to handle sessions
charts = Flask(__name__)
charts.secret_key = 'enzo'


user_questions_l = ['Qual seu animal favorito?','Qual sua musica favorita?']
user_questions_r = ['Você já saiu do país?','Qual sua idade?']

# Define route to render index.html template
@charts.route('/')
def index():
    return render_template('index.html')

@charts.route('/land')
def land():
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect('/')
    os.system("cls")
    charts_data = col_charts.find()
    titles = []
    types = []
    for aux_charts in charts_data:
        titles.append(aux_charts['title'])
        types.append(aux_charts['type'])
    return render_template('land.html', user_name = session['user_logged'], titles = titles, types = types)

@charts.route('/land/<title>')
def chart_page(title):
    if 'user_logged' not in session or session['user_logged'] == None:
        return redirect('/')
    chart_data = col_charts.find_one({"title": title})
    aux_title = chart_data['title']
    aux_type = chart_data['type']
    aux_desc = chart_data['description']
    if aux_type=="simple":
        os.system("cls")
        aux_topic = chart_data['topic1']
        user_topics = []
        user_data = col_users.find({aux_topic: {'$ne': ''}})
        user_topics = [each[aux_topic] for each in user_data]
        df = pandas.DataFrame({'category': user_topics})
        counts = df['category'].value_counts().sort_index()
        chart_df = pandas.DataFrame({'Topic': counts.index, 'Frequency': counts.values})
        chart_df['ratio'] = round((chart_df['Frequency']/len(user_topics)*100))
        pie_chart = altair.Chart(chart_df).mark_arc(size=100).encode(
            theta='ratio:Q',
            color='Topic:N',
            tooltip='Frequency:N'
            
        ).properties(
       width=400,
         height=400,
        title=title
        )
        pie_chart_json = pie_chart.to_json()
        return render_template('chart_page.html',chart_description = aux_desc, chart_tittle=aux_title,chart_topics = desimplify_topics(aux_topic), user_name = session['user_logged'], pie_chart_json = pie_chart_json )
    else:
        os.system("cls")
        aux_topic = chart_data['topic1']
        aux_topic2 = chart_data['topic2']
        aux_subtopic = chart_data['subtopic2']
        user_topics = []
        user_data = col_users.find({
            '$and': [
                { aux_topic: { '$ne': '' } },
                { aux_topic2: aux_subtopic }
            ]
        })
        user_topics = [each[aux_topic] for each in user_data]
        df = pandas.DataFrame({'category': user_topics})
        counts = df['category'].value_counts().sort_index()
        chart_df = pandas.DataFrame({'Topic': counts.index, 'Frequency': counts.values})
        chart_df['ratio'] = round((chart_df['Frequency']/len(user_topics)*100))
        pie_chart = altair.Chart(chart_df).mark_arc(size=100).encode(
            theta='ratio:Q',
            color='Topic:N',
            tooltip='Frequency:N'
            
        ).properties(
        width=500,
        height=500,
        title=title
        )

        pie_chart_json = pie_chart.to_json()
        return render_template('chart_page.html',chart_description = aux_desc, chart_tittle=aux_title,chart_topic = desimplify_topics(aux_topic),chart_topic2 = desimplify_topics(aux_topic2), user_name = session['user_logged'], pie_chart_json = pie_chart_json )

@charts.route('/criar-chart')
def create_chart():
    combo_topics = col_users.find_one({'user':session['user_logged']})
    sub_topics = col_topics.find()
    sub_array = []
    for info in sub_topics:
        sub_array.append(info['sub_topic'])

    return render_template('create_chart.html',user_name = session['user_logged'],topics = combo_topics["ava_topic"], sub_topic = sub_array)






@charts.route('/inserir-chart',methods=['POST',])
def insert_chart():
    
    chart_tittle = request.form['txttitulo']
    chart_date = request.form['txtdata']
    chart_description = request.form['txtdescricao']
    chart_topic1 = simplify_topics(request.form['first-select'])
    chart_topic2 = simplify_topics(request.form['second-select'])
    chart_subtopic2 = request.form['third-select']
    if chart_topic2 == "simple":
        col_charts.insert_one({"title":chart_tittle,"creation_date":chart_date,"description":chart_description,
                          "topic1":chart_topic1,"type":"simple"})
    else:
        col_charts.insert_one({"title":chart_tittle,"creation_date":chart_date,"description":chart_description,
                          "topic1":chart_topic1,"topic2":chart_topic2,"subtopic2":chart_subtopic2,"type":"complex"})
    return redirect('/land')
  
    


@charts.route('/adicionar-informações')
def add_info():
   
    return render_template('add_info.html', questions_r = user_questions_r, questions_l = user_questions_l)


@charts.route('/inserir-info',methods=['POST',])  
def insert_info():
        question_1=request.form['animal']
        print(question_1)
        col_users.update_one({'user_name':session['user_logged']},{"$set":{'anm':question_1}})
        col_users.update_one({'user_name':session['user_logged']},{"$set":{'anm':question_1}})

        return redirect('/land')
# Define route for registration form submission
@charts.route('/registrar', methods=['POST',])
def regis():
    # Create a new user object with form data
    new_user = user_obj(
        user = request.form['txtusuario'],
        name = request.form['txtnome'],
        email = request.form['txtemail'],
        pwrd = request.form['txtsenha'],
        pwrdconf = request.form['txtsenhaconf'],
        cnt = request.form['txtpais'],
        stt = request.form['txtestado'],
        cty = request.form['txtcidade'],
        hair = request.form['txtcorcabelo'],
        shoe = request.form['txtcalcado'],
        ava_topics = ["País onde mora","Estado onde mora","Cidade onde mora","Cor de cabelo","Numero do calçado"]
        )
    # Insert user data as a dictionary (JSON file) into the 'users' collection
    col_users.insert_one(new_user.__dict_user__())
    # Render the index.html template after registration
    return redirect('/')

# Define route for authentication of user
@charts.route('/logar',methods=['POST',])
# Run the Flask app
def logar():
    # Retrieve the username and password submitted in the login form
    username = request.form['txtusuariologin']
    password = request.form['txtsenhalogin']
    # Search the 'users' collection in the database for a user with the specified username
    usercheck = col_users.find({"user":username})
    # Iterate over the search results (usually just one user document)
    for info in usercheck:
        aux_user = info['user']
        aux_pass = info['password']
    # Check if the submitted username matches any user in the database
    if username == aux_user:
        # If the username matches, check if the submitted password matches the stored password
        if password == aux_pass:
            # If both username and password match, store the username in the session
            # Redirect the user to the '/land' page (landing page after successful login)
            session['user_logged'] = aux_user
            return redirect('/land')
        else:
             # If the submitted password doesn't match, redirect to the index page (login page)
            return redirect('/')
    else:
        # If the submitted username doesn't match any user in the database, redirect to the index page
        return redirect('/')

@charts.route('/logout',methods=['POST',])
def logout():
   if 'user_logged' not in session or session['user_logged'] == None:
        return redirect('/') 
   session['user_logged'] = None
   return redirect('/')
charts.run()
