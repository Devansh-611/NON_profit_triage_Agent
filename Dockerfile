FROM python:3.10

# Set working directory
WORKDIR /app

# Copy all files into container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Streamlit default port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]