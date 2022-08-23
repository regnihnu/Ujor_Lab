#!/bin/sh

cd /mnt/h/ujor_lab

git checkout main
echo ">>> Pulling remote branch ujor_lab/main into local branch main"
git pull ujor_lab_hieu main
echo

BRANCHES=`git branch --format="%(refname)"`
for BRANCH in $BRANCHES; do
BRANCH=`basename $BRANCH`
if [ "$BRANCH" != "main" ]; then
	git checkout $BRANCH
	echo ">>> Merging updated local branch main into branch $BRANCH"
	git merge main
	echo
fi
done
