with open('index.html', 'r') as f:
    content = f.read()

# 1) closeOverlay should go to home screen
old_close = "function closeOverlay(){document.getElementById('success-overlay').classList.remove('show');}"
new_close = """function closeOverlay(){
  document.getElementById('success-overlay').classList.remove('show');
  // Go back to home screen
  const homeBtn = document.querySelectorAll('.nav-btn')[0];
  showPage('home', homeBtn);
}"""

if old_close in content:
    content = content.replace(old_close, new_close, 1)
    print("✅ closeOverlay now goes to home")
else:
    print("❌ closeOverlay not found")

# 2) Fix logActiveRest - the date selector may not exist when walk tab is active
# Replace the simple one-liner with one that explicitly uses today's date
old_active = "async function logActiveRest(walked){await saveLog(document.getElementById('log-date').value,{type:'active',walked});}"
new_active = """async function logActiveRest(walked){
  const dateEl = document.getElementById('log-date');
  const date = dateEl && dateEl.value ? dateEl.value : getToday();
  await saveLog(date, {type:'active', walked});
}"""

if old_active in content:
    content = content.replace(old_active, new_active, 1)
    print("✅ logActiveRest date fix applied")
else:
    print("❌ logActiveRest not found")

# 3) Also fix logRest the same way
old_rest = "async function logRest(){await saveLog(document.getElementById('log-date').value,{type:'rest'});}"
new_rest = """async function logRest(){
  const dateEl = document.getElementById('log-date');
  const date = dateEl && dateEl.value ? dateEl.value : getToday();
  await saveLog(date, {type:'rest'});
}"""

if old_rest in content:
    content = content.replace(old_rest, new_rest, 1)
    print("✅ logRest date fix applied")
else:
    print("❌ logRest not found")

with open('index.html', 'w') as f:
    f.write(content)

print("\n✅ Patch 8 complete!")
