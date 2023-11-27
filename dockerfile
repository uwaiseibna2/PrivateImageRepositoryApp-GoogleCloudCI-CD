# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available for Flask (optional for testing)
EXPOSE 5000

# Arguments to pass secrets during build
ARG DB_USER
ARG DB_PASSWORD
ARG APP_SECRET_KEY

# Set environment variables in the container (optional)
ENV DB_USER=$DB_USER \
    DB_PASSWORD=$DB_PASSWORD \
    APP_SECRET_KEY=$APP_SECRET_KEY

# Run your application
CMD ["sh", "run_app.sh"]
