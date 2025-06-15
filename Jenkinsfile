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
                        echo "Waiting for app to start..."
                        for i in {1..15}; do
                            if curl -s http://localhost:3002 > /dev/null; then
                                echo "App is up and running!"
                                break
                            fi
                            echo "Attempt $i: App not ready yet, waiting..."
                            sleep 5
                        done
                        
                        # Final check
                        if ! curl -s http://localhost:3002 > /dev/null; then
                            echo "App failed to start properly"
                            docker logs app_container
                            exit 1
                        fi
                    '''
                }
            }
        }
        stage('Run Selenium Tests') {
            steps {
                dir('tests') {
                    script {
                        try {
                            sh '''
                                echo "Starting Selenium tests..."
                                docker run --rm \
                                    --network host \
                                    -v $PWD:/tests \
                                    -w /tests \
                                    python:3.12-slim bash -c "
                                        echo 'Installing system dependencies...' && \
                                        apt-get update -qq && \
                                        apt-get install -y -qq \
                                            wget \
                                            unzip \
                                            curl \
                                            chromium \
                                            chromium-driver \
                                            xvfb && \
                                        echo 'Installing Python dependencies...' && \
                                        pip install --no-cache-dir -q -r requirement.txt && \
                                        echo 'Running tests...' && \
                                        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & \
                                        export DISPLAY=:99 && \
                                        pytest --maxfail=1 --disable-warnings -v --tb=short
                                    "
                            '''
                        } catch (Exception e) {
                            echo "Test execution failed: ${e.getMessage()}"
                            sh 'docker logs app_container || true'
                            throw e
                        }
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                try {
                    sh '''
                        echo "Cleaning up containers..."
                        docker rm -f app_container || true
                        docker system prune -f || true
                    '''
                } catch (Exception e) {
                    echo "Cleanup warning: ${e.getMessage()}"
                }
            }
            echo 'Cleanup completed.'
        }
        failure {
            echo 'Pipeline failed. Check the logs above for details.'
            script {
                try {
                    sh 'docker ps -a'
                    sh 'docker logs app_container || echo "No app_container logs available"'
                } catch (Exception e) {
                    echo "Could not retrieve debug info: ${e.getMessage()}"
                }
            }
        }
        success {
            echo 'Pipeline completed successfully! All tests passed.'
        }
    }
}
