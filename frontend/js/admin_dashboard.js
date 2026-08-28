const email = localStorage.getItem("email");

if (!email) {
  window.location.href = "login.html";
}

document.getElementById("welcome").innerText =
  "Welcome back, " + email;


// ---------- LOAD SUBJECTS ----------

function loadSubjects() {
  fetch("/subjects")
    .then(res => res.json())
    .then(data => {

      const editSelect =
        document.getElementById("edit_subject");

      const marksSelect =
        document.getElementById("m_subject");

      editSelect.innerHTML =
        '<option value="">Select Subject</option>';

      marksSelect.innerHTML =
        '<option value="">Select Subject</option>';

      data.subjects.forEach(sub => {

        // Edit Subject dropdown
        const editOption =
          document.createElement("option");

        editOption.value = sub.id;

        editOption.textContent =
          `${sub.id} - ${sub.subject_name}`;

        editSelect.appendChild(editOption);


        // Marks dropdown
        const marksOption =
          document.createElement("option");

        marksOption.value = sub.id;

        marksOption.textContent =
          `${sub.id} - ${sub.subject_name}`;

        marksSelect.appendChild(marksOption);
      });

    })
    .catch(() => {
      alert("Unable to load subjects");
    });
}

loadSubjects();


// ---------- STUDENTS ----------

function addStudent() {

  if (!s_roll.value || !s_name.value ||
      !s_semester.value || !s_year.value) {

    alert("Please fill all student fields");
    return;
  }

  fetch("/students", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      roll_no: s_roll.value,
      name: s_name.value,
      semester: parseInt(s_semester.value),
      academic_year: s_year.value
    })
  })
    .then(r => r.json())
    .then(d => {
      alert(d.message || d.error);

      if (d.message) {
        s_roll.value = "";
        s_name.value = "";
        s_semester.value = "";
        s_year.value = "";
      }
    })
    .catch(() => {
      alert("Server error while adding student");
    });
}


function editStudent() {

  if (!s_roll.value || !s_name.value ||
      !s_semester.value || !s_year.value) {

    alert("Please fill all student fields");
    return;
  }

  fetch("/students", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      roll_no: s_roll.value,
      name: s_name.value,
      semester: parseInt(s_semester.value),
      academic_year: s_year.value
    })
  })
    .then(r => r.json())
    .then(d => {
      alert(d.message || d.error);

      if (d.message) {
        s_roll.value = "";
        s_name.value = "";
        s_semester.value = "";
        s_year.value = "";
      }
    })
    .catch(() => {
      alert("Server error while updating student");
    });
}


// ---------- SUBJECTS ----------

function addSubject() {

  const subjectName =
    document.getElementById("subject_name").value.trim();

  if (!subjectName) {
    alert("Please enter subject name");
    return;
  }

  fetch("/subjects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      subject_name: subjectName
    })
  })
    .then(r => r.json())
    .then(d => {
      alert(d.message || d.error);

      if (d.message) {
        document.getElementById("subject_name").value = "";
        loadSubjects();
      }
    })
    .catch(() => {
      alert("Server error while adding subject");
    });
}


function editSubject() {

  const subjectId =
    document.getElementById("edit_subject").value;

  const subjectName =
    document.getElementById("subject_name").value.trim();

  if (!subjectId) {
    alert("Please select an existing subject to edit");
    return;
  }

  if (!subjectName) {
    alert("Please enter subject name");
    return;
  }

  fetch("/subjects", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id: parseInt(subjectId),
      subject_name: subjectName
    })
  })
    .then(r => r.json())
    .then(d => {
      alert(d.message || d.error);

      if (d.message) {
        document.getElementById("edit_subject").value = "";
        document.getElementById("subject_name").value = "";
        loadSubjects();
      }
    })
    .catch(() => {
      alert("Server error while updating subject");
    });
}


// ---------- MARKS ----------

function addMarks() {

  if (!m_roll.value || !m_subject.value || !m_marks.value) {
    alert("Please enter roll number, subject and marks");
    return;
  }

  fetch("/marks", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      roll_no: m_roll.value,
      subject_id: parseInt(m_subject.value),
      marks: parseInt(m_marks.value)
    })
  })
    .then(r => r.json())
    .then(d => alert(d.message || d.error));
}


function editMarks() {

  if (!m_roll.value || !m_subject.value || !m_marks.value) {
    alert("Please enter roll number, subject and marks");
    return;
  }

  fetch("/marks", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      roll_no: m_roll.value,
      subject_id: parseInt(m_subject.value),
      marks: parseInt(m_marks.value)
    })
  })
    .then(r => r.json())
    .then(d => alert(d.message || d.error));
}


// ---------- LOGOUT ----------

function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}