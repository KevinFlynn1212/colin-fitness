with open('server.js', 'r') as f:
    content = f.read()

# Fix monthMissed to start from startDate not beginning of month
old_month = '''  const monthStart = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-01`;
  let monthWorkouts=0, monthMissed=0;
  let d2=new Date(monthStart);'''

new_month = '''  const monthStart = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-01`;
  let monthWorkouts=0, monthMissed=0;
  // Start from the later of month start or app start date so we don't count days before app began
  let d2=new Date(data.startDate > monthStart ? data.startDate : monthStart);'''

if old_month in content:
    content = content.replace(old_month, new_month, 1)
    print("✅ monthMissed now starts from startDate")
else:
    print("❌ monthMissed block not found")

# Also exclude Saturday (dow=6) from missed count since it's an optional walk day
old_miss = '''    if (dow!==0) {
      if (log && ['cardio','strength','active','cheat'].includes(log.type)) monthWorkouts++;
      else if (ds<today) monthMissed++;'''

new_miss = '''    if (dow!==0 && dow!==6) { // exclude Sunday (rest) and Saturday (optional walk)
      if (log && ['cardio','strength','active','cheat'].includes(log.type)) monthWorkouts++;
      else if (ds<today) monthMissed++;'''

if old_miss in content:
    content = content.replace(old_miss, new_miss, 1)
    print("✅ Saturday excluded from missed count")
else:
    print("❌ missed count block not found")

with open('server.js', 'w') as f:
    f.write(content)

# Now fix getToday() in index.html to use local date not UTC
with open('index.html', 'r') as f:
    html = f.read()

old_today = "function getToday(){return new Date().toISOString().split('T')[0];}"
new_today = """function getToday(){
  const d=new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}"""

if old_today in html:
    html = html.replace(old_today, new_today, 1)
    print("✅ getToday() now uses local date")
else:
    print("❌ getToday not found")

with open('index.html', 'w') as f:
    f.write(html)

print("\n✅ Patch 7 complete!")
