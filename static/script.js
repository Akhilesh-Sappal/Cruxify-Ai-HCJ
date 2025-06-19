// static/script.js

function copySummary() {
  const summary = document.getElementById("summary-text").innerText;
  navigator.clipboard.writeText(summary).then(() => {
    alert("Copied to clipboard!");
  });
}

function downloadSummary() {
  const summary = document.getElementById("summary-text").innerText;
  const format = prompt("Enter format: txt, pdf, docx").toLowerCase();
  let blob;

  if (format === "txt") {
    blob = new Blob([summary], { type: "text/plain" });
  } else {
    alert("Only .txt export is currently supported via browser. Use backend for others.");
    return;
  }

  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `summary.${format}`;
  link.click();
}

// TEXT FORM
document.addEventListener("DOMContentLoaded", () => {
  const textForm = document.getElementById("text-form");
  const docForm = document.getElementById("doc-form");

  if (textForm) {
    textForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(textForm);

      const res = await fetch("/summarize", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      document.getElementById("summary-text").innerText = data.summary;
      document.getElementById("summary-output").style.display = "block";
    });
  }

  if (docForm) {
    docForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(docForm);

      const res = await fetch("/summarize", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      document.getElementById("summary-text").innerText = data.summary;
      document.getElementById("summary-output").style.display = "block";
    });
  }
});
