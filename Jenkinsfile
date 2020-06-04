pipeline {
    agent any
    stages {
        stage('install dependencies') {
            steps {
                sh 'python3 --version'
                sh 'pip3 install --user -r dev_requirements.txt'
            }
        }
        stage('run test suites') {
            steps {
                sh 'export PATH=$PATH:/home/jenkins/.local/bin && pytest -v'
            }
        }
    }
}
