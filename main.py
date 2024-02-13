#import mysql lalu mysql connector
import mysql.connector
import neattext.functions as nfx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import MySQLdb
import pyrebase
# from flask_mysqldb import MySQL
import re, hashlib
import os

app = Flask(__name__)
app.secret_key = 'lnglnglngadalahkuncirahasia'

import os
# import library lainnya

# Kode lainnya

db = mysql.connector.connect(
    host=os.environ['MYSQL_HOST'],
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASSWORD'],
    database=os.environ['MYSQL_DATABASE']
)


def cleaning_text(text):
    text = nfx.remove_stopwords(text)
    text = nfx.remove_special_characters(text)
    text = nfx.remove_puncts(text)
    text = nfx.remove_multiple_spaces(text)
    text = nfx.remove_emojis(text)
    text = text.lower()
    return text




@app.route('/recommend', methods=['POST', 'GET'])
def recommend_courses():
    if 'loggedin' in session:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()

        if account:
            user_id = account[0]

            question1 = request.form.get('question1')
            question2 = request.form.get('question2')
            question3 = request.form.get('question3')

            cleaned_question1 = cleaning_text(question1)
            cleaned_question2 = cleaning_text(question2)
            cleaned_question3 = cleaning_text(question3)

            user_answers = cleaned_question1 + " " + cleaned_question2 + " " + cleaned_question3

            cursor = db.cursor()
            cursor.execute("INSERT INTO answers (user_id, question1, question2, question3) VALUES (%s, %s, %s, %s)", (user_id, question1, question2, question3))
            db.commit()

            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()

            vectorizer = TfidfVectorizer()
            course_descriptions = [course[6] for course in courses]
            course_vectors = vectorizer.fit_transform(course_descriptions)
            user_vector = vectorizer.transform([user_answers])
            similarity_scores = cosine_similarity(user_vector, course_vectors)

            sorted_indices = similarity_scores.argsort()[0][::-1]
            recommended_courses = [courses[idx] for idx in sorted_indices]

            recommended_courses = recommended_courses[:15]

            return render_template('./html/index2.html', recommended_courses=recommended_courses , username=session['username'])

    return redirect(url_for('login'))


# @app.route('/')
# def index():
#     return render_template('./html/assesment.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        hash = password + app.secret_key
        hash = hashlib.sha1(hash.encode())
        password = hash.hexdigest()

        cursor = db.cursor()

        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[2]
            return redirect('/home')
        else:
            msg = 'Incorrect username/password!'

    return render_template('./html/login2.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        full_name = request.form['full_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            hash = password + app.secret_key
            hash = hashlib.sha1(hash.encode())
            password = hash.hexdigest()

            cursor.execute('INSERT INTO users VALUES (NULL,%s, %s, %s, %s)', (full_name, username, email, password,))
            db.commit()
            msg = 'You have successfully registered!'

    elif request.method == 'POST':
        msg = 'Please fill out the form!'
        
    return render_template('./html/signup.html', msg=msg)


@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'loggedin' in session:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        user = cursor.fetchone()

        if user:
            username = user[2]  # Mengambil nama pengguna dari hasil query
            cursor.execute('SELECT * FROM answers WHERE user_id = %s', (session['id'],))
            assessment = cursor.fetchone()

            if request.method == 'POST':
                # Pencarian Kursus
                search = request.form.get('searcg')
                cleaned_search = cleaning_text(search)

                cursor = db.cursor()
                cursor.execute("SELECT * FROM courses")
                courses = cursor.fetchall()

                vectorizer = TfidfVectorizer()
                course_descriptions = [course[6] for course in courses]
                course_vectors = vectorizer.fit_transform(course_descriptions)
                user_vector = vectorizer.transform([cleaned_search])
                similarity_scores = cosine_similarity(user_vector, course_vectors)

                sorted_indices = similarity_scores.argsort()[0][::-1]

                search_courses = [courses[idx] for idx in sorted_indices]
                search_courses = search_courses[:15]

                # Insert ke dalam tabel searches
                user_id = session['id']
                insert_search = "INSERT INTO search_history (user_id, search) VALUES (%s, %s)"
                cursor.execute(insert_search, (user_id, cleaned_search))
                db.commit()

                return render_template('./html/search_results2.html', search_courses=search_courses)

            else:
                # Cek apakah pengguna sudah melakukan asesmen sebelumnya
                cursor.execute('SELECT * FROM answers WHERE user_id = %s', (session['id'],))
                assessment = cursor.fetchone()

                if assessment:
                    # Proses hasil asesmen berdasarkan user id dan lakukan rekomendasi dengan fungsi recommend_courses berdasarkan jawaban answers
                    cursor.execute("SELECT * FROM courses")
                    courses = cursor.fetchall()

                    vectorizer = TfidfVectorizer()
                    course_descriptions = [course[6] for course in courses]
                    course_vectors = vectorizer.fit_transform(course_descriptions)
                    user_vector = vectorizer.transform([assessment[2] + " " + assessment[3] + " " + assessment[4]])
                    similarity_scores = cosine_similarity(user_vector, course_vectors)

                    sorted_indices = similarity_scores.argsort()[0][::-1]
                    recommended_courses = [courses[idx] for idx in sorted_indices]

                    recommended_courses = recommended_courses[:15]

                    return render_template('./html/index2.html', username=username, recommended_courses=recommended_courses)
                else:
                    # Setelah melakukan asesmen, langsung pindah ke halaman asesmen
                    return render_template('./html/assesment.html', username=username)

    return redirect(url_for('login'))



@app.route('/search', methods=['POST', 'GET'])
def search_courses():
    if 'loggedin' in session:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()

        if account:
            user_id = account[0]

            search = request.form.get('search')
            cleaned_search = cleaning_text(search)

            cursor = db.cursor()
            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()

            vectorizer = TfidfVectorizer()
            course_descriptions = [course[6] for course in courses]
            course_vectors = vectorizer.fit_transform(course_descriptions)
            user_vector = vectorizer.transform([cleaned_search])
            similarity_scores = cosine_similarity(user_vector, course_vectors)

            sorted_indices = similarity_scores.argsort()[0][::-1]

            search_courses = [courses[idx] for idx in sorted_indices]

            search_courses = search_courses[:30]

            # Insert ke dalam tabel searche_history
            user_id = session['id']
            search = cleaned_search

            cursor = db.cursor()
            cursor.execute("INSERT INTO search_history (user_id, search) VALUES (%s, %s)", (user_id, search))
            db.commit()

            return render_template('./html/search_results2.html', search_courses=search_courses)


@app.route('/profile' , methods=['GET', 'POST'])
def profile():
    if 'loggedin' in session:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('./html/profile.html', account=account)
    
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' in session:
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s', (session['id'],))
        account = cursor.fetchone()

        if request.method == 'POST':
            full_name = request.form.get('full_name')
            username = request.form.get('username')
            email = request.form.get('email')

            cursor = db.cursor()
            cursor.execute('UPDATE users SET full_name = %s, username = %s, email = %s WHERE user_id = %s', (full_name, username, email, session['id'],))
            db.commit()

            return redirect('/profile')

        return render_template('./html/editBiodata.html', account=account)
    
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8080)
