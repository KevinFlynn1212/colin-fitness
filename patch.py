import re

with open('index.html', 'r') as f:
    content = f.read()

# 1) Replace renderSetRows to add plank timer UI
old_render = '''function renderSetRows(exId) {
  const tbody=document.getElementById(`setrows-${exId}`);
  const isPlank=exId==='plank';
  tbody.innerHTML='';
  exSets[exId].forEach((set,i)=>{
    const tr=document.createElement('tr'); tr.className=`set-row${set.completed?' completed':''}`; tr.id=`setrow-${exId}-${i}`;
    tr.innerHTML=`<td><span class="set-num">${i+1}</span></td>
      <td><input class="set-input" type="number" value="${set.reps}" min="1" id="reps-${exId}-${i}" onchange="updateSet('${exId}',${i},'reps',this.value)"></td>
      ${!isPlank?`<td><input class="set-input" type="number" value="${set.weight||''}" min="0" placeholder="lbs" id="weight-${exId}-${i}" onchange="updateSet('${exId}',${i},'weight',this.value)"></td>`:''}
      <td><button class="set-done-btn${set.completed?' completed':''}" id="setbtn-${exId}-${i}" onclick="completeSet('${exId}',${i})">
        ${set.completed?'<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" style="width:14px;height:14px"><path d="M20 6L9 17l-5-5"/></svg>':''}
      </button></td>`;
    tbody.appendChild(tr);
  });
}'''

new_render = '''function renderSetRows(exId) {
  const tbody=document.getElementById(`setrows-${exId}`);
  const isPlank=exId==='plank';
  tbody.innerHTML='';
  exSets[exId].forEach((set,i)=>{
    const tr=document.createElement('tr'); tr.className=`set-row${set.completed?' completed':''}`; tr.id=`setrow-${exId}-${i}`;
    if(isPlank){
      tr.innerHTML=`<td><span class="set-num">${i+1}</span></td>
        <td><input class="set-input" type="number" value="${set.reps}" min="5" id="reps-${exId}-${i}" onchange="updateSet('${exId}',${i},'reps',this.value)"></td>
        <td style="text-align:center">
          <button class="plank-start-btn" id="plank-btn-${exId}-${i}" onclick="startPlankTimer('${exId}',${i})">&#x25B6; Start</button>
          <span class="plank-count" id="plank-count-${exId}-${i}" style="color:var(--muted)"></span>
        </td>
        <td><button class="set-done-btn${set.completed?' completed':''}" id="setbtn-${exId}-${i}" onclick="completeSet('${exId}',${i})">
          ${set.completed?'<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" style="width:14px;height:14px"><path d="M20 6L9 17l-5-5"/></svg>':''}
        </button></td>`;
    } else {
      tr.innerHTML=`<td><span class="set-num">${i+1}</span></td>
        <td><input class="set-input" type="number" value="${set.reps}" min="1" id="reps-${exId}-${i}" onchange="updateSet('${exId}',${i},'reps',this.value)"></td>
        <td><input class="set-input" type="number" value="${set.weight||''}" min="0" placeholder="lbs" id="weight-${exId}-${i}" onchange="updateSet('${exId}',${i},'weight',this.value)"></td>
        <td><button class="set-done-btn${set.completed?' completed':''}" id="setbtn-${exId}-${i}" onclick="completeSet('${exId}',${i})">
          ${set.completed?'<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3" style="width:14px;height:14px"><path d="M20 6L9 17l-5-5"/></svg>':''}
        </button></td>`;
    }
    tbody.appendChild(tr);
  });
}'''

if old_render in content:
    content = content.replace(old_render, new_render, 1)
    print("✅ renderSetRows patched")
else:
    print("❌ renderSetRows NOT found - check whitespace")

# 2) Start workout timer when first set is completed
old_complete = '''function completeSet(exId,i) {
  exSets[exId][i].completed=!exSets[exId][i].completed;
  const allDone=exSets[exId].every(s=>s.completed);
  document.getElementById(`excard-${exId}`).classList.toggle('done-ex',allDone);
  document.getElementById(`exstatus-${exId}`).textContent=allDone?'✅':'○';
  renderSetRows(exId);
  if (exSets[exId][i].completed) {
    startRestTimer(90);
    spawnCoins(document.getElementById(`setbtn-${exId}-${i}`));
  }
}'''

new_complete = '''function completeSet(exId,i) {
  exSets[exId][i].completed=!exSets[exId][i].completed;
  const allDone=exSets[exId].every(s=>s.completed);
  document.getElementById(`excard-${exId}`).classList.toggle('done-ex',allDone);
  document.getElementById(`exstatus-${exId}`).textContent=allDone?'✅':'○';
  renderSetRows(exId);
  if (exSets[exId][i].completed) {
    startWorkoutTimer(); // start/keep workout elapsed timer
    if (exId !== 'plank') startRestTimer(90);
    spawnCoins(document.getElementById(`setbtn-${exId}-${i}`));
  }
}'''

if old_complete in content:
    content = content.replace(old_complete, new_complete, 1)
    print("✅ completeSet patched")
else:
    print("❌ completeSet NOT found")

# 3) Fix "Are you connected?" error - remove the alert, show silent fail or just log the issue
old_savelog = '''async function saveLog(date,log){
  try{
    const res=await fetch('/api/log',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date,log})});
    const result=await res.json();
    if(result.success){
      const prevStreak=(appData.stats||{}).currentStreak||0;
      await loadData();
      stopTimer();
      showSuccess(log,result.stats,prevStreak);
      renderHome();renderCalendar();renderProgress();
    }
  }catch(e){alert('Error saving. Are you connected?');}
}'''

new_savelog = '''async function saveLog(date,log){
  try{
    const res=await fetch('/api/log',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date,log})});
    const result=await res.json();
    if(result.success){
      const prevStreak=(appData.stats||{}).currentStreak||0;
      await loadData();
      stopTimer();
      stopWorkoutTimer();
      showSuccess(log,result.stats,prevStreak);
      renderHome();renderCalendar();renderProgress();
    }
  }catch(e){
    // Retry once silently before showing error
    try {
      await new Promise(r=>setTimeout(r,1000));
      const res2=await fetch('/api/log',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date,log})});
      const result2=await res2.json();
      if(result2.success){
        const prevStreak=(appData.stats||{}).currentStreak||0;
        await loadData();
        stopTimer();
        stopWorkoutTimer();
        showSuccess(log,result2.stats,prevStreak);
        renderHome();renderCalendar();renderProgress();
      }
    } catch(e2){
      console.error('Save failed:', e2);
      // Show a non-blocking toast instead of alert
      showToast('⚠️ Save failed — please try again');
    }
  }
}'''

if old_savelog in content:
    content = content.replace(old_savelog, new_savelog, 1)
    print("✅ saveLog patched")
else:
    print("❌ saveLog NOT found")

# 4) Fix logActiveRest to not alert on connection error
old_active = '''async function logActiveRest(walked){await saveLog(document.getElementById('log-date').value,{type:'active',walked});}
async function logRest(){await saveLog(document.getElementById('log-date').value,{type:'rest'});}'''

# These call saveLog which is now fixed, so they're fine. Just add showToast function.

# 5) Add showToast function near the end (before init())
old_init = '''init();
</script>'''

new_init = '''function showToast(msg) {
  let toast = document.getElementById('save-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'save-toast';
    toast.style.cssText = 'position:fixed;bottom:80px;left:50%;transform:translateX(-50%);background:rgba(30,30,50,0.97);color:#f1f5f9;padding:10px 20px;border-radius:12px;font-size:14px;font-weight:600;z-index:500;border:1px solid var(--border);box-shadow:0 4px 20px rgba(0,0,0,0.5);';
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.display = 'block';
  setTimeout(() => { toast.style.display = 'none'; }, 3500);
}

init();
</script>'''

if old_init in content:
    content = content.replace(old_init, new_init, 1)
    print("✅ showToast + init patched")
else:
    print("❌ init NOT found")

# 6) Also fix buildExerciseCards to add "Secs" column header for plank
old_th = '''<thead><tr><th>Set</th><th>${ex.id===\\'plank\\'?\\'Sec\\':\\'Reps\\'}</th>${ex.id!==\\'plank\\'?\\'<th>Weight (lbs)</th>\\':\\'\\'}<th>Done</th></tr></thead>'''

# Let's find it with a broader search
import re as re2
# Find the sets-table thead line
match = re2.search(r'<thead><tr><th>Set</th><th>\$\{ex\.id===.plank.*?</thead>', content, re.DOTALL)
if match:
    old_thead = match.group(0)
    new_thead = '<thead><tr><th>Set</th><th>${ex.id===\'plank\'?\'Sec\':\'Reps\'}</th>${ex.id===\'plank\'?\'<th>Timer</th>\':\'<th>Weight (lbs)</th>\'}<th>Done</th></tr></thead>'
    content = content.replace(old_thead, new_thead, 1)
    print("✅ thead patched")
else:
    print("⚠️ thead not found (may be ok)")

with open('index.html', 'w') as f:
    f.write(content)

print("\n✅ All patches complete!")
