# SRD UI Options Analysis

## Context

The SRD is a **pure Python** computation engine. Any UI needs to:
1. Collect inputs to build `Person`, `Dependent`, and `Hhold` objects (~40 attributes for Person alone)
2. Run `tax(year).compute(hhold)` and display results (`fed_return`, `prov_return`, `payroll`, `disp_inc`)
3. Load a CSV/database, map columns to `Person`/`Dependent`/`Hhold` attributes, run batch calculations, and export results

This Python dependency is the key architectural constraint.

---

## Option 1: VS Code Extension

**How it works**: A TypeScript extension with a WebView panel (embedded HTML/CSS/JS) that communicates with a Python subprocess running the SRD.

**Architecture**: `VS Code Extension (TypeScript) -> WebView (HTML/JS) -> Python child process -> SRD`

**Pros**:
- Integrated into the dev environment you already use
- Can access workspace files (CSVs) directly

**Cons**:
- **Two-language architecture**: The extension itself must be TypeScript; all UI logic is JS/HTML. Python runs as a subprocess with JSON message passing between the two runtimes.
- **Hard to implement**: WebView panels are sandboxed iframes with limited APIs. Building a complex form + data grid in a WebView is painful.
- **Requires VS Code**: Non-developers or collaborators can't use it without VS Code installed.
- **Distribution**: Needs to be packaged as a `.vsix`, and the user still needs a working Python environment with `srd` installed.
- **Not designed for this**: VS Code extensions are meant for editor features (linting, formatting, language support), not standalone data apps.

**Verdict**: Technically possible but high-effort, low-reward. Not recommended.

---

## Option 2: Electron App

**How it works**: A standalone desktop app using Chromium (for UI) and Node.js (for backend). The Node.js layer spawns a Python process to run the SRD.

**Architecture**: `Electron (React/Vue frontend) -> Node.js main process -> Python child process -> SRD`

**Pros**:
- Full desktop app with native feel (menus, file dialogs, etc.)
- Complete UI freedom (React/Vue/any web framework)
- Cross-platform (Windows, macOS, Linux)

**Cons**:
- **Three-layer architecture**: JavaScript frontend + Node.js backend + Python subprocess. Significant communication plumbing needed.
- **Large bundle**: Electron ships Chromium (~150-300 MB). Plus you need to bundle or require a Python runtime.
- **Heavy to implement**: You need React/Vue components for every form, a Node.js IPC layer, and a Python bridge. This is a substantial amount of JS/TS code.
- **Python distribution problem**: Either bundle Python with the app (complex) or require users to have Python + SRD installed.
- **Overkill**: This is the architecture of apps like Slack and VS Code. For a tax calculator with two screens, it's over-engineered.

**Verdict**: Possible but disproportionate effort for the use case, and requires significant JavaScript expertise.

---

## Option 3: Streamlit Web App (Chosen)

**How it works**: A 100% Python web framework that generates a browser-based UI. Runs locally as `streamlit run app.py` and opens in your browser.

**Architecture**: `Python (Streamlit) -> SRD (direct import)`

**Pros**:
- **100% Python** -- no JavaScript, no TypeScript, no HTML/CSS. Direct `import srd` with no subprocess or IPC.
- **Built for exactly this use case**: Forms, file uploads, data tables, column mapping -- all built-in widgets.
- **Fastest to implement**: A working prototype for both features can be built in a single Python file.
- **Easy to distribute**: `pip install streamlit` + run the script. Or deploy to Streamlit Community Cloud for free web access.
- **Rich data display**: Native support for DataFrames, charts, downloadable files.

**Cons**:
- Runs in a browser tab (not a "native" desktop window)
- The rerun execution model can feel different from traditional apps (the whole script reruns on each interaction)
- Less customization than a full React app for very complex UIs

**Verdict**: Best fit. Minimal complexity, fastest to build, pure Python.

---

## Option 4: Flask/FastAPI + Lightweight HTML Frontend

**How it works**: A Python web server with hand-crafted HTML pages using a CSS framework (Bootstrap) and minimal JavaScript.

**Architecture**: `Browser -> Flask/FastAPI (Python) -> SRD (direct import)`

**Pros**:
- Python backend with direct SRD import (no subprocess)
- Full control over the UI
- Lighter than Electron
- Can be deployed as a web app

**Cons**:
- Requires writing HTML templates, CSS, and some JavaScript (form handling, AJAX calls, file upload logic, data grid rendering)
- Significantly more code than Streamlit for the same result
- You'd need to build the column-mapping UI and data table from scratch in JS

**Verdict**: Viable middle ground if you need more UI control than Streamlit, but substantially more work.

---

## Summary Comparison

| Criteria                  | VS Code Ext. | Electron | Streamlit | Flask |
|--------------------------|:---:|:---:|:---:|:---:|
| 100% Python              | No  | No  | **Yes** | Mostly |
| Implementation effort    | High | High | **Low** | Medium |
| Direct SRD import        | No  | No  | **Yes** | **Yes** |
| Built-in forms/tables    | No  | No  | **Yes** | No |
| File upload + CSV        | Manual | Manual | **Built-in** | Manual |
| Desktop feel             | VS Code only | **Yes** | Browser tab | Browser tab |
| Distribution ease        | Low | Low | **High** | Medium |

---

## SRD API Surface for UI Integration

### Input Data Collection
- Create `Person` objects with income and deduction inputs (~40 attributes)
- Create `Dependent` objects for children (age, child_care, disabled, etc.)
- Create `Hhold` with province selection and optional second spouse

### Run Calculation
- Create `tax(year)` object with year and province
- Call `compute(hhold)` method
- Optional flags: `ifed`, `iprov`, `ipayroll`, `ioas`, `iass`

### Display Results
- `hhold.fam_disp_inc`: Family disposable income (main output)
- `person.fed_return`: Dict with federal tax details
- `person.prov_return`: Dict with provincial tax details
- `person.payroll`: Dict with payroll deductions (ei, cpp, qpip)
- `person.disp_inc`: Individual disposable income
- Benefits: `inc_oas`, `inc_gis`, `inc_sa`, `inc_ei`, etc.

### Key Person Attributes for Form
**Income sources**: `earn`, `rpp`, `cpp`, `self_earn`, `inc_rrsp`, `inc_rdsp`, `div_elig`, `div_other_can`, `inc_othtax`, `inc_othntax`, `cap_gains`
**Deductions**: `con_rrsp`, `con_rdsp`, `con_non_rrsp`, `union_dues`, `donation`, `gift`, `med_exp`
**Status**: `age`, `disabled`, `widow`, `student`, `essential_worker`, `prev_inc_work`
**Monthly**: `hours_month`, `inc_work_month` (lists of 12 values)

### Available Tax Years & Provinces
- **Years**: 2016-2023
- **Full models**: Quebec (qc), Ontario (on)
- **Barebones models**: ab, bc, mb, nb, nl, ns, pe, sk, nt, nu, yt
