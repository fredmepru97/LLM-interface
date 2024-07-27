FROM python:3.7-slim

# Set the working directory in the container

WORKDIR /app

# Copy the dependencies file to the working directory

COPY requirements.txt .

# Install any dependencies

RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory

COPY . .

EXPOSE 8501

# Specify the command to run on container start based on streamlit

CMD ["streamlit", "run", "main.py", "--server.port=8501"]