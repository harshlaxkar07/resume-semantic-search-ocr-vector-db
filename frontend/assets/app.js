/* Semantic Résumé Search — front end for the résumé vector database API. */
(function () {
  "use strict";

  const { $, $$, el, esc, icon, http, toast, modal, bytes, date, pct } = UI;

  http.base = "";

  const session = [];

  const EXAMPLES = [
    "someone who has built production machine learning pipelines",
    "a backend engineer comfortable with distributed systems",
    "experience leading a small team through a migration",
    "strong data visualisation and reporting background",
    "fresh graduate with solid Python fundamentals",
  ];

  /* ---------------- connection ---------------- */
  async function ping() {
    const node = $("#conn");
    const text = $(".conn-text", node);
    try {
      await http.get("/openapi.json");
      node.className = "conn online";
      text.textContent = "API connected";
    } catch (_) {
      node.className = "conn offline";
      text.textContent = "API unreachable";
    }
  }

  /* ---------------- search ---------------- */
  async function search(e) {
    if (e) e.preventDefault();
    const query = $("#query").value.trim();
    if (!query) {
      toast("Describe who you are looking for first", "warn");
      return;
    }

    const btn = $("#searchBtn");
    btn.classList.add("loading");
    const host = $("#results");
    host.innerHTML = skeleton(4);

    try {
      const data = await http.post("/search", {
        query,
        top_k: Number($("#topK").value) || 10,
      });
      renderResults(data.results || [], query);
    } catch (err) {
      host.innerHTML = `<div class="card"><div class="empty">
        <div class="empty-icon" style="background:var(--danger-soft);color:var(--danger)">${icon("alert", 24)}</div>
        <h3>The search could not run</h3><p>${esc(err.message)}</p>
      </div></div>`;
      toast(err.message, "error");
    } finally {
      btn.classList.remove("loading");
    }
  }

  function renderResults(results, query) {
    const host = $("#results");

    if (!results.length) {
      host.innerHTML = `<div class="card"><div class="empty">
        <div class="empty-icon">${icon("search", 24)}</div>
        <h3>Nothing matched closely enough</h3>
        <p>Try describing the role differently, or index more résumés first.</p>
      </div></div>`;
      return;
    }

    const best = Math.max(...results.map((r) => r.similarity_score || 0), 1);

    host.innerHTML = `
      <div class="card">
        <div class="card-head">
          <h3>Ranked matches</h3>
          <p>Ordered by similarity to &ldquo;${esc(query)}&rdquo;.</p>
          <div class="spacer"></div>
          <span class="badge accent">${results.length} result${results.length === 1 ? "" : "s"}</span>
        </div>
        ${results
          .map(
            (r, i) => `
          <div class="hit">
            <div class="hit-rank">${i + 1}</div>
            <div class="hit-body">
              <div class="hit-name truncate">${esc(r.original_filename || "Résumé")}</div>
              <div class="hit-path truncate">${esc(r.pdf_path || "")}</div>
            </div>
            <div class="hit-score">
              <div class="hit-pct">${pct(r.similarity_score)}</div>
              <div class="hit-label">Similarity</div>
              <div class="meter"><span style="width:${((r.similarity_score || 0) / best) * 100}%"></span></div>
            </div>
          </div>`
          )
          .join("")}
      </div>`;
  }

  function skeleton(n) {
    return `<div class="card">${Array.from({ length: n })
      .map(
        () => `<div class="hit">
      <div class="skeleton" style="width:30px;height:30px;border-radius:9px"></div>
      <div class="hit-body"><div class="skeleton skeleton-line" style="width:46%"></div>
      <div class="skeleton skeleton-line" style="width:64%"></div></div>
      <div class="skeleton" style="width:90px;height:32px"></div></div>`
      )
      .join("")}</div>`;
  }

  /* ---------------- upload ---------------- */
  async function upload(file) {
    if (!/\.pdf$/i.test(file.name)) {
      toast(`${file.name} is not a PDF`, "warn");
      return;
    }

    const chip = el("div", { class: "file-chip" });
    chip.innerHTML = `
      <div class="fi">${icon("file", 16)}</div>
      <div class="fbody">
        <div class="fname">${esc(file.name)}</div>
        <div class="fmeta">${esc(bytes(file.size))} · reading and embedding…</div>
        <div class="progress-bar indeterminate mt-1"><span></span></div>
      </div>`;
    $("#queue").prepend(chip);

    const form = new FormData();
    form.append("file", file);

    try {
      const res = await http.post("/resume/upload", form);
      const resume = res.resume || {};
      const chars = (resume.raw_text || "").length;

      chip.querySelector(".fmeta").textContent = `${bytes(file.size)} · ${chars.toLocaleString()} characters indexed`;
      chip.querySelector(".progress-bar").remove();
      const fi = chip.querySelector(".fi");
      fi.style.background = "var(--ok-soft)";
      fi.style.color = "var(--ok)";
      fi.innerHTML = icon("check", 16);

      session.unshift(resume);
      renderSession();
      showLatest(resume);
      toast(res.message || `${file.name} indexed`, "success");
    } catch (err) {
      chip.querySelector(".fmeta").textContent = err.message;
      chip.querySelector(".fmeta").style.color = "var(--danger)";
      chip.querySelector(".progress-bar").remove();
      const fi = chip.querySelector(".fi");
      fi.style.background = "var(--danger-soft)";
      fi.style.color = "var(--danger)";
      fi.innerHTML = icon("alert", 16);
      toast(err.message, "error");
    }
  }

  function renderSession() {
    const host = $("#sessionList");
    if (!session.length) {
      host.innerHTML = `<div class="empty" style="padding:28px 20px">
        <div class="empty-icon">${icon("inbox", 24)}</div>
        <h3>Nothing indexed yet</h3>
        <p>Résumés you add in this session are listed here.</p></div>`;
      return;
    }

    host.innerHTML = session
      .map(
        (r, i) => `
      <div class="session-row">
        <div class="hit-rank">${icon("fileText", 15)}</div>
        <div class="hit-body">
          <div class="hit-name truncate">${esc(r.original_filename || "Résumé")}</div>
          <div class="hit-path truncate">#${esc(r.id ?? "—")} · ${esc(date(r.uploaded_at, true))}</div>
        </div>
        <button class="btn btn-sm btn-ghost" data-view="${i}">${icon("eye", 13)}</button>
      </div>`
      )
      .join("");

    $$("#sessionList [data-view]").forEach((b) =>
      b.addEventListener("click", () => {
        const r = session[Number(b.dataset.view)];
        modal({
          title: r.original_filename || "Résumé",
          size: "lg",
          body: `
            <dl class="kv mb-2">
              <dt>Record ID</dt><dd class="mono">${esc(r.id ?? "—")}</dd>
              <dt>Stored as</dt><dd class="mono">${esc(r.stored_filename || "—")}</dd>
              <dt>Path</dt><dd class="mono">${esc(r.pdf_path || "—")}</dd>
              <dt>Uploaded</dt><dd>${esc(date(r.uploaded_at, true))}</dd>
              <dt>Characters</dt><dd>${(r.raw_text || "").length.toLocaleString()}</dd>
            </dl>
            <div class="extract">${esc(r.raw_text || "No text was extracted.")}</div>`,
        });
      })
    );
  }

  function showLatest(r) {
    $("#latest").innerHTML = `
      <div class="row mb-2" style="gap:12px">
        <div class="avatar lg">${icon("fileText", 20)}</div>
        <div style="min-width:0">
          <h3 class="truncate">${esc(r.original_filename || "Résumé")}</h3>
          <div class="muted small">${(r.raw_text || "").length.toLocaleString()} characters extracted</div>
        </div>
      </div>
      <dl class="kv mb-2">
        <dt>Record ID</dt><dd class="mono">${esc(r.id ?? "—")}</dd>
        <dt>Stored as</dt><dd class="mono truncate">${esc(r.stored_filename || "—")}</dd>
        <dt>Uploaded</dt><dd>${esc(date(r.uploaded_at, true))}</dd>
      </dl>
      <div class="extract">${esc((r.raw_text || "").slice(0, 4000) || "No text was extracted.")}</div>`;
  }

  /* ---------------- boot ---------------- */
  function init() {
    UI.shell({ start: "search" });

    $("#searchForm").addEventListener("submit", search);

    $("#examples").innerHTML = EXAMPLES.map(
      (q) => `<button class="chip" type="button">${esc(q)}</button>`
    ).join("");
    $$("#examples .chip").forEach((c) =>
      c.addEventListener("click", () => {
        $("#query").value = c.textContent;
        search();
      })
    );

    UI.dropzone($("#dropzone"), (files) => [].concat(files).forEach(upload), {
      accept: "application/pdf",
      multiple: true,
    });

    renderSession();
    ping();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
