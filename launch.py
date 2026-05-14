import os
import sys


port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
app_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(app_dir, "app")

os.chdir(app_dir)
sys.path.insert(0, app_dir)

import app as dramabox_app  # noqa: E402


dramabox_app.app.queue(max_size=10).launch(
    server_name="127.0.0.1",
    server_port=port,
    share=os.environ.get("GRADIO_SHARE", "0") == "1",
    ssr_mode=False,
    show_api=False,
)
