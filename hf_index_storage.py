import os
import sys
import shutil
import logging
from pathlib import Path
from dotenv import load_dotenv

from huggingface_hub import HfApi, hf_hub_download, list_repo_files

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

HF_TOKEN        = os.environ.get("HF_TOKEN", "")
HF_REPO_ID      = os.environ.get("HF_REPO_ID", "")
LOCAL_INDEX_DIR = Path(__file__).resolve().parent / "data" / "indexes"
REPO_FOLDER     = "indexes"
REPO_TYPE       = "dataset"


def push_indexes() -> None:

    if not HF_TOKEN or not HF_REPO_ID:
        raise ValueError("HF_TOKEN and HF_REPO_ID must be set in .env")

    files = [f for f in LOCAL_INDEX_DIR.iterdir()
             if f.is_file() and f.suffix in (".index", ".pkl")]

    if not files:
        raise FileNotFoundError(f"No files found in {LOCAL_INDEX_DIR}")

    api = HfApi()
    api.create_repo(repo_id=HF_REPO_ID, repo_type=REPO_TYPE,
                    token=HF_TOKEN, exist_ok=True)

    for fp in files:
        path_in_repo = f"{REPO_FOLDER}/{fp.name}"
        logger.info("Uploading %s ...", fp.name)
        api.upload_file(
            path_or_fileobj=str(fp),
            path_in_repo=path_in_repo,
            repo_id=HF_REPO_ID,
            repo_type=REPO_TYPE,
            token=HF_TOKEN,
        )

    logger.info("Pushed %d files to %s", len(files), HF_REPO_ID)


def pull_indexes() -> None:
    
    if not HF_TOKEN or not HF_REPO_ID:
        raise ValueError("HF_TOKEN and HF_REPO_ID must be set in environment")

    LOCAL_INDEX_DIR.mkdir(parents=True, exist_ok=True)

    all_files = list(list_repo_files(
        repo_id=HF_REPO_ID, repo_type=REPO_TYPE, token=HF_TOKEN
    ))
    remote_files = [f for f in all_files if f.startswith(f"{REPO_FOLDER}/")]

    if not remote_files:
        raise RuntimeError(
            f"No files found under {REPO_FOLDER}/ in {HF_REPO_ID}. "
            "Run `python hf_index_storage.py push` first."
        )

    for remote_path in remote_files:
        filename = Path(remote_path).name
        dest = LOCAL_INDEX_DIR / filename

        if dest.exists():
            logger.info("Already exists, skipping: %s", filename)
            continue

        logger.info("Downloading %s ...", filename)
        downloaded = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=remote_path,
            repo_type=REPO_TYPE,
            token=HF_TOKEN,
        )

        shutil.copy2(os.path.realpath(downloaded), str(dest))

    logger.info("Pulled %d files to %s", len(remote_files), LOCAL_INDEX_DIR)


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("push", "pull"):
        print("Usage: python hf_index_storage.py [push|pull]")
        sys.exit(1)

    if sys.argv[1] == "push":
        push_indexes()
    else:
        pull_indexes()

