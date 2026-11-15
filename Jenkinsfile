
pipeline {
    agent any

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat '''
                    "C:\\Users\\Bindu Narayani\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" --version
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    "C:\\Users\\Bindu Narayani\\AppData\\Local\\Programs\\Python\\Python314\\python.exe" -m venv .venv

                    if errorlevel 1 exit /b 1

                    .venv\\Scripts\\python.exe -m pip install --upgrade pip

                    if errorlevel 1 exit /b 1

                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt

                    if errorlevel 1 exit /b 1
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '''
                    .venv\\Scripts\\python.exe -m unittest discover -s tests -t . -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker --version
                    docker build -t cast-o-matic:latest .
                '''
            }
        }
    }

    post {
        success {
            echo 'Cast-O-Matic pipeline executed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check console output.'
        }
    }
}
