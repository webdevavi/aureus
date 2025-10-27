require("dotenv").config();

const path = require("path");
const ROOT = __dirname;
const LOGS = path.join(ROOT, "logs");

module.exports = {
  apps: [
    {
      name: "api",
      script: "uvicorn",
      args: "backend.api.main:app --host 0.0.0.0 --port 8000",
      interpreter: "python3",
      cwd: ROOT,
      env: process.env,
      autorestart: true,
      max_restarts: 5,
      restart_delay: 5000,
      watch: false,
      max_memory_restart: "1G",
      out_file: path.join(LOGS, "api.out.log"),
      error_file: path.join(LOGS, "api.err.log"),
      merge_logs: true,
    },
    {
      name: "extractor",
      script: "python3",
      args: "-m backend.workers.extractor.main",
      cwd: ROOT,
      env: process.env,
      autorestart: true,
      watch: false,
      max_memory_restart: "3G",
      out_file: path.join(LOGS, "extractor.out.log"),
      error_file: path.join(LOGS, "extractor.err.log"),
      merge_logs: true,
    },
    {
      name: "renderer",
      script: "python3",
      args: "-m backend.workers.renderer.main",
      cwd: ROOT,
      env: process.env,
      autorestart: true,
      watch: false,
      max_memory_restart: "3G",
      out_file: path.join(LOGS, "renderer.out.log"),
      error_file: path.join(LOGS, "renderer.err.log"),
      merge_logs: true,
    },
    {
      name: "frontend",
      script: "bash",
      args: "-c 'npm run build && npx serve -s dist -l 5173'",
      cwd: path.join(ROOT, "frontend"),
      env: {
        ...process.env,
        NODE_ENV: "production",
        PORT: 5173,
      },
      autorestart: true,
      watch: false,
      max_memory_restart: "512M",
      out_file: path.join(LOGS, "frontend.out.log"),
      error_file: path.join(LOGS, "frontend.err.log"),
      merge_logs: true,
    },
  ],
};
