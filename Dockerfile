#Python image 

FROM python:2.7

#Developer
LABEL maintainer="Pitson Mwakabila"

#Copy app.py
COPY . /app

#Work directory
WORKDIR /app

#Installing the requirements 
RUN pip install -r requirements.txt


#Expose port 3111
EXPOSE 3111

#Initialize tne database
CMD ['python', 'init_db.py']

# command to run on container start
CMD [ "python", "app.py" ]

