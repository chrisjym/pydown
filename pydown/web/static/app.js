"use strict";

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const statusEl = document.getElementById("status");
const successEl = document.getElementById("success");
const errorEl = document.getElementById("error");

// --- Drag & drop wiring -----------------------------------------------------
dropzone.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    fileInput.click();
  }
});
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) handleFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((evt) =>
  dropzone.addEventListener(evt, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);
dropzone.addEventListener("drop", (e) => {
  const files = e.dataTransfer.files;
  if (files && files.length) handleFile(files[0]);
});

// --- Convert then auto-download the .md -------------------------------------
async function handleFile(file) {
  hide(errorEl);
  hide(successEl);
  show(statusEl, `Converting “${file.name}”…`);

  const body = new FormData();
  body.append("file", file);

  try {
    const res = await fetch("/convert", { method: "POST", body });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || `Request failed (${res.status}).`);
    }
    const mdName = filenameFromResponse(res, file.name);
    const blob = await res.blob();
    triggerDownload(blob, mdName);
    show(successEl, `Downloaded ${mdName}`);
  } catch (err) {
    show(errorEl, err.message);
  } finally {
    hide(statusEl);
    fileInput.value = ""; // allow re-selecting the same file
  }
}

function triggerDownload(blob, name) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

// Prefer the server's Content-Disposition filename; fall back to the source name.
function filenameFromResponse(res, sourceName) {
  const disp = res.headers.get("Content-Disposition") || "";
  const match = disp.match(/filename="?([^"]+)"?/);
  if (match) return match[1];
  return sourceName.replace(/\.[^.]+$/, "") + ".md";
}

// --- Helpers ----------------------------------------------------------------
function show(el, text) {
  if (text !== undefined) el.textContent = text;
  el.hidden = false;
}
function hide(el) {
  el.hidden = true;
}
