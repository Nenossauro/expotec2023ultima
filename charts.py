# Import necessary modules from Flask, pymongo, and os
from flask import Flask, render_template, request, redirect, session, flash
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pymongo as mongo
import os, datetime, altair, pandas, base64

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

def new_simplify_topics(info):
   
    # add first letter
    oupt = info[0]
     
    # iterate over string
    for i in range(1, len(info)):
        if info[i-1] == ' ':
           
            # add letter next to space
            oupt += info[i]
    oupt = oupt.lower()
    return oupt
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
    # add first letter
    oupt = info[0]
     
    # iterate over string
    for i in range(1, len(info)):
        if info[i-1] == ' ':
           
            # add letter next to space
            oupt += info[i]
    oupt = oupt.lower()
    return oupt
# Define a user object class to represent user data
class user_obj:
    def __init__(self,user,name,email,pwrd,pwrdconf, pic):
        self.user = user
        self.name = name
        self.email = email
        self.pwrd = pwrd
        self.pwrdconf = pwrdconf
        self.pic = pic

    # Define methods to convert user object to dictionary (JSON) format
    def __dict_user__(self):
        return {
            'email': self.email,
            'user': self.user,
            'password': self.pwrd,
            'name': self.name,
            'profile_img' :self.pic

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
    return render_template('land.html', user_name = session['user_logged'],profile_pic =  session['profile_img'], titles = titles, types = types)

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
        return render_template('chart_page.html',user_name = session['user_logged'], profile_pic =  session['profile_img'], chart_description = aux_desc, chart_tittle=aux_title,chart_topics = aux_topic, pie_chart_json = pie_chart_json )
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
        return render_template('chart_page.html',user_name = session['user_logged'],profile_pic =  session['profile_img'], chart_description = aux_desc, chart_tittle=aux_title,chart_topic = desimplify_topics(aux_topic),chart_topic2 = desimplify_topics(aux_topic2), pie_chart_json = pie_chart_json )

@charts.route('/criar-chart')
def create_chart():
    combo_topics = col_users.find_one({'user':session['user_logged']})
    sub_topics = col_topics.find()
    sub_array = []
    for info in sub_topics:
        sub_array.append(info['sub_topic'])

    return render_template('create_chart.html',user_name = session['user_logged'],profile_pic =  session['profile_img'],topics = combo_topics["ava_topic"], sub_topic = sub_array)


@charts.route('/profile')
def profile():
    return render_template('profile.html',user_name = session['user_logged'],profile_pic =  session['profile_img'],name = session['name'],user=session['user_logged'])

#@charts.route('/profile/change_pic',methods=['POST',])
#def cng_pic():
#    img = base64.b64encode(request.files['img'].read()).decode('utf-8')
#    session['profile_img'] = None
#    session['profile_img'] = "data:image/png;base64,"+img
#    col_users.update_one({"user":session['user_logged']},{"$set":{"profile_img":"data:image/png;base64,"+img}})
#
#    return render_template('profile.html',user_name = session['user_logged'],profile_pic =  session['profile_img'],name = session['name'],user=session['user_logged'])



@charts.route('/profile/change_email')
def cng_email():
    return render_template('email.html',user_name = session['user_logged'],profile_pic =  session['profile_img'])
@charts.route('/profile/change_password')
def cng_password():
    return render_template('password.html',user_name = session['user_logged'],profile_pic =  session['profile_img'])

@charts.route('/inserir-chart',methods=['POST',])
def insert_chart():
    
    chart_tittle = request.form['txttitulo']
    chart_date = request.form['txtdata']
    chart_description = request.form['txtdescricao']
    chart_topic1 = simplify_topics(request.form['first-select'])
    chart_topic2 = simplify_topics(request.form['second-select'])
    chart_subtopic2 = request.form['second-if-select']
    if chart_topic2 == "s":
        col_charts.insert_one({"title":chart_tittle,"creation_date":chart_date,"description":chart_description,
                          "topic1":chart_topic1,"type":"simple"})
    else:
        col_charts.insert_one({"title":chart_tittle,"creation_date":chart_date,"description":chart_description,
                          "topic1":chart_topic1,"topic2":chart_topic2,"subtopic2":chart_subtopic2,"type":"complex"})
    return redirect('/land')
  
    


@charts.route('/adicionar-informações')
def add_info():
   
    return render_template('add_info.html', questions_r = user_questions_r, questions_l = user_questions_l,user_name = session['user_logged'],profile_pic =  session['profile_img'])


@charts.route('/inserir-info',methods=['POST',])  
def insert_info():
        
        question_1 = "Animal Favorito"
        question_1_awn=request.form['animal']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Cor Favorita"
        question_1_awn=request.form['cor']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})
        
        question_1 = "Idade"
        question_1_awn=request.form['idade']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Como veio"
        question_1_awn=request.form['transporte']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Tem pet"
        question_1_awn=request.form['pet']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Musica Favorita"
        question_1_awn=request.form['musica']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Já saiu do país"
        question_1_awn=request.form['pais']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Metros de Altura"
        question_1_awn=request.form['altura']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Quantidade de livros lidos esse ano"
        question_1_awn=request.form['livro_ano']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Já saiu do estado"
        question_1_awn=request.form['estado']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Está trabalhando"
        question_1_awn=request.form['trabalha']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Filme Favorito"
        question_1_awn=request.form['filme']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Genero de Musica"
        question_1_awn=request.form['musica_genero']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Genero de Filme"
        question_1_awn=request.form['filme_genero']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Cor dos olhos"
        question_1_awn=request.form['olhos']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Relacionamento romantico"
        question_1_awn=request.form['relacionamento']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Melhor animal de estimação"
        question_1_awn=request.form['melhor_pet']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Achou o site interessante"
        question_1_awn=request.form['interessante']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Quantidade de refeições no dia"
        question_1_awn=request.form['refeicoes']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

        question_1 = "Quantidade de quartos em casa"
        question_1_awn=request.form['quartos']
        col_users.update_one({'user':session['user_logged']},{"$set":{new_simplify_topics(question_1):question_1_awn}})
        col_users.update_one({'user':session['user_logged'],'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
        col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})
    

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
        pic = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFMAAABTCAMAAADUbMsyAAABX1BMVEWenp6fn5+goKChoaGioqKjo6OkpKSlpaWmpqanp6eoqKipqamqqqqrq6usrKytrKytra2ura2urq6vrq6vr6+wr6+wsLCxsbGysrKzs7O0tLS1tbW2tra3t7e4uLi5ubm6urq7u7u8vLy9vb2+vr6/v7/AwMDBwcHCwsLDw8PExMTFxcXGxsbHxcXHx8fIxsbIyMjJx8fJycnKyMjKysrLycnLysrLy8vMy8vMzMzNzMzNzc3Ozs7Pzc3Pzs7Pz8/Qz8/Q0NDR0NDR0dHS0tLT0tLT09PU09PU1NTV1NTV1dXW1dXW1tbX1tbX19fY2NjZ2dna2dna2trb29vc29vc3Nzd3d3e3t7f39/g4ODh4ODh4eHi4uLj4+Pk5OTl5eXm5ubn5+fo5+fo6Ojp6Ojp6enq6urr6+vs7Ozt7e3u7u7v7+/w8PDx8fHy8vLz8/P09PT19fX29vb39/f///8Ku0ecAAAAAWJLR0R0322obQAAA19JREFUWMPt2etTElEUAPDDS8FXRaaoFCCpmawmYUpZlpkhEZC0V42XRCTy3uX/n2lfymvvLvcuM02T54POuGd/cx+7O+dcoT36gDvzL5lsPNsancnlCu12wQxg8WVGY9Ze2O2NdmUGpPBVR2CmxgE8rbgDlHDkDZsHomO1QSdseYNmBAbDvl83YDbXTaAWY8fUZsUJuFjh6MyGOmmZEn+u0ZmrqqQ1PC39jtGYuZ61NJktVtuY3fk0jiblnWpQmMu3I1t6fhBLplikhDxOOCI3GxaF9CRRb8zLf3eRm6wy5w3UH17lSp3YDMp3BgZItKlMIENsysv5ZJBECWXzYsTmorQ9CRXzZkE/EJsu3DARCsvmAd04w6ommtV+mDTX05RUNyNW0UwSmyHxXUGYCInblKd6PmdxJnJRPZ9VYShLWFNYmQmK9114rb1apofcvHoM4MeaPuEL2iI2swHha65lhn8TmxdRYShY0wvm00tSkz9j7bCuMU4nypObyA2bGuYaKhDP/RwFYBdrrpiiqERsZlBMuA8Xb5wIXRObReFGhI84Qk1is450Ik3xHmV0zDKFqTPQDE9Th1SKePG8xNHVYDzezFLXivglLVKbJaxZpTax23TO09feaZqp65hldfKsZcDkLyiGqdd31FRXkzPWH2VVzCuDPVf62wB58sugmT887SeZnwbNXOpVrFtkDxnmhyGTC4RQYuv1bRXKnrxkGOaev0Fv1hYgKNTF28zO4ZdE4uvnt9uMGA9g5oq6N7wPoolO95ieEPo7R5HOrIrHAEFpyp+2us2HYhlZojGbc3BjCkN936U+Ei9MVshNXm6DQrfbE323I7nbe1KpD3OkNRhf2pAbgcds94P0PSW0iFHl1MF/yQ1vVmPL9tvm1d3/zB85OmcDnqPyMGYj6jb3NNeOntKBfWbpuWpyfazqmLlV62DLvhDp1DSTg5fNvr7PfrfJJebVTyrMq/Kqsl7MUcbMcVPV5CJT2OMPeatS8/gE+35z0GSnQSvEktmtmeGI8r1m3Q/aYY6hXZ0UWLruNotTevngZfVzxtMdszCumw5j+/o5YDm7MWsTQ6TD4jBJtpJirsBQ6UNlLfCSWTbBCONCMo9HSUJAMkMjNf2SGfyPzXR4lJG6+3/Hv2D+AevXwHEUe10sAAAAAElFTkSuQmCC"
        )
    # Insert user data as a dictionary (JSON file) into the 'users' collection
    col_users.insert_one(new_user.__dict_user__())
    sessao = request.form['txtusuario']
    question_1 = "País em que mora"
    question_1_awn=request.form['txtpais']
    col_users.update_one({'user':sessao},{"$set":{new_simplify_topics(question_1):question_1_awn}})
    col_users.update_one({'user':sessao,'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
    col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

    question_1 = "Estado em que mora"
    question_1_awn=request.form['txtestado']
    col_users.update_one({'user':sessao},{"$set":{new_simplify_topics(question_1):question_1_awn}})
    col_users.update_one({'user':sessao,'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
    col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

    question_1 = "Cidade em que mora"
    question_1_awn=request.form['txtcidade']
    col_users.update_one({'user':sessao},{"$set":{new_simplify_topics(question_1):question_1_awn}})
    col_users.update_one({'user':sessao,'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
    col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

    question_1 = "Cor do Cabelo"
    question_1_awn=request.form['txtcorcabelo']
    col_users.update_one({'user':sessao},{"$set":{new_simplify_topics(question_1):question_1_awn}})
    col_users.update_one({'user':sessao,'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
    col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

    question_1 = "Numero do calçado"
    question_1_awn=request.form['txtcalcado']
    col_users.update_one({'user':sessao},{"$set":{new_simplify_topics(question_1):question_1_awn}})
    col_users.update_one({'user':sessao,'sub_topic': {'$ne': question_1}},{'$addToSet':{'ava_topic':question_1}})
    col_topics.update_one({'topic':question_1,'sub_topic': {'$ne': question_1_awn}},{'$addToSet': {'sub_topic': question_1_awn}})

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
        aux_img = info['profile_img']
        aux_name = info['name']
    # Check if the submitted username matches any user in the database
    if username == aux_user:
        # If the username matches, check if the submitted password matches the stored password
        if password == aux_pass:
            # If both username and password match, store the username in the session
            # Redirect the user to the '/land' page (landing page after successful login)
            session['user_logged'] = aux_user
            session['profile_img'] = aux_img
            session['name'] = aux_name
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
