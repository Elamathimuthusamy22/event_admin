from flask import Flask, render_template, request, redirect, url_for
from pymongo.errors import BulkWriteError
from pymongo import MongoClient
from datetime import datetime
import pymongo

app = Flask(__name__)
app.config.from_pyfile('config.py')
client = MongoClient('mongodb://localhost:27017/')
db = client['user_login_system']
users_collection = db['users']
events_collection = db['events']
winner1_collection=db['winner1']
winner2_collection=db['winner2']

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
            return redirect(url_for('competition_selection'))
        else:
            # If username and password are invalid, render the login page again
            return render_template('login.html', error='Invalid credentials. Please try again.')
    
    return render_template('login.html')

@app.route('/competition_selection')
def competition_selection():
    return render_template('competition_selection.html')




@app.route('/competition1', methods=['GET', 'POST'])
def competition1():
    if request.method == 'POST':
        # Dictionary to store user IDs, usernames, and their total marks
        user_data = {}

        # Iterate through the submitted form data to update the marks in the database
        for key, value in request.form.items():
            if key.startswith('round1_') or key.startswith('round2_'):
                user_id = key.split('_')[1]  # Extract the user ID from the input field ID
                round_number = key.split('_')[0][-1]  # Extract the round number from the input field ID
                round_marks = int(value)

                # Update or insert the round marks into the competition1 collection
                competition1_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {f'round{round_number}_marks': round_marks}},
                    upsert=True  # Create a new document if it doesn't exist
                )

                # Retrieve the username from the users table
                user_info = users_collection.find_one({'_id': user_id})
                username = user_info.get('username', 'Unknown')  # Get the username or default to 'Unknown'

                # Update user data dictionary
                if user_id in user_data:
                    user_data[user_id]['total_marks'] += round_marks
                    user_data[user_id]['round_count'] += 1
                else:
                    user_data[user_id] = {'username': username, 'total_marks': round_marks, 'round_count': 1}

        # Calculate average marks for each user
        for user_id, data in user_data.items():
            average_marks = data['total_marks'] / data['round_count']
            # Update or insert the winner data into the winner1 collection
            winner1_collection.update_one(
                {'user_id': user_id},
                {'$set': {'username': data['username'], 'average_marks': average_marks}},
                upsert=True  # Create a new document if it doesn't exist
            )

        return redirect(url_for('competition_selection'))

    else:
        # Retrieve the list of users participating in competition1 from the events_collection
        competition1_users = events_collection.find({'event_name': 'Competition 1'})
        return render_template('competition1.html', competition1_users=competition1_users)
@app.route('/winner', methods=['GET'])
def winner():
    # Retrieve the first two winners from the winner1 collection
    winners_cursor = winner1_collection.find().sort('average_marks', pymongo.DESCENDING).limit(2)
    winners_list = list(winners_cursor)
    return render_template('winner.html', winners=winners_list)



# @app.route('/winner')
# def winner():
#     # Calculate the average marks for each user
#     users = competition1_collection.find()
#     winners = []
#     highest_average = 0
#     for user in users:
#         round1_marks = user.get('round1_marks', 0)
#         round2_marks = user.get('round2_marks', 0)
#         average_marks = (round1_marks + round2_marks) / 2
#         if average_marks > highest_average:
#             highest_average = average_marks
#             winner = {'user_id': user['user_id'], 'username': user.get('username', 'Unknown'), 'average_marks': average_marks}
#     winners.append(winner)

#     # Redirect to the winner page with the winner's details
#     return render_template('winner.html', winner=winner)


@app.route('/competition2', methods=['GET', 'POST'])
def competition2():
    if request.method == 'POST':
        # Dictionary to store user IDs, usernames, and their total marks
        user_data = {}

        # Iterate through the submitted form data to update the marks in the database
        for key, value in request.form.items():
            if key.startswith('round1_') or key.startswith('round2_'):
                user_id = key.split('_')[1]  # Extract the user ID from the input field ID
                round_number = key.split('_')[0][-1]  # Extract the round number from the input field ID
                round_marks = int(value)

                # Update or insert the round marks into the competition1 collection
                competition2_collection.update_one(
                    {'user_id': user_id},
                    {'$set': {f'round{round_number}_marks': round_marks}},
                    upsert=True  # Create a new document if it doesn't exist
                )

                # Retrieve the username from the users table
                user_info = users_collection.find_one({'_id': user_id})
                username = user_info.get('username', 'Unknown')  # Get the username or default to 'Unknown'

                # Update user data dictionary
                if user_id in user_data:
                    user_data[user_id]['total_marks'] += round_marks
                    user_data[user_id]['round_count'] += 1
                else:
                    user_data[user_id] = {'username': username, 'total_marks': round_marks, 'round_count': 1}

        # Calculate average marks for each user
        for user_id, data in user_data.items():
            average_marks = data['total_marks'] / data['round_count']
            # Update or insert the winner data into the winner1 collection
            winner2_collection.update_one(
                {'user_id': user_id},
                {'$set': {'username': data['username'], 'average_marks': average_marks}},
                upsert=True  # Create a new document if it doesn't exist
            )

        return redirect(url_for('competition_selection'))

    else:
        # Retrieve the list of users participating in competition1 from the events_collection
        competition2_users = events_collection.find({'event_name': 'Competition 2'})
        return render_template('competition2.html', competition2_users=competition2_users)
# @app.route('/competition2', methods=['GET', 'POST'])
# def competition2():
#     if request.method == 'POST':
#         # Dictionary to store user IDs and their total marks
#         user_marks = {}

#         # Iterate through the submitted form data to update the marks in the database
#         for key, value in request.form.items():
#             if key.startswith('round1_') or key.startswith('round2_'):
#                 user_id = key.split('_')[1]  # Extract the user ID from the input field ID
#                 round_number = key.split('_')[0][-1]  # Extract the round number from the input field ID
#                 round_marks = int(value)

#                 # Update or insert the round marks into the competition1 collection
#                 competition2_collection.update_one(
#                     {'user_id': user_id},
#                     {'$set': {f'round{round_number}_marks': round_marks}},
#                     upsert=True  # Create a new document if it doesn't exist
#                 )

#                 # Update user marks dictionary
#                 if user_id in user_marks:
#                     user_marks[user_id]['total_marks'] += round_marks
#                     user_marks[user_id]['round_count'] += 1
#                 else:
#                     user_marks[user_id] = {'total_marks': round_marks, 'round_count': 1}

#         # Calculate average marks for each user
#         for user_id, marks_info in user_marks.items():
#             average_marks = marks_info['total_marks'] / marks_info['round_count']
#             # Update or insert the winner data into the winner1 collection
#             winner2_collection.update_one(
#                 {'user_id': user_id},
#                 {'$set': {'average_marks': average_marks}},
#                 upsert=True  # Create a new document if it doesn't exist
#             )

#         return redirect(url_for('competition_selection'))

#     else:
#         # Retrieve the list of users participating in competition1 from the events_collection
#         competition2_users = events_collection.find({'event_name': 'Competition 2'})
#         return render_template('competition2.html', competition2_users=competition2_users)
@app.route('/winner1', methods=['GET'])
def winner1():
    # Retrieve the first two winners from the winner1 collection
    winners_cursor = winner2_collection.find().sort('average_marks', pymongo.DESCENDING).limit(2)
    winners_list = list(winners_cursor)
    return render_template('winner1.html', winners=winners_list)

if __name__ == '__main__':
    app.run(debug=True)