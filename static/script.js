function goTo(view, el) {
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.getElementById('view-' + view).classList.add('active');
  document.querySelectorAll('nav.navlist a').forEach(a => a.classList.remove('active'));
  if (el) {
    el.classList.add('active');
  } else {
    const map = ['home', 'form', 'result', 'about'];
    document.querySelectorAll('nav.navlist a').forEach((a, i) => {
      if (map[i] === view) a.classList.add('active');
    });
  }
  window.scrollTo({ top: 0, behavior: 'instant' });
}

document.querySelectorAll('.likert-options').forEach(group => {
  group.addEventListener('click', e => {
    const btn = e.target.closest('button');
    if (!btn) return;
    group.querySelectorAll('button').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
  });
});

function getLikert(field) {
  const sel = document.querySelector('.likert-options[data-field="' + field + '"] button.selected');
  return sel ? parseInt(sel.dataset.val, 10) : 3;
}

// ---------- เชื่อมกับ Flask backend จริง (/predict) ----------
async function computeResult() {
  const errorEl = document.getElementById('formError');
  const submitBtn = document.getElementById('submitBtn');
  errorEl.textContent = '';

  const payload = {
    gender: document.getElementById('gender').value,
    age: document.getElementById('age').value,
    academicPressure: getLikert('academicPressure'),
    studySatisfaction: getLikert('studySatisfaction'),
    sleep: document.getElementById('sleep').value,
    diet: document.getElementById('diet').value,
    studyHours: document.getElementById('studyHours').value,
    financialStress: getLikert('financialStress'),
    familyHistory: document.getElementById('familyHistory').value,
    cgpa: document.getElementById('cgpa').value,
  };

  submitBtn.disabled = true;
  submitBtn.textContent = 'กำลังประมวลผล...';

  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      errorEl.textContent = data.error || 'เกิดข้อผิดพลาด กรุณาลองใหม่อีกครั้ง';
      return;
    }

    showResult(data.prediction, data.probability);
    goTo('result');

  } catch (err) {
    errorEl.textContent = 'ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้ กรุณาลองใหม่อีกครั้ง';
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'ประเมินความเสี่ยง →';
  }
}

function showResult(prediction, probabilityPct) {
  const badge = document.getElementById('resultBadge');
  const bar = document.getElementById('resultBar');
  const title = document.getElementById('resultTitle');
  const desc = document.getElementById('resultDesc');
  const resourceBox = document.getElementById('resourceBox');

  // probabilityPct = ความน่าจะเป็นที่โมเดลทำนายว่า "เป็นซึมเศร้า" (0-100)
  let level;
  if (probabilityPct < 35) level = 'low';
  else if (probabilityPct < 65) level = 'mid';
  else level = 'high';

  badge.className = 'result-badge ' + level;
  bar.className = 'bar-fill ' + level;
  bar.style.width = probabilityPct + '%';
  document.getElementById('resultPct').textContent = probabilityPct + '%';

  const copy = {
    low: ['ความเสี่ยงต่ำ', 'ตอนนี้ดูเหมือนคุณกำลังไปได้ดี', 'จากข้อมูลที่กรอก โมเดลประเมินว่าความเสี่ยงโดยรวมอยู่ในระดับต่ำ ลองรักษาพฤติกรรมที่ดีนี้ต่อไป'],
    mid: ['ความเสี่ยงปานกลาง', 'มีบางจุดที่น่าจะลองดูแลเพิ่มเติม', 'โมเดลพบปัจจัยเสี่ยงบางส่วนจากข้อมูลที่กรอก ลองปรับสมดุลชีวิตและสังเกตตัวเองต่อไป'],
    high: ['ความเสี่ยงสูง', 'คุณอาจกำลังแบกรับความเครียดมากอยู่', 'โมเดลพบปัจจัยเสี่ยงหลายด้านจากข้อมูลที่กรอก การพูดคุยกับผู้เชี่ยวชาญจะช่วยให้คุณได้รับการดูแลที่เหมาะสม'],
  };
  badge.textContent = copy[level][0];
  title.textContent = copy[level][1];
  desc.textContent = copy[level][2];
  resourceBox.style.display = level === 'low' ? 'none' : 'block';
}