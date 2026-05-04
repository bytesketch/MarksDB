const API_BASE = "";

let currentStudent = null;
let subjects = {};
let timings = {};
let allStudents = {};
let allMarks = {};

document.addEventListener("DOMContentLoaded", () => {
  initializeEventListeners();
  loadInitialData();
  showPage("home");
});

function initializeEventListeners() {
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const page = link.dataset.page;
      showPage(page);
    });
  });

  document.getElementById("addStudentBtn").addEventListener("click", () => {
    openStudentModal();
  });

  document.getElementById("studentForm").addEventListener("submit", (e) => {
    e.preventDefault();
    saveStudent();
  });

  document
    .getElementById("studentModalClose")
    .addEventListener("click", closeStudentModal);
  document
    .querySelectorAll(".modal-close")[0]
    .addEventListener("click", closeStudentModal);

  document.getElementById("addMarkBtn").addEventListener("click", () => {
    openMarkModal();
  });

  document.getElementById("markForm").addEventListener("submit", (e) => {
    e.preventDefault();
    saveMark();
  });

  document
    .getElementById("markModalClose")
    .addEventListener("click", closeMarkModal);
  document
    .querySelectorAll(".modal-close")[1]
    .addEventListener("click", closeMarkModal);

  document.getElementById("backToStudents").addEventListener("click", () => {
    currentStudent = null;
    showPage("students");
  });

  document
    .getElementById("cancelDelete")
    .addEventListener("click", closeConfirmModal);
}

function showPage(pageName) {
  document.querySelectorAll(".page").forEach((page) => {
    page.classList.remove("active");
  });

  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.remove("active");
  });

  const page = document.getElementById(pageName);
  if (page) {
    page.classList.add("active");
  }

  const activeLink = document.querySelector(`[data-page="${pageName}"]`);
  if (activeLink) {
    activeLink.classList.add("active");
  }

  switch (pageName) {
    case "home":
      loadHomePage();
      break;
    case "dashboard":
      loadDashboard();
      break;
    case "students":
      loadStudents();
      break;
    case "marks":
      loadMarks();
      break;
  }
}

async function loadInitialData() {
  try {
    const subjectsRes = await fetch(`${API_BASE}/api/subjects`);
    const subjectsData = await subjectsRes.json();
    if (subjectsData.status === "success") {
      subjects = subjectsData.data;
    }

    const timingsRes = await fetch(`${API_BASE}/api/timing`);
    const timingsData = await timingsRes.json();
    if (timingsData.status === "success") {
      timings = timingsData.data;
    }

    populateSelectOptions();
  } catch (error) {
    showNotification("Error loading initial data", "error");
  }
}

function populateSelectOptions() {
  const subjectSelect = document.getElementById("subject");
  subjectSelect.innerHTML = '<option value="">Select Subject</option>';
  Object.entries(subjects).forEach(([id, name]) => {
    const option = document.createElement("option");
    option.value = id;
    option.textContent = name;
    subjectSelect.appendChild(option);
  });

  const timingSelect = document.getElementById("timing");
  timingSelect.innerHTML = '<option value="">Select Timing</option>';
  Object.entries(timings).forEach(([id, name]) => {
    const option = document.createElement("option");
    option.value = id;
    option.textContent = name;
    timingSelect.appendChild(option);
  });
}

async function loadHomePage() {
  try {
    const schoolRes = await fetch(`${API_BASE}/api/school/info`);
    const schoolData = await schoolRes.json();

    const schoolInfoContainer = document.getElementById("schoolInfo");
    if (schoolData.status === "success") {
      const data = schoolData.data;
      let remarksHtml = "";
      if (Array.isArray(data.remarks)) {
        remarksHtml = data.remarks.map((r) => `<li>${r}</li>`).join("");
      }
      const html = `
                <div class="school-info-name">${data.name || "School Name"}</div>
                <div class="school-info-address">${
                  data.address[0] +
                    ", " +
                    data.address[1] +
                    "-" +
                    data.address[2] +
                    ", " +
                    data.address[3] +
                    ", " +
                    data.address[4] || "School Address"
                }</div>
                <div class="school-info-description">${data.description || "School Description"}</div>
                ${remarksHtml ? `<ul class="school-info-remarks">${remarksHtml}</ul>` : ""}
            `;
      schoolInfoContainer.innerHTML = html;
    } else {
      schoolInfoContainer.innerHTML =
        '<p class="error">Failed to load school information</p>';
    }

    const devRes = await fetch(`${API_BASE}/api/developer`);
    const devData = await devRes.json();

    const developerInfo = document.getElementById("developerInfo");
    if (devData.status === "success") {
      const data = devData.data;
      developerInfo.innerHTML = `
                <div class="developer-info-row">
                    <span class="developer-label">Name:</span>
                    <span class="developer-value">${data.name}</span>
                </div>
                <div class="developer-info-row">
                    <span class="developer-label">GitHub:</span>
                    <span class="developer-value">
                        <a href="https://github.com/${data.github}" target="_blank">@${data.github}</a>
                    </span>
                </div>
            `;
    } else {
      developerInfo.innerHTML =
        '<p class="error">Failed to load developer information</p>';
    }
  } catch (error) {
    showNotification("Error loading home page", "error");
  }
}

async function loadDashboard() {
  try {
    const response = await fetch(`${API_BASE}/api/student/get`);
    const data = await response.json();

    const dashboardContent = document.getElementById("dashboardContent");

    if (
      data.status !== "success" ||
      !data.data ||
      Object.keys(data.data).length === 0
    ) {
      dashboardContent.innerHTML = '<p class="loading">No students found</p>';
      return;
    }

    allStudents = data.data;

    const studentsByClass = {};
    Object.entries(data.data).forEach(([srno, student]) => {
      const clazz = student.class;
      if (!studentsByClass[clazz]) {
        studentsByClass[clazz] = [];
      }
      studentsByClass[clazz].push({ srno, ...student });
    });

    let html = "";
    Object.entries(studentsByClass)
      .sort()
      .forEach(([clazz, students]) => {
        html += `<div class="class-group">`;
        html += `<div class="class-group-title">Class ${clazz}</div>`;

        const topStudents = students.slice(0, 3);

        topStudents.forEach((student, index) => {
          const rank = index + 1;
          html += `
                    <div class="student-rank">
                        <div class="rank-badge rank-${rank}">${rank}</div>
                        <div class="rank-info">
                            <div class="rank-name">${student.name}</div>
                            <div class="rank-stats">Roll: ${student.roll}</div>
                        </div>
                    </div>
                `;
        });

        html += `</div>`;
      });

    dashboardContent.innerHTML = html;
  } catch (error) {
    showNotification("Error loading dashboard", "error");
  }
}

async function loadStudents() {
  try {
    const response = await fetch(`${API_BASE}/api/student/get`);
    const data = await response.json();

    const studentsContent = document.getElementById("studentsContent");

    if (
      data.status !== "success" ||
      !data.data ||
      Object.keys(data.data).length === 0
    ) {
      studentsContent.innerHTML =
        '<p class="loading">No students found. Add one to get started.</p>';
      return;
    }

    allStudents = data.data;

    const studentsByClass = {};
    Object.entries(data.data).forEach(([srno, student]) => {
      const clazz = student.class;
      if (!studentsByClass[clazz]) {
        studentsByClass[clazz] = [];
      }
      studentsByClass[clazz].push({ srno, ...student });
    });

    let html = "";
    Object.entries(studentsByClass)
      .sort()
      .forEach(([clazz, students]) => {
        students.forEach((student) => {
          html += `
                    <div class="student-card">
                        <div class="student-card-header">
                            <div class="student-card-name">${student.name}</div>
                            <div class="student-card-actions">
                                <button class="btn btn-primary btn-icon btn-small" onclick="editStudent('${student.srno}')" title="Edit">✎</button>
                                <button class="btn btn-danger btn-icon btn-small" onclick="deleteStudent('${student.srno}')" title="Delete">✕</button>
                            </div>
                        </div>
                        <div class="student-card-info">
                            <div class="student-info-row">
                                <span class="student-info-label">SR. No</span>
                                <span class="student-info-value">${student.srno}</span>
                            </div>
                            <div class="student-info-row">
                                <span class="student-info-label">Class</span>
                                <span class="student-info-value">${student.class}</span>
                            </div>
                            <div class="student-info-row">
                                <span class="student-info-label">Roll No</span>
                                <span class="student-info-value">${student.roll}</span>
                            </div>
                        </div>
                        <div class="student-card-footer">
                            <button class="btn-view-marks" onclick="viewStudentMarks('${student.srno}', '${student.name}')">View Marks</button>
                        </div>
                    </div>
                `;
        });
      });

    studentsContent.innerHTML = html;
  } catch (error) {
    showNotification("Error loading students", "error");
  }
}

async function loadMarks() {
  if (!currentStudent) {
    showPage("students");
    return;
  }

  try {
    const response = await fetch(
      `${API_BASE}/api/marks/${currentStudent.srno}/get`,
    );
    const data = await response.json();

    const marksContent = document.getElementById("marksContent");
    document.getElementById("marksStudentName").textContent =
      `${currentStudent.name} - Marks`;

    if (
      data.status !== "success" ||
      !data.data ||
      Object.keys(data.data).length === 0
    ) {
      marksContent.innerHTML =
        '<p class="loading">No marks found. Add one to get started.</p>';
      return;
    }

    allMarks = data.data;

    let html = "";
    Object.entries(data.data).forEach(([recordId, mark]) => {
      const percentage = ((mark.marks / mark.max_marks) * 100).toFixed(2);
      html += `
                <div class="mark-card">
                    <div class="mark-header">
                        <div class="mark-subject">${subjects[mark.subject] || "Unknown Subject"}</div>
                        <div class="mark-actions">
                            <button class="btn btn-warning btn-icon btn-small" onclick="editMark('${recordId}')" title="Edit">✎</button>
                            <button class="btn btn-danger btn-icon btn-small" onclick="deleteMark('${recordId}')" title="Delete">✕</button>
                        </div>
                    </div>
                    <div class="mark-details">
                        <div class="mark-detail-row">
                            <span class="mark-label">Timing</span>
                            <span class="mark-value">${timings[mark.timing] || "Unknown"}</span>
                        </div>
                        <div class="mark-detail-row">
                            <span class="mark-label">Obtained</span>
                            <span class="mark-value">${mark.marks}</span>
                        </div>
                        <div class="mark-detail-row">
                            <span class="mark-label">Max Marks</span>
                            <span class="mark-value">${mark.max_marks}</span>
                        </div>
                    </div>
                    <div class="mark-percentage">
                        <div class="percentage-label">Percentage</div>
                        <div class="percentage-value">${percentage}%</div>
                    </div>
                </div>
            `;
    });

    marksContent.innerHTML = html;
  } catch (error) {
    showNotification("Error loading marks", "error");
  }
}

function openStudentModal(srno = null) {
  const form = document.getElementById("studentForm");
  const modal = document.getElementById("studentModal");
  const title = document.getElementById("studentModalTitle");

  if (srno) {
    title.textContent = "Edit Student";
    const student = allStudents[srno];
    document.getElementById("srno").value = srno;
    document.getElementById("srno").disabled = true;
    document.getElementById("name").value = student.name;
    document.getElementById("class").value = student.class;
    document.getElementById("roll").value = student.roll;
    form.dataset.mode = "edit";
    form.dataset.srno = srno;
  } else {
    title.textContent = "Add Student";
    form.reset();
    document.getElementById("srno").disabled = false;
    form.dataset.mode = "add";
  }

  modal.classList.add("active");
}

function closeStudentModal() {
  document.getElementById("studentModal").classList.remove("active");
  document.getElementById("studentForm").reset();
}

async function saveStudent() {
  const form = document.getElementById("studentForm");
  const mode = form.dataset.mode;

  const studentData = {
    srno: parseInt(document.getElementById("srno").value),
    name: document.getElementById("name").value,
    class: parseInt(document.getElementById("class").value),
    roll: parseInt(document.getElementById("roll").value),
  };

  try {
    let response;
    if (mode === "add") {
      response = await fetch(`${API_BASE}/api/students/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(studentData),
      });
    } else {
      response = await fetch(
        `${API_BASE}/api/student/${studentData.srno}/modify`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: studentData.name,
            class: studentData.class,
            roll: studentData.roll,
          }),
        },
      );
    }

    const data = await response.json();
    if (data.status === "success") {
      showNotification(data.message, "success");
      closeStudentModal();
      loadStudents();
    } else {
      showNotification(data.message, "error");
    }
  } catch (error) {
    showNotification("Error saving student", "error");
  }
}

async function editStudent(srno) {
  openStudentModal(srno);
}

async function deleteStudent(srno) {
  showConfirmModal(
    "Are you sure you want to delete this student?",
    async () => {
      try {
        const response = await fetch(`${API_BASE}/api/student/${srno}/del`, {
          method: "POST",
        });

        const data = await response.json();
        if (data.status === "success") {
          showNotification("Student deleted successfully", "success");
          loadStudents();
        } else {
          showNotification(data.message, "error");
        }
      } catch (error) {
        showNotification("Error deleting student", "error");
      }
    },
  );
}

function openMarkModal(recordId = null) {
  const form = document.getElementById("markForm");
  const modal = document.getElementById("markModal");
  const title = document.getElementById("markModalTitle");

  if (recordId) {
    title.textContent = "Edit Mark Record";
    const mark = allMarks[recordId];
    document.getElementById("subject").value = mark.subject;
    document.getElementById("timing").value = mark.timing;
    document.getElementById("max").value = mark.max_marks;
    document.getElementById("obtained").value = mark.marks;
    form.dataset.mode = "edit";
    form.dataset.recordId = recordId;
  } else {
    title.textContent = "Add Mark Record";
    form.reset();
    form.dataset.mode = "add";
  }

  modal.classList.add("active");
}

function closeMarkModal() {
  document.getElementById("markModal").classList.remove("active");
  document.getElementById("markForm").reset();
}

async function saveMark() {
  const form = document.getElementById("markForm");
  const mode = form.dataset.mode;

  const markData = {
    subject: parseInt(document.getElementById("subject").value),
    timing: parseInt(document.getElementById("timing").value),
    max: parseFloat(document.getElementById("max").value),
    obtained: parseFloat(document.getElementById("obtained").value),
  };

  try {
    let response;
    if (mode === "add") {
      response = await fetch(`${API_BASE}/marks/${currentStudent.srno}/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(markData),
      });
    } else {
      const recordId = form.dataset.recordId;
      response = await fetch(`${API_BASE}/marks/${recordId}/update`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(markData),
      });
    }

    const data = await response.json();
    if (data.status === "success") {
      showNotification(data.message, "success");
      closeMarkModal();
      loadMarks();
    } else {
      showNotification(data.message, "error");
    }
  } catch (error) {
    showNotification("Error saving mark", "error");
  }
}

async function editMark(recordId) {
  openMarkModal(recordId);
}

async function deleteMark(recordId) {
  showConfirmModal(
    "Are you sure you want to delete this mark record?",
    async () => {
      try {
        const response = await fetch(`${API_BASE}/marks/${recordId}/del`, {
          method: "POST",
        });

        const data = await response.json();
        if (data.status === "success") {
          showNotification("Mark record deleted successfully", "success");
          loadMarks();
        } else {
          showNotification(data.message, "error");
        }
      } catch (error) {
        showNotification("Error deleting mark", "error");
      }
    },
  );
}

function viewStudentMarks(srno, name) {
  currentStudent = { srno, name };
  showPage("marks");
}

function showConfirmModal(message, onConfirm) {
  const modal = document.getElementById("confirmModal");
  document.getElementById("confirmMessage").textContent = message;

  const confirmBtn = document.getElementById("confirmDelete");
  const cancelBtn = document.getElementById("cancelDelete");

  confirmBtn.onclick = () => {
    onConfirm();
    closeConfirmModal();
  };

  modal.classList.add("active");
}

function closeConfirmModal() {
  document.getElementById("confirmModal").classList.remove("active");
}

function showNotification(message, type = "info") {
  const notification = document.getElementById("notification");
  notification.textContent = message;
  notification.className = `notification ${type} show`;

  setTimeout(() => {
    notification.classList.remove("show");
    notification.classList.add("hide");
    setTimeout(() => {
      notification.classList.remove("hide");
    }, 300);
  }, 3000);
}
