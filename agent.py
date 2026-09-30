import json, re, shutil, subprocess, sys, pathlib
from google.genai import types

ROOT = pathlib.Path(__file__).parent
SITE, OUT = ROOT / "site", ROOT / "out"
ALLOWED = ("app/", "components/", "lib/")

ANALYZE_PROMPT = """You are a senior frontend engineer. Using the screenshots (desktop, mobile)
and the scraped data, return ONLY JSON describing the site:
{"colors": {"primary","secondary","background","text","accent"},
 "fonts": {"heading","body"}, "spacing_style": "...",
 "navigation": [{"label","href"}],
 "sections": [{"name","type","layout","content","images"}],
 "responsive_notes": "..."}
List sections top to bottom. Copy real text from the data. Data:\n"""

GENERATE_PROMPT = """Build this website as a Next.js 14+ App Router + TypeScript + Tailwind project.
Rules:
- Only write files under app/ and components/. Do not write config files.
- One reusable component per section (Navbar.tsx, Hero.tsx, Footer.tsx ...), imported in app/page.tsx.
- Use plain <img> tags with the original absolute image URLs (not next/image).
- Use Tailwind classes; put brand colors as CSS variables in app/globals.css.
- Fully responsive (mobile first). Match colors, fonts, spacing and text from the spec.
- Add "use client" only in components that use hooks.
- Output format, nothing else. For each file:
=== FILE: path/to/file.tsx ===
<code>
Spec:\n"""

FIX_PROMPT = """The TypeScript check failed. Fix the errors. Return ONLY the files you changed,
in the same '=== FILE: path ===' format.\n\nERRORS:\n{log}\n\nCURRENT FILES:\n{files}"""

MODIFY_PROMPT = """Modify this Next.js project according to the instruction.
Return ONLY new or changed files in '=== FILE: path ===' format. To delete a file write
'=== DELETE: path ===' on its own line. Keep the code clean and reusable.

INSTRUCTION: {instruction}

CURRENT FILES:\n{files}"""

# ---------- helpers ----------
import time
from google.genai import errors
from config import client, MODEL, FALLBACK_MODELS

def ask(parts, json_mode=False):
    cfg = types.GenerateContentConfig(response_mime_type="application/json") if json_mode else None
    
    # Force-remove "gemini-2.0-flash" if it dynamically leaks from cache, env, or configuration
    raw_models = [MODEL] + FALLBACK_MODELS
    models_to_try = [m for m in raw_models if "gemini-2.0-flash" not in m]
    
    # Absolute safety fallback line if configuration list resolves empty
    if not models_to_try:
        models_to_try = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
        
    max_retries = 3
    
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                # Attempt to complete generation request
                response = client.models.generate_content(
                    model=model_name, 
                    contents=parts, 
                    config=cfg
                )
                return response.text
                
            except errors.APIError as e:
                error_str = str(e).lower()
                error_code = getattr(e, "code", None)
                
                # CATCH 1: Intercept 404 (Retired Models). Immediately break inner attempt loop to pick a fresh endpoint
                if error_code == 404 or "404" in error_str or "not_found" in error_str:
                    print(f" Endpoint {model_name} unavailable (404). Transitioning to next model choice...")
                    break 
                
                # CATCH 2: Handle service rate limits or overloads (429, 503) with progressive timeouts
                elif error_code in [429, 503] or "429" in error_str or "503" in error_str:
                    if attempt < max_retries - 1:
                        sleep_time = 2 ** (attempt + 1)
                        print(f" Server busy ({model_name}). Retrying in {sleep_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(sleep_time)
                        continue
                    else:
                        print(f" {model_name} overloaded after {max_retries} attempts. Falling back to alternative layers...")
                        break
                
                # CATCH 3: Surface real syntax or credential issues immediately
                else:
                    raise e
                    
    raise Exception("All configured Gemini endpoints are currently failing or unreachable. Please verify network status.")

def parse_files(text):
    files = {}
    for path, code in re.findall(r"=== FILE: (.+?) ===\n(.*?)(?=\n=== (?:FILE|DELETE): |\Z)", text, re.S):
        code = re.sub(r"^```\w*\n|\n```\s*$", "", code.strip())   # strip markdown fences
        files[path.strip()] = code
    deletes = re.findall(r"=== DELETE: (.+?) ===", text)
    return files, deletes

def safe(path):
    return path.startswith(ALLOWED) and ".." not in path

def apply(files, deletes=()):
    for path, code in files.items():
        if safe(path):
            p = SITE / path
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(code, encoding="utf-8")
    for path in deletes:
        if safe(path):
            (SITE / path).unlink(missing_ok=True)

def read_project():
    out = {}
    for d in ("app", "components"):
        for p in (SITE / d).rglob("*"):
            if p.is_file() and p.suffix in (".tsx", ".ts", ".css"):
                out[p.relative_to(SITE).as_posix()] = p.read_text(encoding="utf-8")
    return out

def files_as_text(files):
    return "\n".join(f"=== FILE: {k} ===\n{v}" for k, v in files.items())

def reset_site():
    if not SITE.exists():
        shutil.copytree(ROOT / "template", SITE)
    else:
        for d in ("app", "components"):
            shutil.rmtree(SITE / d, ignore_errors=True)
        shutil.copytree(ROOT / "template" / "app", SITE / "app")


# ---------- pipeline stages ----------
def analyze(url):
    subprocess.run([sys.executable, str(ROOT / "scraper.py"), url], check=True)
    data = (OUT / "data.json").read_text(encoding="utf-8")[:30000]
    parts = [types.Part.from_bytes(data=(OUT / "desktop.jpg").read_bytes(), mime_type="image/jpeg"),
             types.Part.from_bytes(data=(OUT / "mobile.jpg").read_bytes(), mime_type="image/jpeg"),
             ANALYZE_PROMPT + data]
    spec = json.loads(ask(parts, json_mode=True))
    (OUT / "spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return spec

def validate():
    r = subprocess.run("npx tsc --noEmit", cwd=SITE, shell=True, capture_output=True, text=True, timeout=180)
    return r.returncode == 0, (r.stdout + r.stderr)[-4000:]

def validate_and_fix(retries=3, log=print):
    for attempt in range(retries + 1):
        ok, err = validate()
        if ok:
            log("Validation passed"); return True
        if attempt == retries:
            break
        log(f"Build errors, auto-fixing (attempt {attempt + 1}/{retries})...")
        text = ask(FIX_PROMPT.format(log=err, files=files_as_text(read_project())))
        files, deletes = parse_files(text)
        apply(files, deletes)
    log("Could not fix all errors"); return False

def generate(spec, log=print):
    reset_site()
    files, _ = parse_files(ask(GENERATE_PROMPT + json.dumps(spec)))
    apply(files)
    return validate_and_fix(log=log)

def modify(instruction, log=print):
    text = ask(MODIFY_PROMPT.format(instruction=instruction, files=files_as_text(read_project())))
    files, deletes = parse_files(text)
    apply(files, deletes)
    return validate_and_fix(log=log)

def start_preview():
    return subprocess.Popen("npm run dev -- -p 3001", cwd=SITE, shell=True)
