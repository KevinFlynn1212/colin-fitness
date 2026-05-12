with open('index.html', 'r') as f:
    content = f.read()

# 1) Fix calendar - don't mark days before startDate as missed
old_cal_day = """    const dow=new Date(ds).getDay(),isFuture=ds>today,log=appData.logs[ds],isToday=ds===today;
    let cls=isFuture?'future':dow===0?'rest':log?'done':'missed';
    if(dow===6&&!log&&!isFuture)cls='rest';"""

new_cal_day = """    const dow=new Date(ds).getDay(),isFuture=ds>today,log=appData.logs[ds],isToday=ds===today;
    const startDate=appData.startDate||'2026-05-08';
    const beforeStart=ds<startDate;
    let cls=isFuture||beforeStart?'future':dow===0?'rest':log?'done':'missed';
    if(dow===6&&!log&&!isFuture&&!beforeStart)cls='rest';"""

if old_cal_day in content:
    content = content.replace(old_cal_day, new_cal_day, 1)
    print("✅ Calendar: days before startDate no longer shown as missed")
else:
    print("❌ Calendar day block not found")

# 2) Fix walk button - add console log and make sure setLogType('active') sets the date input
# The issue: when user clicks Walk tab directly from nav, renderLog may not have run
# so log-date value might be stale or empty. Let's make logActiveRest extra safe.
old_active = """async function logActiveRest(walked){
  const dateEl = document.getElementById('log-date');
  const date = dateEl && dateEl.value ? dateEl.value : getToday();
  await saveLog(date, {type:'active', walked});
}"""

new_active = """async function logActiveRest(walked){
  // Always use today's local date for walk logs
  const date = getToday();
  await saveLog(date, {type:'active', walked});
}"""

if old_active in content:
    content = content.replace(old_active, new_active, 1)
    print("✅ logActiveRest always uses today's local date")
else:
    print("❌ logActiveRest not found")

# 3) Fix logRest same way
old_rest = """async function logRest(){
  const dateEl = document.getElementById('log-date');
  const date = dateEl && dateEl.value ? dateEl.value : getToday();
  await saveLog(date, {type:'rest'});
}"""

new_rest = """async function logRest(){
  const date = getToday();
  await saveLog(date, {type:'rest'});
}"""

if old_rest in content:
    content = content.replace(old_rest, new_rest, 1)
    print("✅ logRest always uses today's local date")
else:
    print("❌ logRest not found")

with open('index.html', 'w') as f:
    f.write(content)

# 4) Fix server.js - missed days should only count from startDate
with open('server.js', 'r') as f:
    sv = f.read()

old_week = """  const startOfWeek = new Date(now);"""
# also fix the today variable used in streak - make sure it uses clientToday properly
# The main fix: in monthMissed, we already fixed to use startDate. Let's verify.
print("Server startDate fix already applied in patch7" if "data.startDate > monthStart" in sv else "❌ startDate fix missing from server")

print("\n✅ Patch 10 complete!")
