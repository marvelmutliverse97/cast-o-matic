pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from Git...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing packages...'
                bat 'py -3.11 -m venv venv || "C:\\Program Files\\Python311\\python.exe" -m venv venv'
                echo 'Installing requirements...'
                bat '.\\venv\\Scripts\\pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Cast-O-Matic Docker container image...'
                bat 'docker build -t cast-o-matic:latest .'
            }
        }

        stage('Deploy / Verify') {
            steps {
                echo 'Verifying local Docker image build...'
                bat 'docker images cast-o-matic'
            }
        }
    }

    post {
        success {
            echo '🎉 Cast-O-Matic CI/CD Pipeline executed successfully from start to finish!'
        }
        failure {
            echo '❌ Pipeline failed during execution. Check the stage logs above.'
        }
    }
}