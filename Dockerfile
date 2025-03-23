# Use Python 3.10 as a parent image
FROM python:3.10-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir requests

# Run script.py when the container launches
CMD ["python", "-u", "script.py"]
