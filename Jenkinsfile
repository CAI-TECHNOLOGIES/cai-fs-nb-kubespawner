pipeline {
    agent any
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Clone repository') {
            steps {
                script {
                        checkout scm
                }
            }
        }
        stage('Build docker image') {
            steps {
                script {
                        app = docker.build('lib')
                    }
            }
        }
        stage('Store files') {
            steps {
                script {
                        app.withRun(){ c ->
                            sh "docker cp ${c.id}:/cai-fs-nb-kubespawner/dist /base/build"
                        }
                }
            }
        }
    }
}
