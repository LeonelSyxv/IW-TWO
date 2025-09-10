const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");
const { PythonShell } = require("python-shell");
const path = require("path");
const fs = require("fs");

const CHAT_IDS = [
  // "120363421743509900@g.us" // Test
  "120363337403652171@g.us", // Monitoreo StarTV Stream
  // "5214921897369-1449534856@g.us", // Monitoreo
];

const PY_ROOT = path.resolve(__dirname, "../Python");

function startWatcher(client, scriptRel, label) {
  const scriptAbs = path.join(PY_ROOT, scriptRel);
  if (!fs.existsSync(scriptAbs)) {
    console.error(`[${label}] Script not found: ${scriptAbs}`);
    return;
  }

  console.log(`[${label}] Starting watcher: ${scriptAbs}`);
  const pyshell = new PythonShell(scriptRel, {
    mode: "text",
    pythonPath: "/home/scott/Projects/IW-TWO/Python/venv/bin/python",
    pythonOptions: ["-u", "-X", "utf8"],
    scriptPath: PY_ROOT,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: "1",
      PYTHONIOENCODING: "utf-8",
      PYTHONPATH: PY_ROOT,
    },
  });

  pyshell.on("message", (line) => {
    const looksJson = line && /^\s*[\[\{"]/.test(line.trim());
    if (!looksJson) return;

    try {
      const payload = JSON.parse(line);
      const list = Array.isArray(payload) ? payload : [payload];
      if (!list.length) return;

      const text = list.join("\n\n");
      CHAT_IDS.forEach((id) => {
        client
          .sendMessage(id, text)
          .then(() => console.log(`[${label}] Sent to ${id}:\n${text}`))
          .catch((err) =>
            console.error(`[${label}] Error sending to ${id}:`, err)
          );
      });
    } catch (e) {
      console.error(`[${label}] Invalid JSON:`, e, "\nLine:", line);
    }
  });

  pyshell.on("pythonError", (err) =>
    console.error(`[${label}] Python error:`, err)
  );
  pyshell.on("stderr", (stderr) =>
    console.error(`[${label}][stderr]:`, String(stderr))
  );
  pyshell.on("error", (err) => console.error(`[${label}] Process error:`, err));

  pyshell.on("close", (exitCode, signal) => {
    console.log(
      `[${label}] Closed (code=${exitCode}, signal=${signal}). Restarting in 5s...`
    );
    setTimeout(() => startWatcher(client, scriptRel, label), 5000);
  });
}

async function runPythonScript(client, scriptRel, label, targetChat) {
  const scriptAbs = path.join(PY_ROOT, scriptRel);
  if (!fs.existsSync(scriptAbs)) {
    for (const id of Array.isArray(targetChat) ? targetChat : [targetChat]) {
      await client.sendMessage(id, `[${label}] Script not found: ${scriptAbs}`);
    }
    return;
  }

  let output = "";
  const pyshell = new PythonShell(scriptRel, {
    mode: "text",
    pythonPath: "/home/scott/Projects/IW-TWO/Python/venv/bin/python",
    pythonOptions: ["-u", "-X", "utf8"],
    scriptPath: PY_ROOT,
    env: {
      ...process.env,
      PYTHONUNBUFFERED: "1",
      PYTHONIOENCODING: "utf-8",
      PYTHONPATH: PY_ROOT,
    },
  });

  pyshell.on("message", (line) => {
    output += line + "\n";
  });

  pyshell.on("close", async () => {
    let text = output.trim();
    try {
      const parsed = JSON.parse(text);
      if (Array.isArray(parsed)) {
        text = parsed.join("\n\n");
      } else if (typeof parsed === "string") {
        text = parsed;
      }
    } catch (e) { }

    const ids = Array.isArray(targetChat) ? targetChat : [targetChat];
    if (text) {
      for (const id of ids) {
        await client.sendMessage(id, text);
      }
    } else {
      for (const id of ids) {
        await client.sendMessage(id, `[${label}] No output from script.`);
      }
    }
  });

  pyshell.on("error", async (err) => {
    const ids = Array.isArray(targetChat) ? targetChat : [targetChat];
    for (const id of ids) {
      await client.sendMessage(id, `[${label}] Error executing script.`);
    }
    console.error(`[${label}] Error:`, err);
  });
}

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: path.resolve(__dirname, "./session") }),
});

client.on("qr", (qr) => {
  console.log("Scan the QR code to log in (first-time only).");
  qrcode.generate(qr, { small: true });
});

client.on("ready", () => {
  console.log("[✅] WhatsApp client ready.");

  // startWatcher(client, "Functions/getLatestReport.py", "getLatestReport");
  // startWatcher(client, "Functions/getResolvedReport.py", "getResolvedReport");
});

client.on("message", async (msg) => {
  if (CHAT_IDS.includes(msg.from)) {
    const body = msg.body.trim().toLowerCase();

    if (body === "!report") {
      console.log("Detected !report command. Running getReport.py...");
      await runPythonScript(
        client,
        "Functions/getReport.py",
        "getReport",
        msg.from
      );
      return;
    }

    if (body === "!grafana") {
      console.log("Detected !grafana command. Running getGrafanaReport.py...");

      const scriptRel = "Functions/getGrafanaReport.py";
      const scriptAbs = path.join(PY_ROOT, scriptRel);
      if (!fs.existsSync(scriptAbs)) {
        await client.sendMessage(
          msg.from,
          `[getGrafana] Script not found: ${scriptAbs}`
        );
        return;
      }

      const pyshell = new PythonShell(scriptRel, {
        mode: "text",
        pythonPath: "/home/scott/Projects/IW-TWO/Python/venv/bin/python",
        pythonOptions: ["-u", "-X", "utf8"],
        scriptPath: PY_ROOT,
      });

      let sent = false;

      pyshell.on("message", async (line) => {
        if (sent) return;

        try {
          const data = JSON.parse(line);

          if (data.image && fs.existsSync(data.image)) {
            const media = MessageMedia.fromFilePath(data.image);
            await client.sendMessage(msg.from, media);
          }

          if (data.message) {
            await client.sendMessage(msg.from, data.message);
          }

          sent = true;
        } catch (err) {
          console.error("[getGrafana] Error parsing output:", err, line);
          await client.sendMessage(
            msg.from,
            "Error processing Grafana report."
          );
        }
      });

      pyshell.on("stderr", (stderr) =>
        console.error("[getGrafana][stderr]:", String(stderr))
      );

      pyshell.on("error", (err) => {
        console.error("[getGrafana] Python error:", err);
        client.sendMessage(msg.from, "Error executing getGrafanaReport.py");
      });
    }
  }
});

client.initialize();
