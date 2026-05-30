const DURATIONS = { focus: 25 * 60, shortBreak: 5 * 60, longBreak: 15 * 60 };
const POMODOROS_BEFORE_LONG = 4;
const CIRCUMFERENCE = 2 * Math.PI * 108;
const SESSION_LABELS = {
  focus: { zh: '专注时间' },
  shortBreak: { zh: '短休息' },
  longBreak: { zh: '长休息' },
};
const SUBTITLES = { idle: '准备开始', running: '进行中…', paused: '已暂停', complete: '时间到！' };

let sessionType = 'focus';
let completedPomodoros = 0;
let totalSeconds = DURATIONS.focus;
let remainingSeconds = DURATIONS.focus;
let isRunning = false;
let intervalId = null;
const originalTitle = document.title;

const body = document.body;
const timeDisplay = document.getElementById('timeDisplay');
const timerSubtitle = document.getElementById('timerSubtitle');
const sessionLabel = document.getElementById('sessionLabel');
const progressCircle = document.getElementById('progressCircle');
const pomodoroDots = document.getElementById('pomodoroDots');
const pomodoroText = document.getElementById('pomodoroText');
const toggleBtn = document.getElementById('toggleBtn');
const toggleLabel = document.getElementById('toggleLabel');
const iconPlay = document.getElementById('iconPlay');
const iconPause = document.getElementById('iconPause');
const resetBtn = document.getElementById('resetBtn');
const skipBtn = document.getElementById('skipBtn');
const soundToggle = document.getElementById('soundToggle');
const timerCard = document.querySelector('.timer-card');

let audioCtx = null;

function getAudioContext() {
  if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  return audioCtx;
}

function playCompletionSound() {
  if (!soundToggle.checked) return;
  try {
    const ctx = getAudioContext();
    const now = ctx.currentTime;
    [523.25, 659.25, 783.99].forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0, now + i * 0.15);
      gain.gain.linearRampToValueAtTime(0.18, now + i * 0.15 + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.001, now + i * 0.15 + 0.5);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now + i * 0.15);
      osc.stop(now + i * 0.15 + 0.55);
    });
  } catch (_) {}
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function updateTabTitle() {
  document.title = isRunning
    ? `${formatTime(remainingSeconds)} · ${SESSION_LABELS[sessionType].zh}`
    : originalTitle;
}

function renderPomodoroDots() {
  pomodoroDots.innerHTML = '';
  for (let i = 0; i < POMODOROS_BEFORE_LONG; i++) {
    const dot = document.createElement('span');
    dot.className = 'pomodoro-dot' + (i < completedPomodoros ? ' pomodoro-dot--filled' : '');
    pomodoroDots.appendChild(dot);
  }
  pomodoroText.textContent = `${completedPomodoros} / ${POMODOROS_BEFORE_LONG}`;
}

function updateProgressRing() {
  progressCircle.style.strokeDashoffset = CIRCUMFERENCE * (1 - remainingSeconds / totalSeconds);
}

function updateModeButtons() {
  document.querySelectorAll('.mode-btn').forEach((btn) => {
    btn.classList.toggle('mode-btn--active', btn.dataset.mode === sessionType);
  });
}

function updateDisplay() {
  timeDisplay.textContent = formatTime(remainingSeconds);
  sessionLabel.textContent = SESSION_LABELS[sessionType].zh;
  body.dataset.session = sessionType;
  updateProgressRing();
  renderPomodoroDots();
  updateModeButtons();
  updateTabTitle();
}

function setSubtitle(key) { timerSubtitle.textContent = SUBTITLES[key]; }

function setRunningUI(running) {
  isRunning = running;
  iconPlay.classList.toggle('hidden', running);
  iconPause.classList.toggle('hidden', !running);
  toggleLabel.textContent = running ? '暂停' : remainingSeconds < totalSeconds ? '继续' : '开始';
  setSubtitle(running ? 'running' : remainingSeconds < totalSeconds ? 'paused' : 'idle');
  updateTabTitle();
}

function setSession(type) {
  sessionType = type;
  totalSeconds = DURATIONS[type];
  remainingSeconds = totalSeconds;
  timerCard.classList.remove('is-complete');
  updateDisplay();
  setSubtitle('idle');
}

function nextSession() {
  if (sessionType === 'focus') {
    completedPomodoros = Math.min(completedPomodoros + 1, POMODOROS_BEFORE_LONG);
    if (completedPomodoros >= POMODOROS_BEFORE_LONG) {
      setSession('longBreak');
      completedPomodoros = 0;
    } else {
      setSession('shortBreak');
    }
  } else {
    setSession('focus');
  }
}

function onComplete() {
  stopTimer();
  setSubtitle('complete');
  timerCard.classList.add('is-complete');
  playCompletionSound();
  setTimeout(() => {
    timerCard.classList.remove('is-complete');
    nextSession();
  }, 1200);
}

function tick() {
  if (remainingSeconds <= 0) { onComplete(); return; }
  remainingSeconds -= 1;
  updateDisplay();
  if (remainingSeconds <= 0) onComplete();
}

function startTimer() {
  if (isRunning) return;
  getAudioContext();
  isRunning = true;
  setRunningUI(true);
  intervalId = setInterval(tick, 1000);
}

function stopTimer() {
  isRunning = false;
  clearInterval(intervalId);
  intervalId = null;
  setRunningUI(false);
}

function toggleTimer() { isRunning ? stopTimer() : startTimer(); }
function resetTimer() {
  stopTimer();
  remainingSeconds = totalSeconds;
  timerCard.classList.remove('is-complete');
  updateDisplay();
  setSubtitle('idle');
}
function skipSession() { stopTimer(); nextSession(); }

progressCircle.style.strokeDasharray = CIRCUMFERENCE;
body.dataset.session = sessionType;
updateDisplay();
setSubtitle('idle');

toggleBtn.addEventListener('click', toggleTimer);
resetBtn.addEventListener('click', resetTimer);
skipBtn.addEventListener('click', skipSession);
document.querySelectorAll('.mode-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    if (btn.dataset.mode === sessionType) return;
    stopTimer();
    setSession(btn.dataset.mode);
  });
});
document.addEventListener('keydown', (e) => {
  if (e.target.matches('input')) return;
  if (e.code === 'Space') { e.preventDefault(); toggleTimer(); }
  else if (e.code === 'KeyR') resetTimer();
});