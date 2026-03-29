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
// Fake Progress Bar
// =======================
if (uploadForm) {
    uploadForm.addEventListener("submit", (e) => {
        e.preventDefault(); // ⛔ STOP default instant submission

        // Attach dropped files safely
        if (droppedFiles && fileInput) {
            const dataTransfer = new DataTransfer();
            Array.from(droppedFiles).forEach(file => dataTransfer.items.add(file));
            fileInput.files = dataTransfer.files;
        }

        if (progressContainer && progressFill) {
            progressContainer.style.display = "block";

            let width = 0;

            const interval = setInterval(() => {
                if (width < 100) {
                    width += 5;
                    progressFill.style.width = width + "%";
                } else {
                    clearInterval(interval);

                    // ✅ Submit AFTER reaching 100%
                    uploadForm.submit();
                }
            }, 100);
        } else {
            // fallback if no progress bar
            uploadForm.submit();
        }
    });
}