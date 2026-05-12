with open('index.html', 'r') as f:
    content = f.read()

# 1) Pass client's local date to /api/data so server uses correct "today"
old_fetch_data = "const res = await fetch('/fitness/api/data');"
new_fetch_data = "const res = await fetch('/fitness/api/data?today=' + getToday());"

if old_fetch_data in content:
    content = content.replace(old_fetch_data, new_fetch_data, 1)
    print("✅ Pass local date to /api/data")
else:
    print("❌ fetch api/data not found")

with open('index.html', 'w') as f:
    f.write(content)

print("✅ Frontend patch done")

# 2) Fix server to use client-supplied date for streak calculation
with open('server.js', 'r') as f:
    content = f.read()

# Fix /api/data to use client date
old_get_data = """app.get('/api/data', (req,res) => {
  const data = loadData();
  const stats = computeStats(data);
  saveData(data);
  res.json({...data, stats});
});"""

new_get_data = """app.get('/api/data', (req,res) => {
  const data = loadData();
  const clientToday = req.query.today || null;
  const stats = computeStats(data, clientToday);
  saveData(data);
  res.json({...data, stats});
});"""

if old_get_data in content:
    content = content.replace(old_get_data, new_get_data, 1)
    print("✅ /api/data uses client date")
else:
    print("❌ /api/data handler not found")

# Fix /api/log to use client date for stats too
old_log = """  const stats = computeStats(data);
  saveData(data);
  res.json({success:true, stats, prs:data.prs});"""

new_log = """  const clientToday = req.body.today || date;
  const stats = computeStats(data, clientToday);
  saveData(data);
  res.json({success:true, stats, prs:data.prs});"""

if old_log in content:
    content = content.replace(old_log, new_log, 1)
    print("✅ /api/log uses client date for stats")
else:
    print("❌ /api/log stats block not found")

# Fix computeStats signature to accept clientToday
old_compute = "function computeStats(data) {"
new_compute = "function computeStats(data, clientToday) {"

if old_compute in content:
    content = content.replace(old_compute, new_compute, 1)
    print("✅ computeStats accepts clientToday")
else:
    print("❌ computeStats signature not found")

# Fix the today line inside computeStats to use clientToday if provided
old_today = "  const today = new Date().toISOString().split('T')[0];"
new_today = """  const today = clientToday || new Date().toISOString().split('T')[0];"""

if old_today in content:
    content = content.replace(old_today, new_today, 1)
    print("✅ today uses clientToday param")
else:
    print("❌ today line not found")

with open('server.js', 'w') as f:
    f.write(content)

print("\n✅ Patch 9 complete!")
