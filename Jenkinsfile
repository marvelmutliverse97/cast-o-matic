pipeline {
    agent any

    stages {
        stage('Checkout SCM') {
            steps {
                echo 'Checking out code from Git...'
                checkout scm
            }
        }

        stage('Checkout Code') {
            steps {
                echo 'Verifying workspace directory...'
                bat 'dir'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Setting up Python virtual environment and installing packages...'
                bat 'C:\\Users\\Bindu Narayani\\AppData\\Local\\Programs\\Python\\Python314\\python.exe -m venv venv'
                bat '.\\venv\\Scripts\\pip install --upgrade pip'
                bat '.\\venv\\Scripts\\pip install -r requirements.txt'
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
            echo 'Cast-O-Matic CI/CD Pipeline executed successfully from start to finish!'
        }
        failure {
            echo ' Pipeline failed during execution. Check the stage logs above.'
        }
    }
}