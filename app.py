import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging, time 


"""
Used python3 against the old 2.7 in the project
"""
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    
    #Timing 
    c_time = time.localtime()
    f_time = time.strftime("%m/%d/%Y %H:%M:%S", c_time)

    if post is None:
      #Log 404 
      app.logger.error("%s" + ", A non-existent article accessed. Error: 404 (not found)", f_time)
      
      return render_template('404.html'), 404
    else:
      #Log title upon retrieval 
      app.logger.info("%s" + ", Article \"" + post['title'] + "\" retrieved", f_time)

      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    c_time = time.localtime()
    f_time = time.strftime("%m/%d/%Y %H:%M:%S", c_time)
    #Log title upon retrieval 
    app.logger.info("%s" + ", About US page is retrieved", f_time)

    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            conn_success = connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))

            if conn_success:
                c_time = time.localtime()
                f_time = time.strftime("%m/%d/%Y %H:%M:%S", c_time)
                #Log title upon retrieval 
                app.logger.info("%s" + ", Article \"" + title + "\" created", f_time)

            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

#Define the /healthz end point and its function 
@app.route('/healthz', methods=(['GET']))
def healthz():
    #Return a json object with an HTTP 200 status code and result: OK-healthy message
    return jsonify({'data':{'status':200, 'result':'OK-healthy'}})

#Define the /metrics end point and its function
@app.route('/metrics', methods=(['GET']))
def metrics():
    #Logging functionality when an the end point is reached 
    #app.logger.info("%s" + "," + "metrics" + " endpoint was reached", time.asctime())
    
    #Database connection 
    connection = get_db_connection()
    
    #Initializie the count for the connections to the db 
    conn_count = None
    
    #Check connection
    if connection:
        conn_count = 1
    else:
        conn_count = 0

    #Execute a selection query for the posts in the database and Count the number of selected rows in the database 
    
    posts_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0] #The .fetchone()[0] is more efficient than len(connection.execute('').fetchall()) efficient agan

    #posts = connection.execute('SELECT * FROM posts').fetchall() 
    #posts_count = len(posts) #Inefficient on large DB
    
    connection.close()

    #Return a json object with HTTP 200 status code, the total number of posts in the database and total connections to the database
    return jsonify({'data': {'status':200, 'db_connection_count': conn_count, 'post_count':posts_count}})

# start the application on port 3111
if __name__ == "__main__":
    #Configuring the logging functionality before running the app
   logging.basicConfig(filename='event_log.log',level=logging.DEBUG, format='%(levelname)s:%(name)s: %(message)s')

   app.run(host='0.0.0.0', port=3111, debug=True)
   #app.run(host='0.0.0.0', port=3111)

   
   
