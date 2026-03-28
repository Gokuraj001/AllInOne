const dropArea = document.getElementById("dropArea");
const fileInput = document.querySelector('input[type="file"]');
const filePreview = document.getElementById("filePreview");
const uploadForm = document.getElementById("uploadForm");
const progressContainer = document.getElementById("progressContainer");
const progressFill = document.getElementById("progressFill");

let droppedFiles = null;

// =======================
// Drag & Drop Handling
// =======================
if (dropArea && fileInput) {
    dropArea.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropArea.classList.add("dragover");
    });

    dropArea.addEventListener("dragleave", () => {
        dropArea.classList.remove("dragover");
    });

    dropArea.addEventListener("drop", (e) => {
        e.preventDefault();
        dropArea.classList.remove("dragover");

        droppedFiles = e.dataTransfer.files;
        showFiles(droppedFiles);
    });

    fileInput.addEventListener("change", () => {
        droppedFiles = fileInput.files;
        showFiles(droppedFiles);
    });
}

// =======================
// File Preview
// =======================
function showFiles(files) {
    if (!filePreview) return;
    filePreview.innerHTML = "";

    if (!files || files.length === 0) {
        filePreview.innerHTML = "<p>No files selected.</p>";
        return;
    }

    Array.from(files).forEach(file => {
        const div = document.createElement("div");
        div.classList.add("file-item");

        const fileSizeKB = (file.size / 1024).toFixed(2);
        div.textContent = `📄 ${file.name} (${fileSizeKB} KB)`;

        filePreview.appendChild(div);
    });
}

// =======================
// Form Submit Handling
// =======================
if (uploadForm) {
    uploadForm.addEventListener("submit", (e) => {
        // If files were dropped, inject them into input using DataTransfer
        if (droppedFiles) {
            const dataTransfer = new DataTransfer();
            Array.from(droppedFiles).forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;
        }

        // Show progress UI if available
        if (progressContainer && progressFill) {
            progressContainer.style.display = "block";

            let width = 0;
            const interval = setInterval(() => {
                if (width >= 95) {
                    clearInterval(interval);
                } else {
                    width += 5;
                    progressFill.style.width = width + "%";
                }
            }, 200);

            // Just before actual submit, push it to 100%
            setTimeout(() => {
                progressFill.style.width = "100%";
            }, 2200);
        }
    });
}