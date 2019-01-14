#!/usr/bin/env groovy

pipeline {
    agent { label 'lhcbci-cernvm' }
    stages {
        stage('Build') {
            steps {
                echo "This is build"
            }
        }
        stage('Test') {
            steps {
                echo "This is test"
            }
        }
        stage('Deploy') {
            steps {
                echo "This is deploy"
            }
        }
    }
}