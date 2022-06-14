#!/bin/sh

git checkout main
echo ">>> Pulling remote branch ujor_lab/main into local branch main"
git pull ujor_lab main

BRANCHES=`git branch --format="%(refname)"`
for BRANCH in $BRANCHES; do
if [ "$BRANCH" != *"main"* ]; then
	git checkout ${BRANCH}
	echo ">>> Merging local branch main into branch $BRANCH"
	git merge main
fi
done

