# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Arguments to pass secrets during build
ARG _DB_USER
ARG _DB_PASSWORD
ARG _APP_SECRET_KEY

# Set environment variables in the container (optional)
ENV DB_USER=$_DB_USER \
    DB_PASSWORD=$_DB_PASSWORD \
    APP_SECRET_KEY=$_APP_SECRET_KEY

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available for Flask (optional for testing)
EXPOSE 5000

# Run your application
CMD ["sh", "run_app.sh"]
