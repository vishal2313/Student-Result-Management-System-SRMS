function calculateGrade(marks) {

  if (marks >= 90) return "A+";
  if (marks >= 80) return "A";
  if (marks >= 70) return "B";
  if (marks >= 60) return "C";
  if (marks >= 50) return "D";
  if (marks >= 40) return "E";

  return "Fail";
}


function getResult() {

  const roll =
    document.getElementById("roll").value.trim();

  const msg =
    document.getElementById("msg");

  const resultDiv =
    document.getElementById("result");


  if (!roll) {

    msg.innerText =
      "Please enter roll number";

    msg.style.color = "red";

    resultDiv.style.display = "none";

    return;
  }


  fetch("http://127.0.0.1:5000/result/" + roll)
    .then(async res => {

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Server error");
      }

      return data;
    })
    .then(data => {

      msg.innerText = "";
      resultDiv.style.display = "block";

      document.getElementById("studentName").innerText =
        data.name;

      document.getElementById("studentRoll").innerText =
        data.roll_no;

      document.getElementById("semester").innerText =
        data.semester;

      document.getElementById("academicYear").innerText =
        data.academic_year;


      const table =
        document.getElementById("marksTable");

      table.innerHTML = "";


      data.subjects.forEach(s => {

        const grade =
          calculateGrade(s.marks);

        table.innerHTML += `
          <tr>
            <td>${s.subject_name}</td>
            <td>${s.marks}</td>
            <td>${grade}</td>
          </tr>
        `;
      });


      document.getElementById("total").innerText =
        data.total;

      document.getElementById("percentage").innerText =
        data.percentage;
    })
    .catch(error => {

      resultDiv.style.display = "none";

      msg.innerText = error.message;
      msg.style.color = "red";

    });
}


function downloadPDF() {

  const roll =
    document.getElementById("roll").value.trim();

  if (!roll) {
    return;
  }

  window.open(
    `/result_pdf/${roll}`,
    "_blank"
  );
}


function logout() {

  localStorage.clear();

  window.location.href =
    "login.html";
}