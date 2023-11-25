# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Set environment variables during the build process
ARG FLASK_SECRET_KEY
ARG DB_USER
ARG DB_PASS
ARG DB_NAME
ARG CLOUD_SQL_CONNECTION_NAME

ENV FLASK_SECRET_KEY=$FLASK_SECRET_KEY
ENV DB_USER=$DB_USER
ENV DB_PASS=$DB_PASS
ENV DB_NAME=$DB_NAME
ENV CLOUD_SQL_CONNECTION_NAME=$CLOUD_SQL_CONNECTION_NAME

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available for Flask (optional for testing)
EXPOSE 5000

# Run your tests (if tests fail, the container will stop here)
CMD ["sh", "run_app.sh"]
