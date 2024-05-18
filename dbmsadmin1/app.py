from flask import Flask, render_template, request, redirect, url_for, session
from pymongo.errors import BulkWriteError
from pymongo import MongoClient
from datetime import datetime
import pymongo

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = 'xyz1234nbg789ty8inmcv2134'
client = MongoClient('mongodb://localhost:27017/')
db = client['user_login_system']
users_collection = db['users']
events_collection = db['events']
winner1_collection = db['winner1']
winner2_collection = db['winner2']
competition1_collection = db['competition1']
competition2_collection = db['competition2']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['username'] = 'admin'
            session['role'] = 'admin'  # Store the role in the session
            return redirect(url_for('competition_selection'))
        elif username == 'admin1' and password == 'admin1':
            session['username'] = 'admin1'
            session['role'] = 'admin1'  # Store the role in the session
            return redirect(url_for('competition_selection'))
        else:
            return render_template('login.html', error='Invalid credentials. Please try again.')

    return render_template('login.html')


@app.route('/competition_selection')
def competition_selection():
    return render_template('competition_selection.html')

@app.route('/competition1', methods=['GET', 'POST'])
def competition1():
    # Restrict admin1 from entering marks for competition1
    if 'role' in session and session['role'] != 'admin':
        return render_template('error.html', message="Admin1 is not allowed to enter marks for Competition 1.")

    if request.method == 'POST':
        user_data = {}
        for key, value in request.form.items():
            if key.startswith('round1_') or key.startswith('round2_'):
                user_id = key.split('_')[1]
                round_number = key.split('_')[0][-1]
                round_marks = int(value)
                competition1_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {f'round{round_number}_marks': round_marks}},
                    upsert=True
                )
                user_info = users_collection.find_one({'_id': user_id})
                username = user_info.get('username', 'Unknown')
                if user_id in user_data:
                    user_data[user_id]['total_marks'] += round_marks
                    user_data[user_id]['round_count'] += 1
                else:
                    user_data[user_id] = {'username': username, 'total_marks': round_marks, 'round_count': 1}
        for user_id, data in user_data.items():
            average_marks = data['total_marks'] / data['round_count']
            winner1_collection.update_one(
                {'user_id': user_id},
                {'$set': {'username': data['username'], 'average_marks': average_marks}},
                upsert=True
            )
        return redirect(url_for('competition_selection'))
    else:
        competition1_users = events_collection.find({'event_name': 'Competition 1'})
        return render_template('competition1.html', competition1_users=competition1_users)

@app.route('/competition2', methods=['GET', 'POST'])
def competition2():
    # Restrict admin from entering marks for competition2
    if 'role' in session and session['role'] != 'admin1':
        return render_template('error.html', message="Admin is not allowed to enter marks for Competition 2.")

    if request.method == 'POST':
        user_data = {}
        for key, value in request.form.items():
            if key.startswith('round1_') or key.startswith('round2_'):
                user_id = key.split('_')[1]
                round_number = key.split('_')[0][-1]
                round_marks = int(value)
                competition2_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {f'round{round_number}_marks': round_marks}},
                    upsert=True
                )
                user_info = users_collection.find_one({'_id': user_id})
                username = user_info.get('username', 'Unknown')
                if user_id in user_data:
                    user_data[user_id]['total_marks'] += round_marks
                    user_data[user_id]['round_count'] += 1
                else:
                    user_data[user_id] = {'username': username, 'total_marks': round_marks, 'round_count': 1}
        for user_id, data in user_data.items():
            average_marks = data['total_marks'] / data['round_count']
            winner2_collection.update_one(
                {'user_id': user_id},
                {'$set': {'username': data['username'], 'average_marks': average_marks}},
                upsert=True
            )
        return redirect(url_for('competition_selection'))
    else:
        competition2_users = events_collection.find({'event_name': 'Competition 2'})
        return render_template('competition2.html', competition2_users=competition2_users)

@app.route('/winner1', methods=['GET'])
def winner1():
    # Restrict admin from viewing the winner1 page
    if 'role' in session and session['role'] != 'admin1':
        return render_template('error.html', message="Admin is not allowed to view this page.")

    winners_cursor = winner2_collection.find().sort('average_marks', pymongo.DESCENDING).limit(2)
    winners_list = list(winners_cursor)
    return render_template('winner1.html', winners=winners_list)



@app.route('/winner', methods=['GET'])
def winner():
    if 'role' in session and session['role'] != 'admin':
        return render_template('error.html', message="Admin is not allowed to view this page.")
    # Retrieve the first two winners from the winner1 collection
    winners_cursor = winner1_collection.find().sort('average_marks', pymongo.DESCENDING).limit(2)
    winners_list = list(winners_cursor)
    return render_template('winner.html', winners=winners_list)




if __name__ == '__main__':
    app.run(debug=True)
