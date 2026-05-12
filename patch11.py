with open('index.html', 'r') as f:
    content = f.read()

# 1) Change walk button to post to /api/walk (separate endpoint, never overwrites workout)
old_active_fn = """async function logActiveRest(walked){
  // Always use today's local date for walk logs
  const date = getToday();
  await saveLog(date, {type:'active', walked});
}"""

new_active_fn = """async function logActiveRest(walked){
  if (!walked) { showToast('Walk skipped.'); return; }
  try {
    const res = await fetch('/fitness/api/walk', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({date:getToday(), today:getToday()})
    });
    const result = await res.json();
    if (result.success) {
      await loadData();
      renderHome(); renderProgress(); renderLog();
      // Show success
      document.getElementById('overlay-icon').textContent = '🐕';
      document.getElementById('overlay-title').textContent = 'Walk Logged!';
      document.getElementById('overlay-sub').textContent = `${result.totalWalks} walk${result.totalWalks===1?'':'s'} total. Keep it up!`;
      document.getElementById('overlay-streak').style.display='none';
      document.getElementById('success-overlay').classList.add('show');
      launchCelebration();
    }
  } catch(e) {
    showToast('⚠️ Save failed — try again');
  }
}"""

if old_active_fn in content:
    content = content.replace(old_active_fn, new_active_fn, 1)
    print("✅ Walk button now uses /api/walk")
else:
    print("❌ logActiveRest not found")

# 2) Update walk count display to read from appData.totalWalks
old_walk_render = """  const walkCount = Object.values(appData.logs||{}).filter(l=>l.type==='active'&&l.walked).length;
  const walkEl = document.getElementById('walk-count-display');
  if (walkEl) {
    const remaining = Math.max(0, 10 - walkCount);
    if (walkCount >= 10) {
      walkEl.textContent = `🎉 ${walkCount} walks total — milestone reached!`;
    } else {
      walkEl.textContent = `${walkCount} walks total · ${remaining} more for a spin reward 🎰`;
    }
  }"""

new_walk_render = """  const walkCount = appData.totalWalks || 0;
  const walkEl = document.getElementById('walk-count-display');
  if (walkEl) {
    const remaining = Math.max(0, 10 - walkCount);
    if (walkCount >= 10) {
      walkEl.textContent = `🎉 ${walkCount} walks total — milestone reached!`;
    } else {
      walkEl.textContent = `${walkCount} walks total · ${remaining} more for a spin reward 🎰`;
    }
  }"""

if old_walk_render in content:
    content = content.replace(old_walk_render, new_walk_render, 1)
    print("✅ Walk display reads from appData.totalWalks")
else:
    print("❌ walk render not found")

# 3) Update home stats walk counter
old_walk_home = """  const walkCount = Object.values(appData.logs||{}).filter(l=>l.type==='active'&&l.walked).length;
  document.getElementById('stat-walks').textContent = walkCount;
  const walksLeft = Math.max(0, 10 - walkCount);
  document.getElementById('stat-walks-to-spin').textContent = walksLeft > 0 ? `${walksLeft} more for 🎰` : '🎉 Spin earned!';"""

new_walk_home = """  const walkCount = appData.totalWalks || 0;
  document.getElementById('stat-walks').textContent = walkCount;
  const walksLeft = Math.max(0, 10 - walkCount);
  document.getElementById('stat-walks-to-spin').textContent = walksLeft > 0 ? `${walksLeft} more for 🎰` : '🎉 Spin earned!';"""

if old_walk_home in content:
    content = content.replace(old_walk_home, new_walk_home, 1)
    print("✅ Home walk stat reads from appData.totalWalks")
else:
    print("❌ home walk stat not found")

with open('index.html', 'w') as f:
    f.write(content)

# Now update server.js
with open('server.js', 'r') as f:
    sv = f.read()

# Add /api/walk endpoint before app.listen
old_listen = "app.listen(PORT, () => console.log(`🎰 Best Bove 60 running on port ${PORT}`));"

new_listen = """app.post('/api/walk', (req,res) => {
  const data = loadData();
  const {date, today} = req.body;
  if (!data.walks) data.walks = [];
  data.walks.push({date: date || new Date().toISOString().split('T')[0], loggedAt: new Date().toISOString()});
  const totalWalks = data.walks.length;
  // Check 10-walk milestone
  if (!data.milestones) data.milestones = {};
  if (!data.spinsAvailable) data.spinsAvailable = {};
  if (totalWalks >= 10 && !data.milestones.walks10) {
    data.milestones.walks10 = true;
    data.spinsAvailable.walks10 = true;
  }
  saveData(data);
  res.json({success:true, totalWalks});
});

app.listen(PORT, () => console.log(`🎰 Best Bove 60 running on port ${PORT}`));"""

if old_listen in content:
    sv = sv.replace(old_listen, new_listen, 1)
    print("✅ /api/walk endpoint added to server")
else:
    sv = sv.replace("app.listen(PORT, () => console.log(`🎰 Best Bove 60 running on port ${PORT}`));", new_listen, 1)
    print("✅ /api/walk endpoint added to server (fallback)")

# Add totalWalks to the /api/data response
old_data_res = "  res.json({...data, stats});"
new_data_res = "  const totalWalks = (data.walks||[]).length;\n  res.json({...data, stats, totalWalks});"

if old_data_res in sv:
    sv = sv.replace(old_data_res, new_data_res, 1)
    print("✅ totalWalks added to /api/data response")
else:
    print("❌ /api/data response not found")

with open('server.js', 'w') as f:
    f.write(sv)

print("\n✅ Patch 11 complete!")
