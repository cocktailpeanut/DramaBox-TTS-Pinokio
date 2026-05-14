module.exports = {
  daemon: true,
  run: [
    {
      method: "shell.run",
      params: {
        venv: "env",
        env: {},
        path: "app",
        message: ["python app.py"],
        on: [{
          // Gradio prints 0.0.0.0 — browsers on Windows need loopback for "Open Web UI"
          event: "/http:\\/\\/(?:0\\.0\\.0\\.0|127\\.0\\.0\\.1|localhost):(\\d+)/",
          done: true
        }]
      }
    },
    {
      method: "local.set",
      params: {
        url: "http://127.0.0.1:{{input.event[1]}}"
      }
    }
  ]
}
