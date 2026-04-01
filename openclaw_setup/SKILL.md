---
name: openclaw_setup
description: >
  Comprehensive OpenClaw manager. Use this skill to Install OpenClaw (with safety checks)
  AND Initialize/Configure it (models, agents). Trigger whenever the user mentions
  "openclaw", "install openclaw", "configure openclaw", "setup openclaw", or wants
  to run an AI coding assistant via OpenClaw.
---

# OpenClaw Manager

Complete guide for installing, configuring, and running OpenClaw. No Python required.

**IMPORTANT FOR THE MODEL**: Follow each part sequentially. Do NOT skip steps. At every step, verify success before proceeding. When a command fails, follow the stated fallback — do not improvise.

---

## Part 0: Detect Environment

Before anything else, determine the OS. This affects every subsequent command.

- **macOS**: shell = `bash/zsh`, paths use `/`
- **Windows**: shell = `PowerShell`, paths use `\`

Ask the user: *"Are you on macOS or Windows?"* if not already clear from context.

---

## Part 1: Safety Notice

Inform the user of the following risks before proceeding, then ask if they want to continue:

- OpenClaw installation will modify the system's Node.js environment and global npm packages
- It is recommended to use a spare computer or a separate user account to avoid affecting the main environment

Use `ask_followup_question` to ask the user whether to proceed. If they confirm, continue to Part 2. If they decline, stop.

---

## Part 2: Install Node.js 22

### Pre-check

```bash
node -v
```

- Output is `v22.x.x` → **skip to Part 3**
- Otherwise → proceed below

### macOS

```bash
touch ~/.zshrc && curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash && source ~/.zshrc
nvm --version          # If this fails: close/reopen terminal, then source ~/.zshrc
nvm install 22 && nvm use 22
node -v                # Must show v22.x.x before continuing
```

### Windows (PowerShell as Administrator)

```powershell
winget install --id OpenJS.NodeJS.22 --silent --accept-package-agreements --accept-source-agreements"
```

> ⚠️ winget does NOT refresh the current session's PATH after install. Run the block below immediately — do NOT open a new terminal.

```powershell
# Refresh PATH in current session so npm is available immediately
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# Verify both are found
node -v   # Must show v22.x.x
npm -v    # Must return a version number before continuing
```
---

## Part 3: Install OpenClaw

Execute the following steps **in order**. Do NOT skip Step 2 (PATH setup) — it is mandatory on all platforms before running `openclaw`.

### Step 1 — Install

```bash
# Set registry
npm config set registry https://mirrors.huaweicloud.com/repository/npm/

# Install (takes several minutes — wait for completion)
npm install -g openclaw
```

**If install fails with both `npm error code 128` AND `git ls-remote` in the output:**
```bash
npm cache clean --force
npm install -g openclaw
```

---

### Step 2 — Add OpenClaw to PATH (MANDATORY — run this before Step 3)

> ⚠️ **Do NOT skip this step.** PATH must be configured before `openclaw` can be found as a command.

**macOS (nvm):**
```bash
# Confirm the binary exists
ls $(npm config get prefix)/bin/openclaw
# If found, nvm already manages PATH — no further action needed
# If NOT found, re-run Step 1
```
---

### Step 3 — Verify (only after Step 2 is complete)

Use absolute path for this session:
```powershell
$openclaw = "$((npm config get prefix))\openclaw.cmd"
& $openclaw --version
```
> 📝 If absolute path was needed, store `$openclaw` and use `& $openclaw` in place of `openclaw` for all subsequent commands.

---

## Part 4: Configure OpenClaw (Direct JSON Edit)

> **Why direct JSON?** `openclaw config set` commands frequently time out or fail due to quote-escaping issues on Windows. Editing the config file directly is faster and more reliable on all platforms.

### Step 1: Collect Provider Details

Ask the user which provider they want and collect the required fields:

| Provider | Required fields |
|---|---|
| **Huawei Cloud** | API Key, Model Name (e.g. `glm-5`) |
| **Doubao** | API Key, Endpoint ID (e.g. `ep-2024...`), Model Name |
| **Anthropic** | API Key, Model Name (e.g. `claude-3-5-sonnet-20240620`) |

Huawei API keys: https://developer.huaweicloud.com/space/developerspace/tokens.html

Use `ask_followup_question` to ask the user to input the API Key and Model Name. 


### Step 2: Open the Config File

Config file location:
- **macOS**: `~/.openclaw/openclaw.json`
- **Windows**: `C:\Users\<USERNAME>\.openclaw\openclaw.json`

If the file does not exist yet, create it (and the directory if needed):

```bash
# macOS
mkdir -p ~/.openclaw && touch ~/.openclaw/openclaw.json

# Windows (PowerShell)
New-Item -ItemType Directory -Force "$HOME\.openclaw"
New-Item -ItemType File -Force "$HOME\.openclaw\openclaw.json"
```

Open the file in any text editor (VS Code, Notepad, nano, etc.).

### Step 3: Write the Full Config JSON

The config has two parts: a **shared base** (identical for all providers) and a **provider block** (differs per provider). Assemble them together as the final file content.

---

#### Part A — Shared Base (always include this)

```json
{
  "gateway": { "mode": "local" },
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace",
      "compaction": { "mode": "safeguard" },
      "maxConcurrent": 4,
      "subagents": { "maxConcurrent": 8 }
    }
  },
  "messages": { "ackReactionScope": "group-mentions" },
  "commands": { "native": "auto", "nativeSkills": "auto", "restart": true, "ownerDisplay": "raw" },
  "session": { "dmScope": "per-channel-peer" }
}
```

---

#### Part B — Provider Block (pick one, fill in placeholders)

**Option 1 — Huawei Cloud** · Replace: `<API_KEY>`, `<MODEL_NAME>` (e.g. `glm-5`)

```json
{
  "auth": { "profiles": { "huawei:default": { "provider": "huawei", "mode": "api_key" } } },
  "models": {
    "providers": {
      "huawei": {
        "baseUrl": "https://api.modelarts-maas.com/openai/v1",
        "apiKey": "<API_KEY>",
        "api": "openai-completions",
        "models": [{ "id": "<MODEL_NAME>", "name": "<MODEL_NAME>" }]
      }
    }
  },
  "agents": { "defaults": { "model": { "primary": "huawei/<MODEL_NAME>" }, "models": { "huawei/<MODEL_NAME>": {} } } }
}
```

**Option 2 — Doubao** · Replace: `<API_KEY>`, `<ENDPOINT_ID>` (e.g. `ep-20240604052306-abcde`), `<MODEL_NAME>` (e.g. `Doubao-1.8`)

```json
{
  "auth": { "profiles": { "doubao:default": { "provider": "doubao", "mode": "api_key" } } },
  "models": {
    "providers": {
      "doubao": {
        "baseUrl": "https://ark.cn-beijing.volces.com/api/v3",
        "apiKey": "<API_KEY>",
        "api": "openai-completions",
        "models": [{ "id": "<ENDPOINT_ID>", "name": "<MODEL_NAME>" }]
      }
    }
  },
  "agents": { "defaults": { "model": { "primary": "doubao/<ENDPOINT_ID>" }, "models": { "doubao/<ENDPOINT_ID>": {} } } }
}
```

**Option 3 — Anthropic** · Replace: `<API_KEY>`, `<MODEL_NAME>` (e.g. `claude-3-5-sonnet-20240620`)

```json
{
  "auth": { "profiles": { "anthropic:default": { "provider": "anthropic", "mode": "api_key" } } },
  "models": {
    "providers": {
      "anthropic": {
        "baseUrl": "https://api.anthropic.com",
        "apiKey": "<API_KEY>",
        "api": "anthropic-chat",
        "models": [{ "id": "<MODEL_NAME>", "name": "<MODEL_NAME>" }]
      }
    }
  },
  "agents": { "defaults": { "model": { "primary": "anthropic/<MODEL_NAME>" }, "models": { "anthropic/<MODEL_NAME>": {} } } }
}
```

---

#### Part C — Merge and write the final file

Deep-merge Part A and Part B (provider block takes precedence for overlapping keys under `agents.defaults`), then write the result to `openclaw.json`. The model should do this merge and produce the final complete JSON to show the user — **do not ask the user to merge manually**.

---

## Part 5: Start OpenClaw Service

Execute the following steps **in order**. Do NOT run `openclaw dashboard` until Step 2 confirms the token exists.

### Step 1 — Start the gateway

**MacOS**
```bash
$openclaw = "$((npm config get prefix))\openclaw.cmd"; & $openclaw gateway
```

**Windows**
Use Powershell to run
```Powershell
$openclaw = "$((npm config get prefix))\openclaw.cmd"; & Start-Process -FilePath $openclaw -ArgumentList "gateway", "run" -WindowStyle Hidden
```


⏳ Wait **180 seconds** for full initialization.

---

### Step 2 — Verify status(MANDATORY before Step 3)

Check whether openclaw is running successful by
```powershell
$openclaw = "$((npm config get prefix))\openclaw.cmd"; & $openclaw gateway status
```

---

### Step 3 — Get the Web UI URL

```bash
openclaw dashboard
```

This outputs a URL like:
```
http://127.0.0.1:18789/#token=xxxxxxxx
```

**Show this URL to the user.**

If `openclaw dashboard` doesn't print the token, read it directly from the config file:

**macOS:**
```bash
grep -o '"token":"[^"]*"' ~/.openclaw/openclaw.json
```

**Windows (PowerShell):**
```powershell
(Get-Content "$HOME\.openclaw\openclaw.json" | ConvertFrom-Json).token
```

---

## Part 6: Summary

Provide the user a concise summary:

1. ✅ Node.js version installed and location
2. ✅ OpenClaw version and install path
3. ✅ Provider configured and model name
4. ✅ Web UI URL: `http://127.0.0.1:18789/#token=...`
5. ⚠️ **Windows only**: To use OpenClaw in any future terminal, permanently add npm prefix to `Path`:
   - 运行 `npm config get prefix` 获取实际路径（如 `C:\Users\you\npm-global`）
   - 将该路径加入系统 PATH：Start → "Environment Variables" → Edit `Path` → Add