with open('index.html', 'r') as f:
    content = f.read()

# 1) Add walks10 to MILESTONES array
old_milestones = '''const MILESTONES = [
  {key:'firstWorkout',icon:'🔥',name:'First Step',desc:'Log your first workout'},
  {key:'streak7',icon:'📅',name:'7-Day Streak',desc:'7 consecutive days — earn a spin!'},'''

new_milestones = '''const MILESTONES = [
  {key:'firstWorkout',icon:'🔥',name:'First Step',desc:'Log your first workout'},
  {key:'walks10',icon:'🐕',name:'10 Dog Walks',desc:'Walk the dog 10 times — earn a spin!'},
  {key:'streak7',icon:'📅',name:'7-Day Streak',desc:'7 consecutive days — earn a spin!'},'''

if old_milestones in content:
    content = content.replace(old_milestones, new_milestones, 1)
    print("✅ walks10 milestone added")
else:
    print("❌ MILESTONES not found")

# 2) Add walks10 spin prize reason label
old_reasons = '''const reasons = {streak7:'🔥 7-day streak reward!',streak14:'🔥 14-day streak reward!',streak30:'🔥 30-day streak reward!',workouts30:'💪 30 workouts milestone!',workouts100:'💪 100 workouts milestone!',cardio500:'🏃 500 cardio minutes!',cardio1000:'🏆 1000 cardio minutes!'};'''

new_reasons = '''const reasons = {streak7:'🔥 7-day streak reward!',streak14:'🔥 14-day streak reward!',streak30:'🔥 30-day streak reward!',workouts30:'💪 30 workouts milestone!',workouts100:'💪 100 workouts milestone!',cardio500:'🏃 500 cardio minutes!',cardio1000:'🏆 1000 cardio minutes!',walks10:'🐕 10 dog walks milestone!'};'''

if old_reasons in content:
    content = content.replace(old_reasons, new_reasons, 1)
    print("✅ walks10 spin reason added")
else:
    print("❌ reasons not found")

# 3) Update the walk card UI to show walk count
old_walk_card = '''    <div class="card" style="text-align:center;padding:24px;">
      <div style="font-size:48px;margin-bottom:12px;">🐕</div>
      <div style="font-size:18px;font-weight:700;margin-bottom:8px;">Dog Walk Day</div>
      <div style="font-size:14px;color:var(--muted);margin-bottom:20px;">Did you get those steps in?</div>
      <div style="display:flex;gap:12px;">
        <button class="btn btn-green" onclick="logActiveRest(true)">✅ Yes, walked!</button>
        <button class="btn btn-outline" onclick="logActiveRest(false)">❌ Not today</button>
      </div>
    </div>'''

new_walk_card = '''    <div class="card" style="text-align:center;padding:24px;">
      <div style="font-size:48px;margin-bottom:12px;">🐕</div>
      <div style="font-size:18px;font-weight:700;margin-bottom:8px;">Dog Walk Day</div>
      <div style="font-size:14px;color:var(--muted);margin-bottom:8px;">Did you get those steps in?</div>
      <div style="font-size:13px;color:var(--green);font-weight:700;margin-bottom:16px;" id="walk-count-display"></div>
      <div style="display:flex;gap:12px;">
        <button class="btn btn-green" onclick="logActiveRest(true)">✅ Yes, walked!</button>
        <button class="btn btn-outline" onclick="logActiveRest(false)">❌ Not today</button>
      </div>
    </div>'''

if old_walk_card in content:
    content = content.replace(old_walk_card, new_walk_card, 1)
    print("✅ Walk card UI updated")
else:
    print("❌ Walk card not found")

# 4) Update renderLog to populate walk count display
old_renderlog = '''function renderLog() {
  document.getElementById('log-date').value = getToday();
  buildExerciseCards();
  updateLogDateLabel();
}'''

new_renderlog = '''function renderLog() {
  document.getElementById('log-date').value = getToday();
  buildExerciseCards();
  updateLogDateLabel();
  // Show walk count
  const walkCount = Object.values(appData.logs||{}).filter(l=>l.type==='active'&&l.walked).length;
  const walkEl = document.getElementById('walk-count-display');
  if (walkEl) {
    const remaining = Math.max(0, 10 - walkCount);
    if (walkCount >= 10) {
      walkEl.textContent = `🎉 ${walkCount} walks total — milestone reached!`;
    } else {
      walkEl.textContent = `${walkCount} walks total · ${remaining} more for a spin reward 🎰`;
    }
  }
}'''

if old_renderlog in content:
    content = content.replace(old_renderlog, new_renderlog, 1)
    print("✅ renderLog walk count added")
else:
    print("❌ renderLog not found")

with open('index.html', 'w') as f:
    f.write(content)

print("\n✅ Patch 4 (frontend) complete!")
