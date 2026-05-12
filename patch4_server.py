with open('server.js', 'r') as f:
    content = f.read()

# Add walks10 milestone check in computeStats
old_milestone_check = '''  if (totalCardioMinutes>=500 && !m.cardio500min) { m.cardio500min=true; if(!spins.cardio500)spins.cardio500=true; }'''

new_milestone_check = '''  if (totalCardioMinutes>=500 && !m.cardio500min) { m.cardio500min=true; if(!spins.cardio500)spins.cardio500=true; }

  // Count dog walks
  const totalWalks = logDates.filter(d => logs[d] && logs[d].type==='active' && logs[d].walked).length;
  if (totalWalks>=10 && !m.walks10) { m.walks10=true; if(!spins.walks10)spins.walks10=true; }'''

if old_milestone_check in content:
    content = content.replace(old_milestone_check, new_milestone_check, 1)
    print("✅ Server walks10 milestone added")
else:
    print("❌ Server milestone check not found")

# Return totalWalks in stats
old_return = '''  return {
    currentStreak, longestStreak, totalCardioMinutes, totalStrengthSessions,
    totalCardioSessions, totalWorkouts, totalVolume:Math.round(totalVolume),'''

new_return = '''  return {
    currentStreak, longestStreak, totalCardioMinutes, totalStrengthSessions,
    totalCardioSessions, totalWorkouts, totalVolume:Math.round(totalVolume), totalWalks,'''

if old_return in content:
    content = content.replace(old_return, new_return, 1)
    print("✅ totalWalks added to stats return")
else:
    print("❌ stats return not found")

# Add walks10 to default milestones
old_default = '''    milestones:{firstWorkout:false,streak7:false,workouts30:false,cardio500min:false,streak30:false,workouts100:false,cardio1000min:false,sixMonths:false,oneYear:false}'''

new_default = '''    milestones:{firstWorkout:false,walks10:false,streak7:false,workouts30:false,cardio500min:false,streak30:false,workouts100:false,cardio1000min:false,sixMonths:false,oneYear:false}'''

if old_default in content:
    content = content.replace(old_default, new_default, 1)
    print("✅ walks10 added to default milestones")
else:
    print("❌ default milestones not found")

with open('server.js', 'w') as f:
    f.write(content)

print("\n✅ Patch 4 (server) complete!")
