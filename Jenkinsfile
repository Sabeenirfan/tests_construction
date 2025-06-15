pipeline {
    agent any

    environment {
        APP_PORT_HOST = '3002'          // Port exposed on the host
        APP_PORT_CONTAINER = '3000'     // App listens on this inside container
        APP_NAME = 'construction-app'
        CONTAINER_NAME = 'app_container'
        TEST_IMAGE = 'python:3.12-slim'
        DISPLAY = ':99'
        BASE_URL = "http://$CONTAINER_NAME:$APP_PORT_CONTAINER"
    }

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
                        echo "🔨 Building Docker image..."
                        docker build -t $APP_NAME .

                        echo "🧼 Removing existing container if exists..."
                        docker rm -f $CONTAINER_NAME || true

                        echo "🔗 Creating network if not exists..."
                        docker network create test_net || true

                        echo "🚀 Running the container..."
                        docker run -d \
                            --name $CONTAINER_NAME \
                            --network test_net \
                            -p $APP_PORT_HOST:$APP_PORT_CONTAINER \
                            $APP_NAME

                        echo "⏳ Waiting for the app to start..."
                        for i in {1..15}; do
                            if curl -s http://localhost:$APP_PORT_HOST > /dev/null; then
                                echo "✅ App is up and running!"
                                break
                            fi
                            echo "Attempt $i: App not ready yet, waiting..."
                            sleep 5
                        done

                        echo "🔍 Final health check..."
                        if ! curl -s http://localhost:$APP_PORT_HOST > /dev/null; then
                            echo "❌ App failed to start properly."
                            docker logs $CONTAINER_NAME
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
                                echo "🧪 Running Selenium tests..."
                                docker run --rm \
                                    --network test_net \
                                    -v $PWD:/tests -w /tests \
                                    $TEST_IMAGE bash -c "
                                        set -e
                                        apt-get update -qq
                                        apt-get install -y -qq wget unzip curl chromium chromium-driver xvfb

                                        echo '📦 Installing Python requirements...'
                                        pip install --no-cache-dir --upgrade pip
                                        pip install --no-cache-dir -r requirement.txt

                                        echo '🎬 Running tests with Xvfb...'
                                        Xvfb $DISPLAY -screen 0 1024x768x24 > /dev/null 2>&1 &
                                        export DISPLAY=$DISPLAY
                                        pytest --maxfail=1 --disable-warnings -v --tb=short
                                    "
                            '''
                        } catch (e) {
                            echo "⚠️ Selenium tests failed: ${e.getMessage()}"
                            sh 'docker logs $CONTAINER_NAME || true'
                            throw e
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            echo '🧹 Performing cleanup (excluding running app container)...'
            script {
                try {
                    sh '''
                        echo "Cleaning up exited containers..."
                        docker ps -a --filter "status=exited" --filter "name!=app_container" --quiet | xargs -r docker rm

                        echo "Removing dangling images and volumes..."
                        docker system prune -f --volumes || true
                    '''
                } catch (e) {
                    echo "⚠️ Cleanup warning: ${e.getMessage()}"
                }
            }
        }

        failure {
            echo '❌ Pipeline failed. Debug information:'
            script {
                try {
                    sh '''
                        docker ps -a
                        docker logs $CONTAINER_NAME || echo "No logs found for app container"
                    '''
                } catch (e) {
                    echo "⚠️ Failed to collect logs: ${e.getMessage()}"
                }
            }
        }

        success {
            echo '✅ Pipeline succeeded and app is running on port 3002.'
        }
    }
}
