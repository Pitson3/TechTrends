import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging, time, sys 

#global conn_count variable to track the connection count (Suggested by the previous project reviewer the one implemented previously)
conn_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global conn_count

    connection = sqlite3.connect('database.db')
    
    #Update conn_count after each and every connection 
    conn_count += 1

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
      logging.info("%s" + ", Article \"" + post['title'] + "\" retrieved", f_time)

      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    c_time = time.localtime()
    f_time = time.strftime("%m/%d/%Y %H:%M:%S", c_time)
    
    #Log title upon retrieval 
    logging.info("%s" + ", About US page is retrieved", f_time)

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
                logging.info("%s" + ", Article \"" + title + "\" created", f_time)

            connection.commit()
            connection.close()

            return redirect(url_for('index'))

    return render_template('create.html')

#Define the /healthz end point and its function 
@app.route('/healthz', methods=(['GET']))
def healthz():
    
    return jsonify({'status':200, 'result':'OK-healthy'})

#Define the /metrics end point and its function
@app.route('/metrics', methods=(['GET']))
def metrics():
    
    #Database connection 
    connection = get_db_connection()
    
    #Execute a selection query for the posts in the database and Count the number of selected rows in the database 
    
    posts_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0] #The .fetchone()[0] is more efficient than len(connection.execute('').fetchall()) efficient agan

    #posts = connection.execute('SELECT * FROM posts').fetchall() 
    #posts_count = len(posts) #Inefficient on large DB
    
    connection.close()

    return jsonify({'status':200, 'db_connection_count': conn_count, 'post_count':posts_count})

# start the application on port 3111
if __name__ == "__main__":
    #Configuring the logging functionality before running the app
    """
    Removed the stream parameter and added the handler to carter for the STDOUT and STDERR logs based on the suggestion by the reviewer at udacity
    """
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout), logging.StreamHandler(sys.stderr)], level=logging.DEBUG, format='%(levelname)s:%(name)s: %(message)s')

    app.run(host='0.0.0.0', port=3111, debug=True)
  
   
   
 