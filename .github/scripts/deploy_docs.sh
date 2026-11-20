#!/usr/bin/env bash
# Deploys built docs to the gh-pages branch as a single commit with no history.
#
# usage: deploy_docs.sh <build_dir> <repository_url>
#
# Each folder in build_dir (dev, or a version and stable) replaces the folder
# of the same name on gh-pages, and everything else on gh-pages (the other
# versions, the root index.html redirect and .nojekyll) is kept. Sphinx build
# caches (.doctrees) are removed, as the site does not use them.
#
# The result is pushed as a new commit with no parent, replacing the branch,
# so gh-pages does not build up history. Every clone of the repository
# downloads every branch, so that history would otherwise grow every clone.
#
# Deploys can run at the same time (a release pushes main and a tag together),
# so the push only replaces the commit this run started from. If another
# deploy pushed first, the push is rejected and the deploy starts again from
# the new gh-pages.
#
# Set DRY_RUN=1 to build the commit without pushing it.
set -euo pipefail

build_dir=$(realpath "$1")
repository_url=$2

for attempt in 1 2 3 4 5; do
    site=$(mktemp -d)
    git clone --quiet --depth 1 --branch gh-pages --single-branch "$repository_url" "$site"
    started_from=$(git -C "$site" rev-parse HEAD)

    for folder in "$build_dir"/*/; do
        name=$(basename "$folder")
        rm -rf "${site:?}/$name"
        cp -r "$folder" "$site/$name"
    done
    find "$site" -mindepth 2 -maxdepth 2 -type d -name .doctrees -exec rm -rf {} +

    git -C "$site" checkout --quiet --orphan deploy
    git -C "$site" add --all
    git -C "$site" \
        -c user.name="github-actions[bot]" \
        -c user.email="41898282+github-actions[bot]@users.noreply.github.com" \
        commit --quiet --message "Deploy docs from ${GITHUB_SHA:-a local build}"

    if [ "${DRY_RUN:-0}" = "1" ]; then
        echo "dry run, commit $(git -C "$site" rev-parse HEAD) in $site was not pushed"
        exit 0
    fi
    if git -C "$site" push --quiet --force-with-lease="gh-pages:$started_from" origin deploy:gh-pages; then
        echo "deployed $(ls "$build_dir" | tr '\n' ' ')to gh-pages"
        rm -rf "$site"
        exit 0
    fi
    echo "gh-pages changed during deploy attempt $attempt, starting again"
    rm -rf "$site"
    sleep $((attempt * 10))
done
echo "could not deploy after 5 attempts" >&2
exit 1
