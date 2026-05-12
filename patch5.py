with open('index.html', 'r') as f:
    content = f.read()

# Fix all API fetch calls to use absolute /fitness/ paths
replacements = [
    ("fetch('api/data')", "fetch('/fitness/api/data')"),
    ("fetch('api/log',", "fetch('/fitness/api/log',"),
    ("fetch('api/spin-reward',", "fetch('/fitness/api/spin-reward',"),
    ("fetch('api/cashin-cheat',", "fetch('/fitness/api/cashin-cheat',"),
    ("fetch('api/bodyweight',", "fetch('/fitness/api/bodyweight',"),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ {old} → {new}")
    else:
        print(f"❌ Not found: {old}")

# Make walk counter visible on the home page stats row - add after the existing 4 stats
old_stats = '''  <div class="stats-row">
    <div class="stat-card gold"><div class="stat-value" id="stat-streak">0</div><div class="stat-label">🔥 Day Streak</div></div>
    <div class="stat-card amber"><div class="stat-value" id="stat-days-to-60">—</div><div class="stat-label">📅 Days to 60</div></div>
    <div class="stat-card green"><div class="stat-value" id="stat-month-done">0</div><div class="stat-label">✅ This Month</div></div>
    <div class="stat-card red"><div class="stat-value" id="stat-missed">0</div><div class="stat-label">❌ Missed</div></div>
  </div>'''

new_stats = '''  <div class="stats-row">
    <div class="stat-card gold"><div class="stat-value" id="stat-streak">0</div><div class="stat-label">🔥 Day Streak</div></div>
    <div class="stat-card amber"><div class="stat-value" id="stat-days-to-60">—</div><div class="stat-label">📅 Days to 60</div></div>
    <div class="stat-card green"><div class="stat-value" id="stat-month-done">0</div><div class="stat-label">✅ This Month</div></div>
    <div class="stat-card red"><div class="stat-value" id="stat-missed">0</div><div class="stat-label">❌ Missed</div></div>
  </div>
  <div class="stats-row" style="grid-template-columns:1fr 1fr;">
    <div class="stat-card" style="border-color:var(--green);"><div class="stat-value" style="color:var(--green);" id="stat-walks">0</div><div class="stat-label">🐕 Dog Walks</div></div>
    <div class="stat-card" style="border-color:var(--muted);"><div class="stat-value" style="color:var(--muted);font-size:18px;" id="stat-walks-to-spin">10 for spin</div><div class="stat-label">🎰 Next Reward</div></div>
  </div>'''

if old_stats in content:
    content = content.replace(old_stats, new_stats, 1)
    print("✅ Walk counter added to home stats")
else:
    print("❌ Stats row not found")

# Update renderHome to populate walk stats
old_render_home_end = '''  document.getElementById('stat-streak').textContent = stats.currentStreak;
  document.getElementById('stat-days-to-60').textContent = stats.daysUntilGoal?.toLocaleString()||'—';
  document.getElementById('stat-month-done').textContent = stats.monthWorkouts;
  document.getElementById('stat-missed').textContent = stats.monthMissed;'''

new_render_home_end = '''  document.getElementById('stat-streak').textContent = stats.currentStreak;
  document.getElementById('stat-days-to-60').textContent = stats.daysUntilGoal?.toLocaleString()||'—';
  document.getElementById('stat-month-done').textContent = stats.monthWorkouts;
  document.getElementById('stat-missed').textContent = stats.monthMissed;
  const walkCount = Object.values(appData.logs||{}).filter(l=>l.type==='active'&&l.walked).length;
  document.getElementById('stat-walks').textContent = walkCount;
  const walksLeft = Math.max(0, 10 - walkCount);
  document.getElementById('stat-walks-to-spin').textContent = walksLeft > 0 ? `${walksLeft} more for 🎰` : '🎉 Spin earned!';'''

if old_render_home_end in content:
    content = content.replace(old_render_home_end, new_render_home_end, 1)
    print("✅ renderHome walk stats updated")
else:
    print("❌ renderHome stat block not found")

with open('index.html', 'w') as f:
    f.write(content)

print("\n✅ Patch 5 complete!")
