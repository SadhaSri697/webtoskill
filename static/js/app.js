/**
 * WebToSkill Studio - Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initBackendStatus();
    initCompiler();
    initExplorer();
    initValidator();
    initSimulator();
});

// Toast Notification
function showToast(message, duration = 3000) {
    const toast = document.getElementById("toast");
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove("hidden");
    setTimeout(() => {
        toast.classList.add("hidden");
    }, duration);
}

// Tab Switching
function initTabs() {
    const tabBtns = document.querySelectorAll(".nav-tab");
    const tabPanes = document.querySelectorAll(".tab-pane");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const tabId = btn.getAttribute("data-tab");
            
            tabBtns.forEach(b => {
                b.classList.remove("active");
                b.setAttribute("aria-selected", "false");
            });
            tabPanes.forEach(p => p.classList.remove("active"));

            btn.classList.add("active");
            btn.setAttribute("aria-selected", "true");

            const targetPane = document.getElementById(`tab-${tabId}`);
            if (targetPane) {
                targetPane.classList.add("active");
            }
        });
    });
}

// Backend Health Check
async function initBackendStatus() {
    const statusLabel = document.getElementById("backend-status-text");
    try {
        const res = await fetch("/api/status");
        if (res.ok) {
            const data = await res.json();
            if (statusLabel) {
                statusLabel.textContent = `Backend: Online (${data.sample_skills_count + data.compiled_skills_count} skills)`;
            }
        } else {
            if (statusLabel) statusLabel.textContent = "Backend: Error";
        }
    } catch (e) {
        if (statusLabel) statusLabel.textContent = "Backend: Offline";
    }
}

// -------------------------------------------------------------
// 1. Live Website Compiler
// -------------------------------------------------------------
function initCompiler() {
    const urlInput = document.getElementById("target-url-input");
    const compileBtn = document.getElementById("compile-submit-btn");
    const progressBox = document.getElementById("compiler-progress");
    const resultsBox = document.getElementById("compiler-results");

    const stepFetch = document.getElementById("step-fetch");
    const stepExtract = document.getElementById("step-extract");
    const stepGenerate = document.getElementById("step-generate");
    const stepValidate = document.getElementById("step-validate");

    const statElements = document.getElementById("stat-elements-count");
    const statDomain = document.getElementById("stat-domain-name");
    const statBadge = document.getElementById("stat-validation-badge");

    const codeHome = document.getElementById("code-preview-home");
    const codeOverview = document.getElementById("code-preview-overview");
    const tableBody = document.getElementById("inventory-table-body");
    const copyBtn = document.getElementById("btn-copy-skill");

    // Presets
    document.querySelectorAll(".preset-chip[data-url]").forEach(chip => {
        chip.addEventListener("click", () => {
            urlInput.value = chip.getAttribute("data-url");
            urlInput.focus();
        });
    });

    // Subtab switching inside Results
    const subtabs = document.querySelectorAll(".sub-tab");
    const subpanes = document.querySelectorAll(".subtab-pane");

    subtabs.forEach(tab => {
        tab.addEventListener("click", () => {
            const id = tab.getAttribute("data-subtab");
            subtabs.forEach(t => t.classList.remove("active"));
            subpanes.forEach(p => p.classList.remove("active"));
            tab.classList.add("active");
            const target = document.getElementById(`subtab-pane-${id}`);
            if (target) target.classList.add("active");
        });
    });

    // Copy action
    if (copyBtn) {
        copyBtn.addEventListener("click", () => {
            const activePane = document.querySelector(".subtab-pane.active");
            if (activePane) {
                const text = activePane.innerText;
                navigator.clipboard.writeText(text).then(() => {
                    showToast("Copied to clipboard!");
                }).catch(() => {
                    showToast("Failed to copy text");
                });
            }
        });
    }

    // Submit Compiler
    compileBtn.addEventListener("click", async () => {
        const rawUrl = urlInput.value.trim();
        if (!rawUrl) {
            showToast("Please enter a valid website URL");
            return;
        }

        compileBtn.disabled = true;
        compileBtn.querySelector(".btn-text").textContent = "Compiling...";
        progressBox.classList.remove("hidden");
        resultsBox.classList.add("hidden");

        // Reset Pipeline
        const steps = [stepFetch, stepExtract, stepGenerate, stepValidate];
        steps.forEach(s => {
            s.classList.remove("active", "done");
        });

        // Step 1: Fetch
        stepFetch.classList.add("active");

        const advanceTimer1 = setTimeout(() => {
            stepFetch.classList.remove("active");
            stepFetch.classList.add("done");
            stepExtract.classList.add("active");
        }, 600);

        const advanceTimer2 = setTimeout(() => {
            stepExtract.classList.remove("active");
            stepExtract.classList.add("done");
            stepGenerate.classList.add("active");
        }, 1200);

        try {
            const resp = await fetch("/api/compile", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: rawUrl })
            });

            clearTimeout(advanceTimer1);
            clearTimeout(advanceTimer2);

            const result = await resp.json();

            // Finish pipeline steps
            steps.forEach(s => s.classList.add("done"));

            if (!resp.ok) {
                showToast(`Compile error: ${result.error || "Failed"}`);
                return;
            }

            // Populate Stats
            statElements.textContent = result.elements_count || 0;
            statDomain.textContent = result.domain || rawUrl;
            
            if (result.validation && result.validation.passed) {
                statBadge.className = "badge badge-success";
                statBadge.textContent = "VALID ✓";
            } else {
                statBadge.className = "badge badge-warning";
                statBadge.textContent = "WARNINGS ⚠";
            }

            // Populate Code Previews
            codeHome.textContent = result.home_preview || "";
            codeOverview.textContent = result.overview_preview || "";

            // Populate Elements Table
            tableBody.innerHTML = "";
            (result.elements || []).forEach(el => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><code>${el.ref}</code></td>
                    <td><code>${escapeHtml(el.selector)}</code></td>
                    <td><span class="badge badge-neutral">${escapeHtml(el.type)}</span></td>
                    <td>${escapeHtml(el.purpose)}</td>
                `;
                tableBody.appendChild(tr);
            });

            resultsBox.classList.remove("hidden");
            showToast(`Compiled ${result.domain} successfully!`);

            // Refresh Explorer and Validator choices
            loadSkillsList();
            refreshValidatorSelect();

        } catch (err) {
            showToast(`Request failed: ${err.message}`);
        } finally {
            compileBtn.disabled = false;
            compileBtn.querySelector(".btn-text").textContent = "Compile Website";
        }
    });
}

function escapeHtml(str) {
    if (!str) return "";
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// -------------------------------------------------------------
// 2. Skill Explorer & Reader
// -------------------------------------------------------------
let allSkills = [];

async function initExplorer() {
    const refreshBtn = document.getElementById("btn-refresh-skills");
    if (refreshBtn) {
        refreshBtn.addEventListener("click", loadSkillsList);
    }
    await loadSkillsList();
}

async function loadSkillsList() {
    const listContainer = document.getElementById("skills-list-container");
    if (!listContainer) return;

    listContainer.innerHTML = '<div class="loading-state">Loading skills...</div>';

    try {
        const resp = await fetch("/api/skills");
        const data = await resp.json();
        allSkills = data.skills || [];

        if (allSkills.length === 0) {
            listContainer.innerHTML = '<div class="empty-state">No skills found.</div>';
            return;
        }

        listContainer.innerHTML = "";
        allSkills.forEach((skill, idx) => {
            const item = document.createElement("div");
            item.className = `skill-item ${idx === 0 ? "active" : ""}`;
            item.setAttribute("data-id", skill.id);

            item.innerHTML = `
                <div class="skill-item-header">
                    <span class="skill-item-name">${skill.name}</span>
                    <span class="skill-item-tag">${skill.type} (${skill.file_count} files)</span>
                </div>
                <div class="skill-item-desc">${skill.description}</div>
            `;

            item.addEventListener("click", () => {
                document.querySelectorAll(".skill-item").forEach(el => el.classList.remove("active"));
                item.classList.add("active");
                displaySkillContent(skill.id);
            });

            listContainer.appendChild(item);
        });

        // Auto load first skill
        if (allSkills.length > 0) {
            displaySkillContent(allSkills[0].id);
        }

    } catch (e) {
        listContainer.innerHTML = `<div class="empty-state">Error loading skills: ${e.message}</div>`;
    }
}

async function displaySkillContent(skillId) {
    const title = document.getElementById("viewer-skill-name");
    const meta = document.getElementById("viewer-skill-meta");
    const actions = document.getElementById("viewer-file-selector");
    const contentBox = document.getElementById("viewer-file-content");

    contentBox.textContent = "Loading file content...";

    try {
        const resp = await fetch(`/api/skills/${encodeURIComponent(skillId)}`);
        const data = await resp.json();

        if (!resp.ok) {
            contentBox.textContent = `Error: ${data.error}`;
            return;
        }

        title.textContent = skillId;
        meta.textContent = `${data.path} • ${Object.keys(data.files).length} files • ${data.elements.length} elements mapped`;

        actions.innerHTML = "";
        const fileNames = Object.keys(data.files);

        fileNames.forEach((fname, idx) => {
            const pill = document.createElement("button");
            pill.className = `file-pill ${idx === 0 ? "active" : ""}`;
            pill.textContent = fname;

            pill.addEventListener("click", () => {
                actions.querySelectorAll(".file-pill").forEach(p => p.classList.remove("active"));
                pill.classList.add("active");
                contentBox.textContent = data.files[fname];
            });

            actions.appendChild(pill);
        });

        if (fileNames.length > 0) {
            contentBox.textContent = data.files[fileNames[0]];
        }

    } catch (e) {
        contentBox.textContent = `Failed to fetch skill: ${e.message}`;
    }
}

// -------------------------------------------------------------
// 3. w2s Format Validator
// -------------------------------------------------------------
function initValidator() {
    const runBtn = document.getElementById("btn-run-validation");
    const select = document.getElementById("validator-target-select");
    const badge = document.getElementById("validator-status-badge");
    const summary = document.getElementById("validator-summary-text");
    const container = document.getElementById("validator-details-container");

    refreshValidatorSelect();

    runBtn.addEventListener("click", async () => {
        const target = select.value;
        if (!target) return;

        runBtn.disabled = true;
        badge.className = "badge badge-neutral";
        badge.textContent = "Running...";
        summary.textContent = `Linting ${target} with w2s/validate.py...`;
        container.innerHTML = '<div class="empty-state">Validating schema rules...</div>';

        try {
            const resp = await fetch("/api/validate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ skill_path: target })
            });

            const result = await resp.json();

            if (result.passed) {
                badge.className = "badge badge-success";
                badge.textContent = "PASSED ✓";
                summary.textContent = `Zero errors found! ${result.warnings.length} warnings.`;
            } else {
                badge.className = "badge badge-warning";
                badge.textContent = "FAILED ❌";
                summary.textContent = `${result.errors.length} errors, ${result.warnings.length} warnings.`;
            }

            container.innerHTML = "";

            if (result.errors.length === 0 && result.warnings.length === 0) {
                container.innerHTML = `
                    <div class="log-item success">
                        ✓ All schema checks passed. Frontmatter, routes, element refs, and selectors are compliant with w2s specification.
                    </div>
                `;
            } else {
                result.errors.forEach(err => {
                    const el = document.createElement("div");
                    el.className = "log-item error";
                    el.textContent = err;
                    container.appendChild(el);
                });

                result.warnings.forEach(warn => {
                    const el = document.createElement("div");
                    el.className = "log-item warning";
                    el.textContent = warn;
                    container.appendChild(el);
                });
            }

            showToast(`Validation check completed.`);
        } catch (err) {
            badge.className = "badge badge-warning";
            badge.textContent = "ERROR";
            summary.textContent = err.message;
        } finally {
            runBtn.disabled = false;
        }
    });
}

async function refreshValidatorSelect() {
    const select = document.getElementById("validator-target-select");
    if (!select) return;

    try {
        const resp = await fetch("/api/skills");
        const data = await resp.json();
        const skills = data.skills || [];

        select.innerHTML = "";
        skills.forEach(s => {
            const opt = document.createElement("option");
            opt.value = s.folder;
            opt.textContent = `${s.name} (${s.folder})`;
            select.appendChild(opt);
        });
    } catch (e) {
        // Fallback default options
    }
}

// -------------------------------------------------------------
// 4. AI Agent Automation Simulator
// -------------------------------------------------------------
function initSimulator() {
    const runBtn = document.getElementById("btn-run-simulation");
    const skillSelect = document.getElementById("sim-skill-select");
    const taskInput = document.getElementById("sim-task-input");
    const resultsBox = document.getElementById("sim-results-box");
    const summaryText = document.getElementById("sim-summary-text");

    // Presets
    document.querySelectorAll(".sim-preset").forEach(btn => {
        btn.addEventListener("click", () => {
            taskInput.value = btn.getAttribute("data-task");
            taskInput.focus();
        });
    });

    // Populate skill options
    fetch("/api/skills").then(r => r.json()).then(data => {
        const skills = data.skills || [];
        if (skills.length > 0) {
            skillSelect.innerHTML = "";
            skills.forEach(s => {
                const opt = document.createElement("option");
                opt.value = s.id;
                opt.textContent = `${s.name} (${s.type})`;
                skillSelect.appendChild(opt);
            });
        }
    }).catch(() => {});

    runBtn.addEventListener("click", async () => {
        const task = taskInput.value.trim();
        const skillId = skillSelect.value;

        if (!task) {
            showToast("Please enter an agent goal or task");
            return;
        }

        runBtn.disabled = true;
        summaryText.textContent = "Consulting element inventory and generating execution sequence...";
        resultsBox.innerHTML = '<div class="empty-state">Resolving semantic selectors...</div>';

        try {
            const resp = await fetch("/api/simulate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ task, skill_id: skillId })
            });

            const data = await resp.json();
            if (!resp.ok) {
                resultsBox.innerHTML = `<div class="log-item error">Error: ${data.error}</div>`;
                return;
            }

            summaryText.textContent = `Matched ref "${data.matched_ref}" with selector "${data.target_selector}".`;

            let stepsHtml = "";
            data.actions.forEach(act => {
                stepsHtml += `
                    <div class="sim-step-item">
                        <div class="sim-step-header">
                            <span class="sim-step-title">Step ${act.step}: ${act.action}</span>
                        </div>
                        <div class="sim-step-desc">${act.detail}</div>
                        ${act.code ? `<div class="sim-step-code">${act.code}</div>` : ""}
                    </div>
                `;
            });

            resultsBox.innerHTML = `
                <div style="margin-bottom: 1rem;">${stepsHtml}</div>
                <div class="sidebar-title" style="margin-top: 1.25rem;">Generated Playwright Script:</div>
                <pre class="code-box" style="max-height: 220px;"><code>${escapeHtml(data.playwright_code)}</code></pre>
            `;

            showToast("Agent simulation generated!");
        } catch (e) {
            resultsBox.innerHTML = `<div class="log-item error">Failed: ${e.message}</div>`;
        } finally {
            runBtn.disabled = false;
        }
    });
}
