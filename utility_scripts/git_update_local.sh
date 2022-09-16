#!/bin/sh

cd /mnt/h/ujor_lab_local || echo "No such local directory found"
remote_repo="ujor_lab_hieu"

git checkout main
echo ">>> Pulling remote branch \"$remote_repo\"/main into local branch main"
git pull $remote_repo main
echo

BRANCHES=$(git branch --format="%(refname)")
for BRANCH in $BRANCHES; do
BRANCH=$(basename $BRANCH)
if [ "$BRANCH" != "main" ]; then
	git checkout $BRANCH
	echo ">>> Merging updated local branch main into branch $BRANCH"
	git merge main
	echo
fi
done
