pipeline {
    agent any
    stages {
        stage('Clone Repositories') {
            steps {
                // Clone application code
                dir('app') {
                    git branch: 'main', url: 'https://github.com/Sabeenirfan/construction.git'
                }
                // Clone test code
                dir('tests') {
                    git branch: 'main', url: 'https://github.com/Sabeenirfan/tests_construction.git'
                }
            }
        }

        stage('Run Tests Inside Docker') {
            steps {
                dir('tests') {
                    sh '''
                        docker run --rm \
                            -v $PWD:/tests \
                            -v $WORKSPACE/app:/app \
                            -w /tests \
                            python:3.12 bash -c "
                                apt-get update && \
                                apt-get install -y chromium chromium-driver && \
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
            sh 'docker system prune -f || true'
        }
        failure {
            echo 'Pipeline failed. Check the logs above for details.'
        }
        success {
            echo 'Pipeline completed successfully!'
             // Clone application code
             // Clone application code
            //clome
        }
    }
}
