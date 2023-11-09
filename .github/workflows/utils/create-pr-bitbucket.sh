#!/usr/bin/env bash

set -x

while getopts "s:d:r:b:i:t:e:m:" option;
    do
    case "$option" in
        s ) SOURCE_FOLDER=${OPTARG};;
        d ) DEST_FOLDER=${OPTARG};;
        r ) DEST_REPO=${OPTARG};;
        b ) DEST_BRANCH=${OPTARG};;
        i ) DEPLOY_ID=${OPTARG};;
        t ) TOKEN=${OPTARG};;
        m ) AUTO_MERGE=${OPTARG};;
    esac
done

set -eo pipefail  # fail on error

generate_pr_data()
{
    cat <<EOF
    {
        "title": "Deployment ${DEPLOY_ID} to ${DEST_FOLDER}-folder on ${DEST_BRANCH}-branch",
        "description": "Deployment to $DEST_FOLDER-folder ",
        "state": "OPEN",
        "open": true,
        "closed": false,
        "fromRef": {
            "id": "${DEPLOY_BRANCH_NAME}",
            "repository": {
                "slug": "${REPO_NAME}",
                "name": null,
                "project": {
                    "key": "${REPO_PROJECT}"
                }
            }
        },
        "toRef": {
            "id": "${DEST_BRANCH}",
            "repository": {
                "slug": "${REPO_NAME}",
                "name": null,
                "project": {
                    "key": "${REPO_PROJECT}"
                }
            }
        },
        "locked": false,
        "reviewers": []
        }
EOF
}

# Define variables
REPO_REST_API_URL="https://sourcecode.socialcoding.bosch.com/rest/api/1.0"
REPO_URL=${DEST_REPO}
REPO_GIT=${DEST_REPO##*/}
REPO_NAME=${REPO_GIT%.*}
REPO_PATH=${REPO_URL%/*}
REPO_PROJECT=${REPO_PATH##*/}

# Set GitOps config
PR_USER_NAME="Git Ops"
PR_USER_EMAIL="agent@gitops.com"

git config --global user.email $PR_USER_EMAIL
git config --global user.name $PR_USER_NAME

# Clone manifests repo
echo "Cloning GitOps manifests repo..."
git -c "http.extraHeader=Authorization: Bearer $TOKEN" clone $REPO_URL -b $DEST_BRANCH --depth 1 --single-branch
cd "$REPO_NAME" && git status

# Create a new branch 
DEPLOY_BRANCH_NAME=deploy/$DEPLOY_ID/$DEST_FOLDER
echo "Creating new branch $DEPLOY_BRANCH_NAME ..."
git checkout -b $DEPLOY_BRANCH_NAME

# Add generated manifests to the new deploy branch
mkdir -p $DEST_FOLDER
[ -d $SOURCE_FOLDER ] && cp -r $SOURCE_FOLDER/* $DEST_FOLDER/
git add -A
git status

if [[ `git status --porcelain | head -1` ]]; then
    git commit -m "Deployment ID $DEPLOY_ID to $DEST_FOLDER on $DEST_BRANCH-branch"

    # Push to the deploy branch 
    echo "Pushing to the deploy branch $DEPLOY_BRANCH_NAME of repo $REPO_URL"
    git -c "http.extraHeader=Authorization: Bearer $TOKEN" push --set-upstream $REPO_URL $DEPLOY_BRANCH_NAME

    # Creating PR 
    echo "Creating PR to $DEST_BRANCH"
    PR_RESPONSE=$(curl --location --request POST "${REPO_REST_API_URL}/projects/${REPO_PROJECT}/repos/${REPO_NAME}/pull-requests" \
        --header "Content-Type: application/json" \
        --header "Authorization: Bearer ${TOKEN}" \
        --data-raw "$(generate_pr_data)")

    if [[ "$AUTO_MERGE" == "Y" ]]; then
        # TO-DO: MERGE PR
        echo "TO-DO. Not implemented."
    fi
fi