# 番茄钟 · Pomodoro Timer

一个简洁美观的番茄钟网页应用，帮助你在专注与休息之间保持节奏。

A beautiful, standalone Pomodoro timer web app to balance focus and rest.

## 功能 · Features

- **25 分钟专注** · 25-minute focus sessions
- **5 分钟短休息** · 5-minute short breaks
- **15 分钟长休息** · 15-minute long break after every 4 pomodoros
- **开始 / 暂停 / 重置** · Start, pause, and reset controls
- **跳过当前阶段** · Skip to next session
- **环形进度指示** · Circular progress ring
- **番茄计数器** · Pomodoro counter (e.g. 2 / 4)
- **完成提示音** · Optional completion chime (Web Audio API)
- **标签页标题倒计时** · Remaining time shown in browser tab title
- **键盘快捷键** · Space = start/pause, R = reset

## 使用方法 · How to Run

### 方式一：直接打开 · Open directly

双击 `index.html` 或在浏览器中打开该文件。

Double-click `index.html` or open it in any modern browser.

### 方式二：本地服务器 · Local server (optional)

```bash
python -m http.server 8080
# or: npx serve .
```

然后在浏览器访问 `http://localhost:8080`

## 项目结构 · Structure

```
pomodoro-timer/
├── index.html
├── css/styles.css
├── js/app.js
└── README.md
```

Vanilla HTML, CSS, and JavaScript — no build step required.