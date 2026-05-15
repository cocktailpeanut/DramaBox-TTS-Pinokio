import os
import sys


port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
root_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(root_dir, "app")
src_dir = os.path.join(app_dir, "src")

os.chdir(app_dir)
sys.path.insert(0, src_dir)
sys.path.insert(0, app_dir)

import model_downloader  # noqa: E402


def _patch_hf_downloads_for_windows():
    from huggingface_hub import hf_hub_download, snapshot_download

    cache_root = os.path.abspath(model_downloader.DEFAULT_CACHE)
    local_root = os.path.join(cache_root, "local")
    dramabox_dir = os.path.join(local_root, "ResembleAI--Dramabox")
    gemma_dir = os.path.join(local_root, "unsloth--gemma-3-12b-it-bnb-4bit")

    def get_model_path(name: str, cache_dir: str = None) -> str:
        if name not in model_downloader.MODEL_FILES:
            raise ValueError(f"Unknown model: {name}. Choose from: {list(model_downloader.MODEL_FILES.keys())}")
        repo_path = model_downloader.MODEL_FILES[name]
        model_downloader.logger.info(f"Fetching {name} from {model_downloader.DRAMABOX_REPO}/{repo_path}...")
        local_path = hf_hub_download(
            repo_id=model_downloader.DRAMABOX_REPO,
            filename=repo_path,
            cache_dir=cache_root,
            local_dir=dramabox_dir,
            token=os.environ.get("HF_TOKEN"),
        )
        model_downloader.logger.info(f"  -> {local_path}")
        return local_path

    def get_gemma_path(cache_dir: str = None) -> str:
        model_downloader.logger.info(f"Fetching Gemma from {model_downloader.GEMMA_REPO}...")
        local_dir = snapshot_download(
            repo_id=model_downloader.GEMMA_REPO,
            cache_dir=cache_root,
            local_dir=gemma_dir,
            token=os.environ.get("HF_TOKEN"),
            max_workers=1,
        )
        model_downloader.logger.info(f"  -> {local_dir}")
        return local_dir

    def get_all_paths(cache_dir: str = None) -> dict:
        paths = {}
        for name in model_downloader.MODEL_FILES:
            paths[name] = get_model_path(name)
        paths["gemma_root"] = get_gemma_path()
        return paths

    model_downloader.get_model_path = get_model_path
    model_downloader.get_gemma_path = get_gemma_path
    model_downloader.get_all_paths = get_all_paths


_patch_hf_downloads_for_windows()

import app as dramabox_app  # noqa: E402


dramabox_app.app.queue(max_size=10).launch(
    server_name="127.0.0.1",
    server_port=port,
    share=os.environ.get("GRADIO_SHARE", "0") == "1",
    ssr_mode=False,
    show_api=False,
)
