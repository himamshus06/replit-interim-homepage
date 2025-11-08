// Final working version with PDF download
document.addEventListener("DOMContentLoaded", () => {
  const { jsPDF } = window.jspdf;

  const SUBJECTS_DATA = {
    Physics: ["Electrostatics", "Optics", "Modern Physics", "Mechanics", "Waves", "Thermodynamics"],
    Mathematics: ["Calculus", "Algebra", "Coordinate Geometry", "Trigonometry", "Probability", "Vectors"],
    Chemistry: ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Chemical Bonding", "Equilibrium"],
    Biology: ["Genetics", "Ecology", "Human Physiology", "Plant Morphology", "Cell Biology"],
    English: ["Grammar", "Writing Skills", "Comprehension", "Literature", "Vocabulary"],
  };

  const HABIT_TEMPLATES = {
    conceptual: [
      "Watch one 10-minute video on {topic}.",
      "Explain {topic} without notes.",
      "Draw a mind map for {topic}.",
    ],
    application: [
      "Solve 2 {topic} problems daily.",
      "Revisit a wrong {topic} question and fix it.",
      "Do a 15-min timed drill for {topic}.",
    ],
    retention: [
      "Make flashcards for {topic}.",
      "Review {topic} before sleep.",
      "Teach {topic} for 5 minutes aloud.",
    ],
    practice: [
      "Weekly mini test on {topic}.",
      "Mix {topic} with other subjects for recall.",
      "Skim strong topic {topic} once per week.",
    ],
  };

  const subjects = [];

  // Populate dropdown
  const subjectSelect = document.getElementById("subjectSelect");
  Object.keys(SUBJECTS_DATA).forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    subjectSelect.appendChild(opt);
  });

  document.getElementById("addSubjectBtn").addEventListener("click", () => {
    const subject = subjectSelect.value;
    if (!subject) return alert("Please select a subject!");
    if (subjects.find((s) => s.name === subject)) return alert("Subject already added!");
    subjects.push({ name: subject, topics: [] });
    subjectSelect.value = "";
    renderSubjects();
  });

  document.getElementById("analyzeBtn").addEventListener("click", () => {
    if (subjects.length === 0) return alert("Add subjects first!");
    const allTopics = subjects.flatMap((s) => s.topics);
    if (allTopics.length === 0) return alert("Add at least one topic!");

    const analysis = analyzePerformance();
    displayAnalysis(analysis);
    displayHabits(analysis);
  });

  document.getElementById("downloadBtn").addEventListener("click", downloadPDF);

  function renderSubjects() {
    const container = document.getElementById("subjectsContainer");
    container.innerHTML = "";

    if (!subjects.length) {
      container.innerHTML = '<p class="no-subjects">No subjects added yet.</p>';
      return;
    }

    subjects.forEach((subject, i) => {
      const card = document.createElement("div");
      card.className = "subject-card";
      card.innerHTML = `
        <h3>${subject.name}</h3>
        <div id="topics-${i}">${renderTopicsList(subject.topics, i)}</div>
        <div class="topic-controls">
          <div class="input-group">
            <label>Select Topic:</label>
            <select id="topicSelect-${i}">
              <option value="">Choose topic</option>
              ${SUBJECTS_DATA[subject.name]
                .map((t) => `<option value="${t}">${t}</option>`)
                .join("")}
            </select>
          </div>
          <div class="input-group">
            <label>Marks (0–100):</label>
            <input type="number" id="marksInput-${i}" min="0" max="100" placeholder="Enter marks">
          </div>
          <button onclick="addTopic(${i})">➕</button>
          <button onclick="removeSubject(${i})" class="remove-btn">✖</button>
        </div>`;
      container.appendChild(card);
    });
  }

  window.addTopic = function (i) {
    const topic = document.getElementById(`topicSelect-${i}`).value;
    const marks = parseInt(document.getElementById(`marksInput-${i}`).value);
    if (!topic || isNaN(marks) || marks < 0 || marks > 100)
      return alert("Enter valid topic and marks between 0–100");
    const subj = subjects[i];
    if (subj.topics.find((t) => t.name === topic)) return alert("Topic already added!");
    subj.topics.push({ name: topic, marks });
    renderSubjects();
  };

  window.removeSubject = function (i) {
    subjects.splice(i, 1);
    renderSubjects();
  };

  window.removeTopic = function (i, name) {
    subjects[i].topics = subjects[i].topics.filter((t) => t.name !== name);
    renderSubjects();
  };

  function renderTopicsList(topics, i) {
    if (!topics.length) return '<p class="no-topics">No topics added yet.</p>';
    return topics
      .map(
        (t) => `
      <div class="topic-input">
        <strong>${t.name}</strong>
        <span>Marks: ${t.marks}/100</span>
        <span class="priority-badge ${getPriorityClass(t.marks)}">${getPriorityText(t.marks)}</span>
        <button onclick="removeTopic(${i}, '${t.name}')" class="remove-btn">✖</button>
      </div>`
      )
      .join("");
  }

  function getPriorityClass(p) {
    if (p < 60) return "priority-high";
    if (p < 80) return "priority-medium";
    return "priority-low";
  }

  function getPriorityText(p) {
    if (p < 60) return "Needs Improvement";
    if (p < 80) return "Moderate";
    return "Strong";
  }

  function analyzePerformance() {
    const result = { weak: [], moderate: [], strong: [] };
    subjects.forEach((s) => {
      s.topics.forEach((t) => {
        if (t.marks < 60) result.weak.push({ subject: s.name, topic: t.name, marks: t.marks });
        else if (t.marks < 80) result.moderate.push({ subject: s.name, topic: t.name, marks: t.marks });
        else result.strong.push({ subject: s.name, topic: t.name, marks: t.marks });
      });
    });
    return result;
  }

  function displayAnalysis(a) {
    const out = document.getElementById("improvementAreas");
    let html = "";
    if (a.weak.length)
      html += `<div class="analysis-card priority-high"><h3>High Priority</h3>${a.weak
        .map((x) => `<p><b>${x.subject}</b> - ${x.topic} (${x.marks}%)</p>`)
        .join("")}</div>`;
    if (a.moderate.length)
      html += `<div class="analysis-card priority-medium"><h3>Moderate Priority</h3>${a.moderate
        .map((x) => `<p><b>${x.subject}</b> - ${x.topic} (${x.marks}%)</p>`)
        .join("")}</div>`;
    if (a.strong.length)
      html += `<div class="analysis-card priority-low"><h3>Strong Areas</h3>${a.strong
        .map((x) => `<p><b>${x.subject}</b> - ${x.topic} (${x.marks}%)</p>`)
        .join("")}</div>`;
    out.innerHTML = html;
    document.getElementById("analysisSection").style.display = "block";
  }

  function displayHabits(a) {
    const out = document.getElementById("habitsOutput");
    let html = "";

    const addHabit = (title, list, type, color) => {
      if (!list.length) return;
      html += `<div class="analysis-card ${color}"><h3>${title}</h3>`;
      list.forEach((x) => {
        const t = pickTemplate(type, x.topic);
        html += `<p><b>${x.subject}</b> - ${x.topic}: ${t}</p>`;
      });
      html += "</div>";
    };

    addHabit("High Priority Habits (Daily)", a.weak, "conceptual", "priority-high");
    addHabit("Moderate Priority Habits (3–4x/week)", a.moderate, "application", "priority-medium");
    addHabit("Strong Area Habits (Weekly)", a.strong, "practice", "priority-low");

    out.innerHTML = html;
    document.getElementById("habitsSection").style.display = "block";
  }

  function pickTemplate(type, topic) {
    const arr = HABIT_TEMPLATES[type] || HABIT_TEMPLATES.practice;
    return arr[Math.floor(Math.random() * arr.length)].replace("{topic}", topic);
  }

  // ✅ Generate and download PDF
  function downloadPDF() {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("Study Habit Plan", 14, 15);

    const habits = document.getElementById("habitsOutput").innerText;
    doc.setFontSize(12);
    doc.text(habits || "No plan generated yet.", 14, 25, { maxWidth: 180 });

    doc.save("study-habit-plan.pdf");
  }
});
