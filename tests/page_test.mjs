// The browser page (dm/page.html), driven in Edge with a stand-in for Anthropic's API: key, new game, turns, the
// sheet, retries and failures, saves kept across a reload, import, export, delete. Run from the repo root:
//     npm install --no-save puppeteer-core@25.11.0
//     py -3.12 -m dm.site --build
//     node tests/page_test.mjs build/site <a converted save to import, e.g. saves/x.json>
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import puppeteer from "puppeteer-core";

const SITE = process.argv[2], SAVE = process.argv[3];
const EDGE = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
const fails = [];
const check = (ok, what) => { console.log((ok ? "ok   " : "FAIL ") + what); if (!ok) fails.push(what); };

// ---- the stand-in API: scripted replies first, else a roll then a closing line ----
const requests = [], script = [];
let n = 0;
const msg = (content, stop) => ({id: "msg_" + ++n, type: "message", role: "assistant", model: "m", content,
                                 stop_reason: stop, stop_sequence: null, usage: {input_tokens: 1, output_tokens: 1}});
const api = http.createServer((req, res) => {
  const cors = {"access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "POST"};
  if (req.method === "OPTIONS") { res.writeHead(204, cors); return res.end(); }
  let body = "";
  req.on("data", c => body += c);
  req.on("end", () => {
    const r = JSON.parse(body);
    requests.push({headers: req.headers, body: r});
    let status = 200, out;
    if (script.length) [status, out] = script.shift();
    else {
      const last = r.messages[r.messages.length - 1];
      const answered = last.content.some(b => b.type === "tool_result");
      out = answered ? msg([{type: "text", text: "The goblin falls. What does Brakka do?"}], "end_turn")
        : msg([{type: "thinking", thinking: "", signature: "sig"}, {type: "text", text: "Roll to hit."},
               {type: "tool_use", id: "tu_" + n, name: "roll", input: {dice: "1d20+5", reason: "Brakka's attack vs the goblin"}}], "tool_use");
    }
    res.writeHead(status, {...cors, "content-type": "application/json"});
    res.end(JSON.stringify(out));
  });
}).listen(8799, "127.0.0.1");

// ---- the site, as dm.site serves it ----
const site = http.createServer((req, res) => {
  const p = path.join(SITE, decodeURIComponent(req.url.split("?")[0]).replace(/^\/$/, "/index.html"));
  if (!fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, {"content-type": p.endsWith(".html") ? "text/html; charset=utf-8" : "application/zip"});
  res.end(fs.readFileSync(p));
}).listen(8798, "127.0.0.1");

const browser = await puppeteer.launch({executablePath: EDGE, headless: true, args: ["--no-first-run"]});
const page = await browser.newPage();
await page.setViewport({width: 400, height: 800});
const errors = [];
page.on("pageerror", e => errors.push(String(e)));
page.on("dialog", d => d.accept());
const visible = sel => page.$eval(sel, e => !e.hidden && !e.closest("[hidden]")).catch(() => false);
const outText = () => page.$eval("#out", e => e.innerText);
const idle = () => page.waitForFunction(() => !busy, {timeout: 60000});
const opened = () => page.waitForFunction(() => running && !busy && text.length, {timeout: 60000});
const ready = async () => {
  await page.waitForFunction(() => py && document.getElementById("loading").hidden, {timeout: 60000});
  await page.evaluate(() => py.runPython("import dm.browser as b; b.API = 'http://127.0.0.1:8799/v1/messages'"));
};

const t0 = Date.now();
await page.goto("http://127.0.0.1:8798/");
await ready();
console.log(`loaded in ${Date.now() - t0} ms`);
check(await visible("#keyBox") && !(await visible("#keyHave")), "no key yet: the key box shows");

// a new game without a key is stopped
await page.evaluate(() => go({character: "fighter"}));
check(!(await page.evaluate(() => running)), "no key: a game doesn't start");

await page.type("#key", "sk-ant-test-123");
await page.click("#keyForm button");
check(!(await visible("#keyBox")) && await visible("#keyHave"), "key saved: the box is replaced by 'saved'");
check(await page.evaluate(() => localStorage.getItem("anthropic-key")) === "sk-ant-test-123", "key kept in localStorage");

// a new game: the opening turn
await page.click("#start .grid button");  // Fighter
await opened();
let t = await outText();
check(t.includes("Roll to hit.") && t.includes("The goblin falls."), "the DM's opening text shows");
check(await page.$$eval(".card .die", d => d.length) >= 1, "the roll is drawn as dice");
check(await page.$eval("#name", e => e.textContent) === "Brakka Ironvein", "the header names the character");
const first = requests[0];
check(first.headers["x-api-key"] === "sk-ant-test-123", "the key goes to the API");
check(first.headers["anthropic-dangerous-direct-browser-access"] === "true", "the browser-access header is sent");
check(first.body.cache_control?.ttl === "1h" && first.body.thinking?.type === "adaptive", "caching and thinking are on");
check(first.body.tools.some(x => x.name === "lookup"), "the tools are sent");
check(requests[1].body.messages.at(-1).content[0].type === "tool_result", "the tool's result goes back");

// the save is in the browser's database
await page.waitForFunction(async () => (await saves("readonly", s => s.getAll())).length === 1);
const stored = await page.evaluate(async () => (await saves("readonly", s => s.getAll()))[0]);
check(stored.name === "Brakka Ironvein" && JSON.parse(stored.data).messages.length === 4, "the save (with the conversation) is stored");

// a player's line
await page.type("#line", "I swing my axe");
await page.click("#form button");
await idle();
t = await outText();
check(t.includes("I swing my axe"), "the player's line shows");
check(requests.at(-2).body.messages.at(-1).content[0].text.includes("[The player]\nI swing my axe"), "the line reaches the DM");

// the sheet panel
await page.click("#sheetBtn");
check(await visible("#panel") && (await page.$eval("#panelBody", e => e.innerText)).includes("Brakka Ironvein"), "the sheet opens in the panel");
await page.keyboard.press("Escape");
check(!(await visible("#panel")), "Esc closes the sheet");

// overload: retried, then it works
script.push([529, {type: "error", error: {type: "overloaded_error", message: "Overloaded"}}]);
await page.type("#line", "again");
await page.click("#form button");
await idle();
t = await outText();
check(!t.includes("The DM call failed") && t.split("The goblin falls.").length >= 4, "an overloaded API is retried");

// a bad key: the failure shows, and the next line carries on
script.push([401, {type: "error", error: {type: "authentication_error", message: "invalid x-api-key"}}]);
await page.type("#line", "one");
await page.click("#form button");
await idle();
t = await outText();
check(t.includes("The DM call failed: 401: invalid x-api-key"), "a failed call shows why");
const before = requests.length;
await page.type("#line", "two");
await page.click("#form button");
await idle();
const sent = requests[before].body.messages.at(-1);
check(sent.role === "user" && sent.content.filter(b => b.type === "text").length === 2, "the next line joins the unanswered one");

// save and quit, then the start screen lists it
await page.click("#top button:last-child");
await idle();
check(await visible("#start") && (await page.$eval("#saves", e => e.innerText)).includes("Brakka Ironvein"), "quit: back to the start, the save listed");

// reload: the key and the save are still there; continue it
await page.reload();
await ready();
check(await visible("#keyHave") && (await page.$$(".saveRow")).length === 1, "after a reload: key and save still there");
await page.click(".saveRow .save");
await opened();
t = await outText();
check(t.includes("I swing my axe") && t.includes("The goblin falls."), "continuing shows the game so far");
const n0 = requests.length;
await page.type("#line", "onward");
await page.click("#form button");
await idle();
check(requests[n0].body.messages.length > 8, "the DM has its whole conversation after a reload");
await page.click("#top button:last-child");
await idle();

// import a converted save (Brakka's real game), then continue it
const input = await page.$("#importFile");
await input.uploadFile(SAVE);
await page.waitForFunction(() => document.querySelectorAll(".saveRow").length === 2);
await page.click(".saveRow .save");  // the newest: the import
await opened();
t = await outText();
check(t.length > 20000 && (await page.$eval("#name", e => e.textContent)).length > 0, `the imported game shows (${t.length} characters)`);
await page.click("#sheetBtn");
check((await page.$$("#panelBody .card.sheet")).length >= 2, "its sheet panel has the PC and companions");
await page.keyboard.press("Escape");
const n1 = requests.length;
await page.type("#line", "I look around");
await page.click("#form button");
await idle();
check(requests[n1].body.messages.length > 1000, `the imported conversation goes to the DM (${requests[n1].body.messages.length} messages)`);
await page.click("#top button:last-child");
await idle();

// export: the file is the save
const exported = await page.evaluate(async () => {
  let got = null;
  const orig = URL.createObjectURL;
  URL.createObjectURL = b => { got = b; return orig(b); };
  const id = document.querySelector(".saveRow .save").dataset.id;
  await exportSave(id);
  URL.createObjectURL = orig;
  return JSON.parse(await got.text()).sheet.name;
});
check(exported.length > 0, "export gives the save as a file");

// delete (the confirm is accepted)
await page.click(".saveRow button[aria-label=Delete]");
await page.waitForFunction(() => document.querySelectorAll(".saveRow").length === 1);
check(true, "delete removes a save");

// forget the key
await page.click("#keyHave a");
check(await visible("#keyBox") && !(await page.evaluate(() => localStorage.getItem("anthropic-key"))), "forget removes the key");

check(!errors.length, "no page errors" + (errors.length ? ": " + errors.join(" | ") : ""));
await browser.close(); api.close(); site.close();
console.log(fails.length ? `${fails.length} FAILED` : "all passed");
process.exit(fails.length ? 1 : 0);
