from os import environ
from os import path as ospath
from subprocess import run as srun
from dotenv import load_dotenv

load_dotenv('config.env' , override=True)

if ospath.exists("log.txt"):
    with open("log.txt", "r+") as f:
        f.truncate(0)

UPSTREAM_REPO = environ.get("UPSTREAM_REPO")
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = None

UPSTREAM_BRANCH = environ.get("UPSTREAM_BRANCH")
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = "main"

if UPSTREAM_REPO is not None:
    if ospath.exists(".git"):
        srun(["rm", "-rf", ".git"])

    update = srun(
        [
            f"git init -q \
                     && git config --global user.email evendeadiamthehero04@gmail.com \
                     && git config --global user.name evendeadiamthehero04 \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"
        ],
        shell=True,
    )

    if update.returncode == 0:
        print("Successfully updated with latest commit from UPSTREAM_REPO")
    else:
        print(
            "Something went wrong while updating, check UPSTREAM_REPO if valid or not!"
        )