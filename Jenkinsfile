#!/usr/bin/env groovy

pipeline {
    agent { label 'lhcbci-cernvm' }
    parameters {
        string(name: 'Pilot_repo', defaultValue: 'DIRACGrid', description: 'The Pilot repo')
        string(name: 'Pilot_branch', defaultValue: 'master', description: 'The Pilot branch')
        string(name: 'DIRAC_test_repo', defaultValue: 'DIRACGrid', description: 'The DIRAC repo to use for getting the test code')
        string(name: 'DIRAC_test_branch', defaultValue: 'rel-v6r20', description: 'The DIRAC branch to use for getting the test code')
        string(name: 'DIRAC_install_repo', defaultValue: 'DIRACGrid', description: 'The DIRAC repo to use for installing DIRAC')
        string(name: 'DIRAC_install_branch', defaultValue: 'v6r20p25', description: 'The DIRAC version to install (tag or branch)')
    }
    stages {
        stage('GET') {
            steps {
                echo "Here getting the code"

                sh """
                    mkdir -p $PWD/TestCode
                    cd $PWD/TestCode

                    git clone https://github.com/${params.Pilot_repo}/Pilot.git
                    cd Pilot
                    git checkout ${params.Pilot_branch}
                    cd ..

                    git clone https://github.com/${params.DIRAC_test_repo}/DIRAC.git
                    cd DIRAC
                    git checkout ${params.DIRAC_test_branch}
                    cd ../..
                """

                echo "Got the test code"
            }
        }
        stage('SourceAndInstall') {
            steps {
                echo "Sourcing and installing"

                sh """
                    set -e
                    source $WORKSPACE/TestCode/Pilot/tests/CI/pilot_ci.sh

                    export DIRACSETUP=LHCb-Certification
                    export JENKINS_QUEUE=jenkins-queue_not_important
                    export JENKINS_SITE=DIRAC.Jenkins.ch

                    fullPilot

                    cd $WORKSPACE/PilotInstallDIR
                    source $WORKSPACE/PilotInstallDIR/environmentLHCbDirac
                """

                echo "**** Pilot INSTALLATION DONE ****"
            }
        }
        stage('Test') {
            steps {
                echo "Starting the tests"
            }
        }
    }
    post {
        always {
            echo 'One way or another, I have finished'
            cleanWs() /* clean up our workspace */
        }
        success {
            echo 'I succeeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
}