with open('index.html', 'r') as f:
    content = f.read()

# 1) Fix all API fetch calls - remove leading slash so they use relative paths
#    /fitness/ + api/log = /fitness/api/log which nginx strips to /api/log on express
replacements = [
    ("fetch('/api/data')", "fetch('api/data')"),
    ("fetch('/api/log',", "fetch('api/log',"),
    ("fetch('/api/log')", "fetch('api/log')"),
    ("fetch('/api/spin-reward',", "fetch('api/spin-reward',"),
    ("fetch('/api/cashin-cheat',", "fetch('api/cashin-cheat',"),
    ("fetch('/api/bodyweight',", "fetch('api/bodyweight',"),
    ("fetch('/api/stats'", "fetch('api/stats'"),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)
        print(f"✅ Fixed: {old} → {new}")
    else:
        print(f"⚠️  Not found: {old}")

# 2) Change rest timer bar color from blue to amber/gold
old_rest_css = '''.rest-banner { background:rgba(14,165,233,0.08); border:1px solid rgba(14,165,233,0.3); border-radius:12px; padding:10px 14px; display:none; align-items:center; justify-content:space-between; margin-bottom:12px; }
.rest-banner.active { display:flex; }
.rest-banner-time { font-size:26px; font-weight:900; color:var(--blue); font-family:'Righteous',sans-serif; line-height:1; }
.rest-banner-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:2px; }'''

new_rest_css = '''.rest-banner { background:rgba(245,158,11,0.08); border:1px solid rgba(245,158,11,0.4); border-radius:12px; padding:10px 14px; display:none; align-items:center; justify-content:space-between; margin-bottom:12px; }
.rest-banner.active { display:flex; }
.rest-banner-time { font-size:26px; font-weight:900; color:var(--amber); font-family:'Righteous',sans-serif; line-height:1; }
.rest-banner-label { font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:1px; color:var(--muted); margin-bottom:2px; }'''

if old_rest_css in content:
    content = content.replace(old_rest_css, new_rest_css, 1)
    print("✅ Rest timer color changed to amber")
else:
    print("❌ Rest timer CSS not found")

with open('index.html', 'w') as f:
    f.write(content)

print("\n✅ Patch 3 complete!")
