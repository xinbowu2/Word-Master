from flask import Flask, render_template, json, request, redirect, session
from werkzeug import generate_password_hash, check_password_hash

from Quiz import *
from QuizHandler import *

app = Flask(__name__)
qh = [None]
numOfQuizes = 3


con = pymysql.connect(host='localhost',
			 user='root',
			 password='Ab1993118',
			 db='test',
			 charset='utf8mb4',
			 cursorclass=pymysql.cursors.DictCursor)

app.secret_key = 'why would I tell you my secret key?'

@app.route('/')
@app.route('/index')
def main():
	return render_template('index.html')

@app.route('/showSignIn')
def showSignIn():
	return render_template('signin.html')

@app.route('/signIn',methods=['POST'])
def signIn():
	_username = request.form['inputUsername']
	_password = request.form['inputPassword']
	
	if _username and _password:
		with con.cursor() as cursor:
			sql = "select * from user where username = %s;"
			cursor.execute(sql, _username)

			if (cursor.rowcount > 0):
				for row in cursor:
					print('haha')
					if row['password'] == _password:
						session['user'] = row['username']
						return render_template('userHome.html')
					else:
						return render_template('error.html',error = 'Wrong Username or Password.')
			else:
				return render_template('error.html',error = 'Wrong Username or Password.')

	else:
		return json.dumps({'html':'<span>Enter the required fields</span>'})


@app.route('/showSignUp')
def showSignUp():
	return render_template('signup.html')

@app.route('/signUp',methods=['POST','GET'])
def signUp():
	_username = request.form['inputUsername']
	_password = request.form['inputPassword']

	if _username and _password:
		with con.cursor() as cursor:
			sql = "select * from user where username = %s;"
			cursor.execute(sql, _username)
			print("hi")

			if (cursor.rowcount == 0):
				sql2 = "insert into user (username,password) values(%s,%s);"
				cursor.execute(sql2, (_username, _password))
				con.commit()
				session['user'] = _username;
				return render_template('userHome.html')
			else:
				return render_template('error.html',error = 'Username exists!')

	else:
		return json.dumps({'html':'<span>Enter the required fields</span>'})


@app.route('/userHome')
def userHome():
	if session.get('user'):
		return render_template('userHome.html', username = session.get('user'))
	else:
		return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
	session.pop('user',None)
	return redirect('/')

@app.route('/wordlist')
def wordlist():
	if session.get('user'):
		return render_template('wordlist.html', username = session.get('user'))
	else:
		return render_template('error.html',error = 'Unauthorized Access')

@app.route('/addWord',methods=['GET','GET'])
def addWord():
	if session.get('user'):
		wordToAdd = request.args.get('wordToAdd')

		with con.cursor() as cursor:
			sql = "SELECT * FROM wordlist WHERE word=%s AND username=%s"
			cursor.execute(sql, (wordToAdd, session.get('user')))
			print(cursor.rowcount)
			if cursor.rowcount != 0:
				return "hehe"

			sql = "SELECT * FROM dict WHERE word=%s;"
			cursor.execute(sql, wordToAdd)

			if (cursor.rowcount == 0):
				return "hehe"

			sql2 = "INSERT INTO wordlist (username, word, orig_count, correctness, test_count) VALUES (%s, %s, 0, 0, 0);"
			cursor.execute(sql2, (session.get('user'), wordToAdd))

		con.commit()

		return "hehe"

	else:
		return render_template('error.html',error = 'Unauthorized Access')

@app.route('/searchWord', methods = ['GET'])
def searchWord():
	if session.get('user'):
		wordToSearch = request.args.get('wordToSearch')


		with con.cursor() as cursor:
			sql = "SELECT meaning FROM dict WHERE word = %s;"
			cursor.execute(sql, wordToSearch)

		meaning = "word not found"
		for m in cursor:
			meaning = m['meaning']

		return meaning
	else:
		return render_template('error.html',error = 'Unauthorized Access')

@app.route('/quizSubmit', methods = ['POST'])
def quizSubmit():
	if session.get('user'):
		jsdata = request.form['returnedAnswers']
		results = json.loads(jsdata)


		username = str(session.get('user'))
		qh[0].updateCorrectness(username, results)
		return "hehe"

	else:
		return render_template('error.html',error = 'Unauthorized Access')

@app.route('/showQuiz')
def showQuiz():
	if session.get('user'):

		with con.cursor() as cursor:
				sql = "SELECT * FROM wordlist WHERE username = %s;"
				cursor.execute(sql, session.get('user'))
		if (cursor.rowcount < numOfQuizes):
			return render_template('errorQ.html',error = 'too few words in your list...')

		username = str(session.get('user'))
		qh[0] = QuizHandler(username, con, num_quizes=numOfQuizesm)
		quizes = qh[0].get_quizes()

		listOfQuizDicts = []
		for q in quizes:
			quizD = dict()
			quizD.update({'question': q.get_word()})
			quizD.update({'choices': q.get_choices()})
			quizD.update({'answer': q.get_correctChoice()})
			listOfQuizDicts.append(quizD)

		return render_template('quiz.html', username = session.get('user'), question = quizes[0].get_question(), quizes = listOfQuizDicts, num=6, answer=quizes[0].get_correctChoice(),
							choiceA = quizes[0].get_choices()['A'], choiceB = quizes[0].get_choices()['B'], choiceC = quizes[0].get_choices()['C'], choiceD = quizes[0].get_choices()['D'])
	else:
		return render_template('error.html',error = 'Unauthorized Access')

@app.route('/getWord')
def getWord():
	try:
		if session.get('user'):

			with con.cursor() as cursor:
				sql = "SELECT * FROM wordlist WHERE username = %s;"
				cursor.execute(sql, session.get('user'))

			words_dict = []
			for w in cursor:
				words_dict.append({'content': w['word'], 'userid': w['username']})

			return json.dumps(words_dict)
		else:
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error = str(e))




@app.route('/getWordTag',methods=['GET'])
def getWordMeaning():
    try:
        
        # con = mysql.connect()
        # cursor = con.cursor()
        wordToSearch = request.args.get('wordToSearch')
        print 'wordToSearch'
        print wordToSearch
        words_dict = [] 
        global _word
       
        input=wordToSearch.split(' ')
        print "input to get method is"
        print input
        

        # for word in input:
        #     print _word
        #     cursor = con.cursor()
        #     cursor.callproc('sp_getWordMeaning',(_word,))
        #     cursor.callproc('sp_getWordMeaning',(word,))
        #     cursor.callproc('sp_getWordMeaning',(_word))
        #     words = cursor.fetchall()
        #     cursor.close()


        # print 'get word meaning'
        # print 'get words meaning'
        # print words
        # print type(words)
        # print list(words)
        # print words[0]
        # print list(words[0])

        #     for word in words:
        #         word_dict = {
        #                 #'meaning'
        #                 'meaning': word[2],
        #                 'word': word[1]}
        #         words_dict.append(word_dict)

        for word in input:
            # print "inside iteration"
            # print "word is"
            # print word

            with con.cursor() as cursor:
                sql = "SELECT * FROM dict WHERE word = %s;"
                cursor.execute(sql, word)
            
            print "inside iteration 2"
            for m in cursor:
                # print m['dic_word_meaning']
                # print m['dic_word_name']
                word_dict = {
                        'meaning': m['pos'],
                        'word': m['word']}
                words_dict.append(word_dict)

        
        print"words_dict"
        print words_dict
        return json.dumps(words_dict)
        # else:
        #     return render_template('error.html', error = 'Unauthorized Access')
    except Exception as e:
        return render_template('error.html', error = str(e))
 













if __name__ == "__main__":
  app.run()
