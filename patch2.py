with open('index.html', 'r') as f:
    content = f.read()

# 1) Remove the floating rest banner from CSS
old_css = '''/* FIXED REST TIMER BANNER */
.rest-banner { position:fixed; top:0; left:0; right:0; z-index:150; background:linear-gradient(135deg,#1a0f00,#0a1528); border-bottom:3px solid var(--gold); padding:10px 16px; display:none; align-items:center; justify-content:space-between; gap:12px; box-shadow:0 4px 24px rgba(0,0,0,0.7); }
.rest-banner.active { display:flex; }
.rest-banner-time { font-size:40px; font-weight:900; color:var(--gold); font-family:'Righteous',sans-serif; line-height:1; }
.rest-banner-label { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:2px; }'''

new_css = '''/* INLINE REST TIMER (between exercise cards) */
.rest-banner { background:rgba(14,165,233,0.08); border:1px solid rgba(14,165,233,0.3); border-radius:12px; padding:10px 14px; display:none; align-items:center; justify-content:space-between; margin-bottom:12px; }
.rest-banner.active { display:flex; }
.rest-banner-time { font-size:26px; font-weight:900; color:var(--blue); font-family:'Righteous',sans-serif; line-height:1; }
.rest-banner-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:2px; }'''

if old_css in content:
    content = content.replace(old_css, new_css, 1)
    print("✅ CSS patched")
else:
    print("❌ CSS not found")

# 2) Remove the floating banner HTML div
old_html = '''<!-- FLOATING REST TIMER BANNER -->
<div class="rest-banner" id="rest-banner">
  <div>
    <div class="rest-banner-label">⏱️ Rest Timer</div>
    <div class="rest-banner-time" id="rest-banner-time">1:30</div>
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;">
    <button class="btn-xs btn-outline" onclick="setRestTimer(60)">60s</button>
    <button class="btn-xs btn-outline" onclick="setRestTimer(90)">90s</button>
    <button class="btn-xs btn-outline" onclick="setRestTimer(120)">2m</button>
    <button class="btn-xs" style="background:var(--red);color:white;border:none;border-radius:8px;cursor:pointer;font-family:inherit;font-weight:700;padding:5px 10px;font-size:12px;" onclick="stopTimer()">✕ Stop</button>
  </div>
</div>

<!-- SUCCESS OVERLAY -->'''

new_html = '''<!-- REST TIMER (inline between exercise cards, moved by JS) -->
<div class="rest-banner" id="rest-banner">
  <div>
    <div class="rest-banner-label">⏱️ Rest Timer</div>
    <div class="rest-banner-time" id="rest-banner-time">1:30</div>
  </div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
    <button class="btn-xs btn-outline" onclick="setRestTimer(60)">60s</button>
    <button class="btn-xs btn-outline" onclick="setRestTimer(90)">90s</button>
    <button class="btn-xs btn-outline" onclick="setRestTimer(120)">2m</button>
    <button class="btn-xs" style="background:var(--red);color:white;border:none;border-radius:8px;cursor:pointer;font-family:inherit;font-weight:700;padding:5px 10px;font-size:12px;" onclick="stopTimer()">✕ Stop</button>
  </div>
</div>

<!-- SUCCESS OVERLAY -->'''

if old_html in content:
    content = content.replace(old_html, new_html, 1)
    print("✅ HTML banner kept (now inline)")
else:
    print("❌ HTML banner not found")

# 3) Update startRestTimer to move the banner after the given exercise card
old_timer = '''// REST TIMER (floating banner)
function startRestTimer(s) {
  stopTimer(); timerSeconds=s;
  const banner = document.getElementById('rest-banner');
  banner.classList.add('active');
  updateTimerDisplay();
  timerInterval=setInterval(()=>{
    timerSeconds--;
    updateTimerDisplay();
    if(timerSeconds<=0){stopTimer();document.getElementById('rest-banner-time').textContent='Go! 💪';setTimeout(stopTimer,1200);}
  },1000);
}
function setRestTimer(s){startRestTimer(s);}
function stopTimer(){
  if(timerInterval){clearInterval(timerInterval);timerInterval=null;}
  document.getElementById('rest-banner').classList.remove('active');
}
function updateTimerDisplay(){
  const m=Math.floor(timerSeconds/60),s=timerSeconds%60;
  const t=`${m}:${String(s).padStart(2,'0')}`;
  document.getElementById('rest-banner-time').textContent=t;
  if(document.getElementById('timer-display'))document.getElementById('timer-display').textContent=t;
}'''

new_timer = '''// REST TIMER (inline between exercise cards)
function startRestTimer(s, afterExId) {
  stopTimer(); timerSeconds=s;
  const banner = document.getElementById('rest-banner');
  // Move banner after the exercise card that triggered it
  if (afterExId) {
    const card = document.getElementById('excard-' + afterExId);
    if (card && card.parentNode) {
      card.parentNode.insertBefore(banner, card.nextSibling);
    }
  }
  banner.classList.add('active');
  updateTimerDisplay();
  timerInterval=setInterval(()=>{
    timerSeconds--;
    updateTimerDisplay();
    if(timerSeconds<=0){
      document.getElementById('rest-banner-time').textContent='Go! 💪';
      setTimeout(stopTimer,1200);
    }
  },1000);
}
function setRestTimer(s){startRestTimer(s, null);}
function stopTimer(){
  if(timerInterval){clearInterval(timerInterval);timerInterval=null;}
  document.getElementById('rest-banner').classList.remove('active');
}
function updateTimerDisplay(){
  const m=Math.floor(timerSeconds/60),s=timerSeconds%60;
  const t=`${m}:${String(s).padStart(2,'0')}`;
  document.getElementById('rest-banner-time').textContent=t;
  if(document.getElementById('timer-display'))document.getElementById('timer-display').textContent=t;
}'''

if old_timer in content:
    content = content.replace(old_timer, new_timer, 1)
    print("✅ startRestTimer patched")
else:
    print("❌ startRestTimer not found")

# 4) Pass exId into startRestTimer call in completeSet
old_complete = '''  if (exSets[exId][i].completed) {
    startWorkoutTimer(); // start/keep workout elapsed timer
    if (exId !== 'plank') startRestTimer(90);
    spawnCoins(document.getElementById(`setbtn-${exId}-${i}`));
  }'''

new_complete = '''  if (exSets[exId][i].completed) {
    startWorkoutTimer(); // start/keep workout elapsed timer
    if (exId !== 'plank') startRestTimer(90, exId);
    spawnCoins(document.getElementById(`setbtn-${exId}-${i}`));
  }'''

if old_complete in content:
    content = content.replace(old_complete, new_complete, 1)
    print("✅ completeSet call patched")
else:
    print("❌ completeSet call not found")

with open('index.html', 'w') as f:
    f.write(content)

print("\n✅ Patch 2 complete!")
