pipeline {
    agent { label 'docker' }
    options { timestamps(); disableConcurrentBuilds() }
    environment { IMAGE = 'opencv-edge-mvp' }
    stages {
        stage('Build test image') {
            steps { sh 'docker build --target test -t ${IMAGE}:ci .' }
        }
        stage('Unit and integration tests') {
            steps { sh 'docker run --rm -v "$WORKSPACE:/app" ${IMAGE}:ci python -m pytest -q --junitxml=/app/junit.xml' }
        }
        stage('Build runtime image') {
            steps { sh 'docker build --target runtime -t ${IMAGE}:latest .' }
        }
    }
    post {
        always { junit testResults: 'junit.xml', allowEmptyResults: true }
    }
}
