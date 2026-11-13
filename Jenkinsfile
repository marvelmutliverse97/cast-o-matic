pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }
stage('Install Dependencies') {
    steps {
        echo 'Setting up Python virtual environment & installing dependencies...'
        bat 'C:\\Users\\Bindu Narayani\\AppData\\Local\\Programs\\Python\\Python314\\python.exe -m venv venv'
        bat '.\\venv\\Scripts\\pip install -r requirements.txt'
    }
}

        stage('Build Docker Image') {
            steps {
                echo 'Building Cast-O-Matic Docker image...'
                bat 'docker build -t cast-o-matic:latest .'
            }
        }

        stage('Deploy / Verify') {
            steps {
                echo 'Cast-O-Matic pipeline stage completed successfully!'
            }
        }
    }

    post {
        success {
            echo 'Cast-O-Matic CI/CD Pipeline executed successfully!'
        }
        failure {
            echo ' Pipeline failed during execution. Check logs.'
        }
    }
}