pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment{
        AWS_ACCOUNT_ID = "214346124741"
        IMAGE_NAME = "cloudnexus/daas_backend"
        ECR_REPO = "${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-2.amazonaws.com/${IMAGE_NAME}"
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/SeSAC-Cloud-dev/terraform_api.git'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                sh 'aws ecr get-login-password --region ap-northeast-2 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.ap-northeast-2.amazonaws.com'
                sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
            }
        }
        
        stage('Tag Docker Image') {
            steps {
                sh 'docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${ECR_REPO}:${BUILD_NUMBER}'
            }
        }
        
        stage('Publish Docker Image') {
            steps {
                sh 'docker push ${ECR_REPO}:${BUILD_NUMBER}'
            }
        }

        stage('clean') {
            steps {
                sh 'docker rmi ${ECR_REPO}:${BUILD_NUMBER}'
                sh 'docker rmi ${IMAGE_NAME}:${BUILD_NUMBER}'
            }
        }
    }

    post {
        always {
            script {
                //sh 'docker system prune -f'
                //  sh 'docker rmi $(docker images -q --filter "dangling=true")
                  sh 'docker builder prune -f'
            }
        }
    }

}

