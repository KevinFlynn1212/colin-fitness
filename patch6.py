with open('index.html', 'r') as f:
    content = f.read()

# 1) Open ALL exercise cards by default (not just the first one)
old_default_open = '''    if (idx===0) toggleExCard(ex.id);'''
new_default_open = '''    toggleExCard(ex.id); // open all by default'''

if old_default_open in content:
    content = content.replace(old_default_open, new_default_open, 1)
    print("✅ All exercise cards open by default")
else:
    print("❌ default open line not found")

# 2) Call renderLog() after a successful save so walk counter updates
old_save_success = '''      stopTimer();
      stopWorkoutTimer();
      showSuccess(log,result.stats,prevStreak);
      renderHome();renderCalendar();renderProgress();
    }
  }catch(e){
    // Retry once silently before showing error
    try {
      await new Promise(r=>setTimeout(r,1000));
      const res2=await fetch('/fitness/api/log',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date,log})});
      const result2=await res2.json();
      if(result2.success){
        const prevStreak=(appData.stats||{}).currentStreak||0;
        await loadData();
        stopTimer();
        stopWorkoutTimer();
        showSuccess(log,result2.stats,prevStreak);
        renderHome();renderCalendar();renderProgress();
      }'''

new_save_success = '''      stopTimer();
      stopWorkoutTimer();
      showSuccess(log,result.stats,prevStreak);
      renderHome();renderCalendar();renderProgress();renderLog();
    }
  }catch(e){
    // Retry once silently before showing error
    try {
      await new Promise(r=>setTimeout(r,1000));
      const res2=await fetch('/fitness/api/log',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({date,log})});
      const result2=await res2.json();
      if(result2.success){
        const prevStreak=(appData.stats||{}).currentStreak||0;
        await loadData();
        stopTimer();
        stopWorkoutTimer();
        showSuccess(log,result2.stats,prevStreak);
        renderHome();renderCalendar();renderProgress();renderLog();
      }'''

if old_save_success in content:
    content = content.replace(old_save_success, new_save_success, 1)
    print("✅ renderLog() called after save — walk count will refresh")
else:
    print("❌ save success block not found")

with open('index.html', 'w') as f:
    f.write(content)

print("\n✅ Patch 6 complete!")
