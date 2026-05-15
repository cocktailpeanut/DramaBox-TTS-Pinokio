import os
import sys

from mmgp import offload, profile_type


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "app")
SRC_DIR = os.path.join(APP_DIR, "src")

sys.path.insert(0, SRC_DIR)
sys.path.insert(0, APP_DIR)

import inference_server  # noqa: E402
import torch  # noqa: E402


_original_load_all = inference_server.TTSServer._load_all


def _profile_from_env():
    profiles = {
        "1": profile_type.HighRAM_HighVRAM,
        "2": profile_type.HighRAM_LowVRAM,
        "3": profile_type.LowRAM_HighVRAM,
        "4": profile_type.LowRAM_LowVRAM,
        "5": profile_type.VerylowRAM_LowVRAM,
        "highram_highvram": profile_type.HighRAM_HighVRAM,
        "highram_lowvram": profile_type.HighRAM_LowVRAM,
        "lowram_highvram": profile_type.LowRAM_HighVRAM,
        "lowram_lowvram": profile_type.LowRAM_LowVRAM,
        "verylowram_lowvram": profile_type.VerylowRAM_LowVRAM,
    }
    key = os.environ.get("MMGP_PROFILE", "5").strip().lower()
    if key and key != "auto":
        return profiles.get(key, profile_type.VerylowRAM_LowVRAM)
    try:
        total_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
    except Exception:
        return profile_type.VerylowRAM_LowVRAM
    if total_gb >= 24:
        return profile_type.HighRAM_HighVRAM
    if total_gb >= 17:
        return profile_type.HighRAM_LowVRAM
    if total_gb >= 13:
        return profile_type.LowRAM_LowVRAM
    return profile_type.VerylowRAM_LowVRAM


def _load_all_with_mmgp(self):
    _original_load_all(self)
    pipe = {
        "text_encoder": self._prompt_encoder,
        "audio_conditioner": self._audio_conditioner,
        "transformer": self._velocity_model,
        "vae": self._audio_decoder,
    }
    offload.profile(pipe, _profile_from_env())


inference_server.TTSServer._load_all = _load_all_with_mmgp

import app as dramabox_app  # noqa: E402


if __name__ == "__main__":
    port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
    # MMGP mutates/offloads modules at runtime. Keep low-VRAM generations
    # serialized so two requests cannot race the same CPU/GPU module state.
    dramabox_app.app.queue(max_size=2, default_concurrency_limit=1).launch(
        server_name="127.0.0.1",
        server_port=port,
        share=os.environ.get("GRADIO_SHARE", "0") == "1",
        ssr_mode=False,
        show_api=False,
    )
