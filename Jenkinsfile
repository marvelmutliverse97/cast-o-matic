
pipeline {

    agent any

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    if not exist .venv (
                        python -m venv .venv
                    )

                    .venv\\Scripts\\python.exe -m pip install --upgrade pip

                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
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
            echo 'Pipeline failed. Check the console output for the failing stage.'
        }

    }
}
