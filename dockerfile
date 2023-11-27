# Use the official Python image as the base image
FROM python:3.8-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Retrieve Secrets from Secret Manager (during the build process)
# Ensure gcloud CLI is available in the build environment for this step
RUN --mount=type=secret,id=DB_USER \
    --mount=type=secret,id=DB_PASSWORD \
    --mount=type=secret,id=APP_SECRET_KEY \
    export DB_USER=$(cat /run/secrets/DB_USER) && \
    export DB_PASSWORD=$(cat /run/secrets/DB_PASSWORD) && \
    export APP_SECRET_KEY=$(cat /run/secrets/APP_SECRET_KEY)

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available for Flask (optional for testing)
EXPOSE 5000

# Set environment variables in the container
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV APP_SECRET_KEY=$APP_SECRET_KEY

# Run your application
CMD ["sh", "run_app.sh"]
