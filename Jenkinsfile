pipeline {
    agent any
    stages {
        stage('Clone Repositories') {
            steps {
                dir('app') {
                    git branch: 'main', url: 'https://github.com/Sabeenirfan/construction.git'
                }
                dir('tests') {
                    git branch: 'main', url: 'https://github.com/Sabeenirfan/tests_construction.git'
                }
            }
        }

        stage('Build and Run App Container') {
            steps {
                dir('app') {
                    sh '''
                        docker build -t construction-app .
                        docker rm -f app_container || true
                        docker run -d --name app_container -p 3002:3002 construction-app
                        # Wait until app is up
                        for i in {1..10}; do
                            if curl -s http://localhost:3002 > /dev/null; then
                                echo "App is up!"
                                break
                            fi
                            echo "Waiting for app..."
                            sleep 3
                        done
                    '''
                }
            }
        }

        stage('Run Tests Inside Docker') {
            steps {
                dir('tests') {
                    sh '''
                        docker run --rm \
                            --network host \  # allows access to localhost:3002
                            -v $PWD:/tests \
                            -v $WORKSPACE/app:/app \
                            -w /tests \
                            python:3.12 bash -c "
                                apt-get update && \
                                apt-get install -y chromium chromium-driver curl && \
                                pip install -r requirement.txt && \
                                pytest --maxfail=1 --disable-warnings -v
                            "
                    '''
                }
            }
        }
    }

    post {
        always {
            sh '''
                docker rm -f app_container || true
                docker system prune -f || true
            '''
        }
        failure {
            echo 'Pipeline failed. Check the logs above for details.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}
