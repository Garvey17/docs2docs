FROM python:3.12-slim 

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

#Set working directory

WORKDIR /app

# Install Linux packages required by Chromium/Playwright
RUN apt-get update && apt-get install -y \ 
    libnss3 \ 
    libatk1.0-0 \ 
    libatk-bridge2.0-0 \ 
    libcups2 \ 
    libdrm2 \ 
    libxkbcommon0 \ 
    libxcomposite1 \ 
    libxdamage1 \ 
    libxfixes3 \ 
    libxrandr2 \ 
    libgbm1 \ 
    libasound2 \
    libasound2t64 \ 
    curl \ 
    && rm -rf /var/lib/apt/lists/*

#Copy dependencies from requirements.txt to root of working dir
COPY requirements.txt .

#Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#Install Playwright browser binaries
RUN playwright install chromium 

#Copy project code
COPY . .

#Expose FastAPI port
EXPOSE 8000

#Start FastAPI application
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" , "--timeout-keep-alive", "300"]
