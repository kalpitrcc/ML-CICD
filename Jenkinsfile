def modelpath = ""

pipeline {
  agent {
    kubernetes {
      yaml '''
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: git
            image: alpine/git:latest
            command:
            - cat
            tty: true
          - name: docker
            image: docker:latest
            command:
            - cat
            tty: true
            volumeMounts:
             - mountPath: /var/run/docker.sock
               name: docker-sock
          volumes:
          - name: docker-sock
            hostPath:
              path: /var/run/docker.sock    
        '''
    }
  }

				environment {
					modelpath = ""

				DOCKER_HUB_CREDENTIALS = credentials('DEVSDS_DOCKERHUB')

				}
	

 stages {
    stage('Clone') {
      steps {
        container('git') {
          git branch: 'main', changelog: false, poll: false, url: 'https://github.com/kalpitrcc/cicd.git'
        }
      }
    }
   stage('Docker Login') {
      steps {
        container('docker') {
          sh 'echo $DOCKER_HUB_CREDENTIALS_PSW | docker login -u $DOCKER_HUB_CREDENTIALS_USR --password-stdin'
      
      }
    }
    }
    stage('Build Training Image') {
      steps {
        container('docker') {
          sh 'cd model-training/ && docker build -t devsds/modeltraining:$BUILD_NUMBER . ' 
        }
      }
    }
    
     stage('Push Training Image') {
      steps {
        container('docker') {
          sh 'docker push devsds/modeltraining:$BUILD_NUMBER'
      }
    }
   }
   stage('Pre Processing') {
      agent {
        kubernetes {
          yaml """
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: preprocessing
            image: "devsds/modeltraining:${BUILD_NUMBER}"
            env: 
            - name: RAW_DATA_DIR 
              value: "/data/raw"
            - name: RAW_DATA_FILE
              value: "adult.csv"
            - name: PROCESSED_DATA_DIR
              value: "/data/processed"
            command:
            - cat
            tty: true
            volumeMounts:
            - mountPath: "/home/jovyan/results/*"
              name: "workspace-volume"
            - mountPath: "/data"
              name: "dataset"
          volumes:
            - name: "workspace-volume"
              persistentVolumeClaim:
                claimName: claim1    
            - name: "dataset"
              persistentVolumeClaim:
                claimName: dataset

        """.stripIndent()
        }
      }
      
      steps {
        container('preprocessing') { 
	        sh 'python /app/preprocessing.py'
          
        }
      }
    }
   
   stage('Training') {
      agent {
        kubernetes {
          yaml """
        apiVersion: v1
        kind: Pod
        spec:
          containers:
          - name: modeltraining
            image: "devsds/modeltraining:${BUILD_NUMBER}"
            env: 
            - name: MLFLOW_S3_ENDPOINT_URL 
              value: "http://10.1.100.147:10019"
            - name: AWS_ACCESS_KEY_ID
              value: "admin"
            - name: PROCESSED_DATA_DIR
              value: "/data/processed"
            - name: AWS_SECRET_ACCESS_KEY
              value: "admin123"
            - name: MLFLOW_TRACKING_URI
              value: "http://10.1.100.147:10020"
            command:
            - cat
            tty: true
            volumeMounts:
            - mountPath: "/home/jovyan/results/*"
              name: "workspace-volume"
            - mountPath: "/data"
              name: "dataset"
          volumes:
            - name: "workspace-volume"
              persistentVolumeClaim:
                claimName: claim1    
            - name: "dataset"
              persistentVolumeClaim:
                claimName: dataset

        """.stripIndent()
        }
      }
      
      steps {
        container('modeltraining') { 
		script{
			modelpath = sh(returnStdout: true, script: "python /app/training.py | grep -Eo   's3://[a-zA-Z0-9./?=_-]*' ")
			//modelpath = sh(returnStdout: true, script: "python /app/training.py")
			echo "${modelpath}"
		}             
        }
      }
    }
    stage('Build Model Deployment Image') {
      steps {
        container('docker') {
          sh 'cd model-deployment/ && docker build -t devsds/modeldeployment:$BUILD_NUMBER . ' 
        }
      }
    }
    
     stage('Push Model Deployment Image') {
      steps {
        container('docker') {
          sh 'docker push devsds/modeldeployment:$BUILD_NUMBER'
      }
    }
   }
   
   stage('Deploy Model'){
     steps{
	     
	     script{
	     env.modelpath = modelpath
	     }
	echo "${modelpath}"
	
       sh '''sed -i "s#@@@PREDICTION_SERVER@@@#modeldeployment:${BUILD_NUMBER}#g" model-deployment/prediction-server.yaml '''
	     sh '''sed -i "s#@@@MODELPATH@@@#${modelpath}#g" model-deployment/prediction-server.yaml '''
       sh 'cat model-deployment/prediction-server.yaml'
       sh 'kubectl get pods'
	
     }
   }
   
  }
    post {
      always {
        container('docker') {
          sh 'docker rmi devsds/modeltraining:${BUILD_NUMBER} -f'
          sh 'docker rmi devsds/modeldeployment:${BUILD_NUMBER} -f'
        }
      }
    }
}
