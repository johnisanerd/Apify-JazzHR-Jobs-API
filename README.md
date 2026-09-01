# 💼 JazzHR Jobs API: search every company hiring on JazzHR

A Python and MCP quick-start for the **JazzHR API** on Apify. One search covers every employer on the platform, so you never have to hunt down a company career URL first.

- Actor: [JazzHR Jobs API on Apify](https://apify.com/johnvc/jazzhr-jobs-api?fpr=9n7kx3)
- Input schema: [input parameters](https://apify.com/johnvc/jazzhr-jobs-api/input-schema?fpr=9n7kx3)
- Get a free API token: [apify.com](https://apify.com?fpr=9n7kx3)

Most JazzHR tools want a company board URL before they will do anything. This one already knows all of them. Point it at the whole platform and it returns structured job posting data: title, employer, location, employment type, real posting date, apply link, and the full description as markdown, HTML, or plain text. It can also hand back a directory of every business hiring on JazzHR, which is a useful thing to have before you decide whose board is worth reading in full.

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

### Text walkthrough

The **JazzHR API** reads the public career boards that JazzHR hosts on applytojob.com. Every input is optional: run it with nothing set and you get a sample from across the platform, or narrow it with `keywords`, `location`, `employmentType`, `remoteOnly`, and `postedAfter`. Keywords are matched against the job URL before a posting is opened, so filtering makes the run cheaper as well as tighter. Each row comes back with `title`, `companyName`, `locationText`, `employmentType`, `datePosted`, `validThrough`, `applyUrl`, and `descriptionMarkdown`. Switch `outputMode` to `companiesOnly` and you get one row per employer with a live count of open roles, which is how you build a list of companies that use JazzHR. Switch it to `urlsOnly` and you get the entire job index for a handful of upstream requests, the cheapest way to survey what is out there. Turn on `newJobsOnly` and each scheduled run returns only postings it has not seen before.

## Quick Start

Prerequisites: Python 3.11 or newer, [uv](https://docs.astral.sh/uv/), and a free Apify API token from [apify.com](https://apify.com?fpr=9n7kx3).

```bash
git clone https://github.com/johnisanerd/Apify-JazzHR-Jobs-API.git
cd Apify-JazzHR-Jobs-API
uv sync
cp .env.example .env          # paste your token into .env
uv run python jazzhr-jobs-api-example.py
```

Each example is a separate flag:

```bash
uv run python jazzhr-jobs-api-example.py --example jobs        # full job records
uv run python jazzhr-jobs-api-example.py --example companies   # employer directory
uv run python jazzhr-jobs-api-example.py --example urls        # job index, no descriptions
uv run python jazzhr-jobs-api-example.py --example new-jobs    # delta mode
uv run python jazzhr-jobs-api-example.py --example all
```

Every example asks for a small number of rows on purpose. You pay per row returned, so confirm the shape of the data first, then raise `maxItems`.

## Why use this API

**No company URL required.** Other tools make you supply a board before they can do anything. Leave the input empty here and the search covers every employer on the platform.

**A directory nobody else sells.** The `companiesOnly` mode returns every business hiring on JazzHR with a live count of their open roles. That is the list you want if you are prospecting companies that use JazzHR.

**Descriptions ready for an LLM.** Ask for markdown and hand the result straight to a model without stripping HTML first.

**Two sources per posting.** Around half of live postings publish no structured job data at all. Those are read from the page markup instead, so they arrive with a title, company, location and description rather than coming back half empty. The `parseStatus` field tells you which kind of row you have.

**Expired postings are skipped and never billed.** Roughly a fifth of the platform index points at roles that have already closed. You are charged for jobs you actually receive, not for dead links.

**A feed, not just a snapshot.** Delta mode remembers what it has already returned, so a scheduled run gives you only new postings.

## Recipes

No Store example pages are published for this Actor yet. The four scripted examples above cover the same ground: a filtered job search, the employer directory, the cheap job index, and the delta feed.

**Schedule tip.** Save your input as a Task in the [Apify Console](https://console.apify.com), turn on `newJobsOnly`, and schedule it daily or weekly. From then on the dataset only ever contains postings that appeared since the last run, so the pipeline stays current without anyone touching it.

## Usage Examples

Basic, matching the default run:

```json
{
  "keywords": ["nurse", "registered nurse"],
  "location": "TX",
  "employmentType": "FULL_TIME",
  "postedAfter": "2026-01-01",
  "descriptionFormat": "markdown",
  "maxItems": 10
}
```

Advanced, a remote-only search that skips staffing agencies and returns every description format:

```json
{
  "keywords": ["software engineer"],
  "remoteOnly": true,
  "excludeCompanies": ["someagency"],
  "descriptionFormat": "all",
  "maxConcurrency": 25,
  "maxItems": 100
}
```

## Input Parameters

Every parameter is optional.

| Parameter | Type | Default | Description |
|---|---|---|---|
| `startUrls` | array | empty | Company boards such as `https://company.applytojob.com`, or individual job URLs. Empty searches every employer. |
| `keywords` | array | empty | Job title words to keep. Applied before a posting is opened, so it also lowers the cost of the run. |
| `outputMode` | string | `jobs` | `jobs` for full records, `urlsOnly` for the job index, `companiesOnly` for the employer directory. |
| `descriptionFormat` | string | `markdown` | `markdown`, `html`, `text`, or `all`. |
| `companies` | array | empty | Only include these company slugs. For `acme.applytojob.com` the slug is `acme`. |
| `excludeCompanies` | array | empty | Skip these company slugs. |
| `location` | string | empty | Text match on city, state, postal code, or country. |
| `employmentType` | string | `ANY` | `FULL_TIME`, `PART_TIME`, `CONTRACTOR`, `TEMPORARY`, `INTERN`, `OTHER`. |
| `remoteOnly` | boolean | `false` | Keep only remote roles. |
| `postedAfter` | string | empty | `YYYY-MM-DD`. Uses the employer's real posting date. |
| `maxItems` | integer | `100` | Row cap. The platform holds over 100,000 live jobs, so this keeps a first run small. |
| `newJobsOnly` | boolean | `false` | Return only postings not seen in an earlier run. |
| `firstRunBehavior` | string | `emitAll` | On the first delta run, return everything or just record what exists today. |
| `deltaStoreName` | string | `jazzhr-seen-jobs` | Named store holding the remembered job IDs. |
| `maxConcurrency` | integer | `10` | Parallel page reads, up to 25. |
| `proxyConfiguration` | object | direct | Optional Apify Proxy settings. |

## Output Format

A full job record:

```json
{
  "id": "job_20260617184930_ZL9U2ROWTQWMZDDD",
  "jobId": "vMHpWDZa3l",
  "title": "Account Executive",
  "companyName": "Ease Inc",
  "companySlug": "easeinc",
  "companyWebsite": "http://www.ease.io",
  "boardUrl": "https://easeinc.applytojob.com",
  "applyUrl": "https://easeinc.applytojob.com/apply/vMHpWDZa3l/Account-Executive",
  "canonicalUrl": "https://careers.easeinc.com/apply/vMHpWDZa3l/Account-Executive",
  "city": "Irvine",
  "region": "CA",
  "postalCode": "92618",
  "country": "US",
  "locationText": "Irvine, CA, US",
  "isRemote": true,
  "employmentType": "FULL_TIME",
  "experienceLevel": "Mid Level",
  "datePosted": "2026-06-17",
  "validThrough": "2026-09-15",
  "descriptionMarkdown": "Ease is hiring an Account Executive...",
  "parseStatus": "full",
  "scrapedAt": "2026-08-24T18:22:04Z"
}
```

The employer directory returns a smaller row:

```json
{
  "companySlug": "10pearls",
  "boardUrl": "https://10pearls.applytojob.com",
  "jobCount": 21,
  "sampleJobTitles": ["AI Solutions Architect", "Associate Account Executive Intern"],
  "scrapedAt": "2026-08-24T18:22:04Z"
}
```

## People also search for

### Is this a JazzHR scraper?

It reads public pages the way a scraper does, and what you get back is an API: structured JSON, filters, stable field names, no HTML unless you ask for it. If you have been trying to scrape job postings yourself, this is the version where someone else maintains the parser.

### What is applytojob.com?

It is the domain where JazzHR hosts its customers' career pages. A company hiring through JazzHR gets a board at `company.applytojob.com`, and application email comes from that domain too, which is why so many people look it up after applying somewhere.

### How do I find companies that use JazzHR?

Set `outputMode` to `companiesOnly`. You get one row per employer with their board URL and a live count of open roles. The `--example companies` script does exactly this.

### How do I use the JazzHR API from Python?

Clone this repo, run `uv sync`, put your Apify token in `.env`, and run the example. The `rows()` helper shows the whole pattern: call the Actor, then iterate the dataset.

### Can I run it on a schedule or through MCP?

Both. Save the input as a Task in the Apify Console and schedule it, ideally with `newJobsOnly` on. For MCP, the install sections below add this Actor as a tool in Claude, Cursor, or ChatGPT.

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the JazzHR Jobs API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/jazzhr-jobs-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the JazzHR Jobs API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

---

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/jazzhr-jobs-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/jazzhr-jobs-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the JazzHR Jobs API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

---

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/jazzhr-jobs-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/jazzhr-jobs-api`, using OAuth when prompted.
5. Ask Claude to run the JazzHR Jobs API.

Open Claude on the web: https://claude.ai

---

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/jazzhr-jobs-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/jazzhr-jobs-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the JazzHR Jobs API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

---

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/jazzhr-jobs-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

---

Made with care by [johnvc on Apify](https://apify.com/johnvc?fpr=9n7kx3).

Last Updated: 2026.09.01
