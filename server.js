const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;
const DATA_FILE = path.join(__dirname, 'fitness-data.json');

app.use(express.json());
app.use(express.static(__dirname));

function loadData() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch (e) { return getDefaultData(); }
}

function getDefaultData() {
  return {
    startDate: '2026-05-08', goal: 'Best Shape by 60', goalDate: '2031-10-18',
    workoutGoal: 500, logs: {}, prs: {}, bodyWeight: {},
    milestones: {
      firstWorkout: false, streak7: false, workouts30: false, cardio500min: false,
      streak30: false, workouts100: false, cardio1000min: false, sixMonths: false, oneYear: false
    }
  };
}

function saveData(data) { fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2)); }

function computeStats(data) {
  const logs = data.logs;
  const logDates = Object.keys(logs).sort();
  let currentStreak = 0, longestStreak = 0, totalCardioMinutes = 0;
  let totalStrengthSessions = 0, cardioZone2Sessions = 0, totalCardioSessions = 0;
  let totalVolume = 0;

  for (const date of logDates) {
    const log = logs[date];
    if (log.type === 'cardio') {
      totalCardioMinutes += log.minutes || 0;
      totalCardioSessions++;
      if (log.zone === 'zone2') cardioZone2Sessions++;
    } else if (log.type === 'strength') {
      totalStrengthSessions++;
      if (log.exercises) {
        for (const exId of Object.keys(log.exercises)) {
          const ex = log.exercises[exId];
          if (ex.sets) {
            for (const set of ex.sets) {
              if (set.weight && set.unit !== 'sec') totalVolume += set.weight * (set.reps || 1);
            }
          }
        }
      }
    }
  }

  const today = new Date().toISOString().split('T')[0];
  let checkDate = new Date(today);
  while (true) {
    const ds = checkDate.toISOString().split('T')[0];
    const log = logs[ds];
    const dow = checkDate.getDay();
    if (log && ['cardio','strength','active'].includes(log.type)) currentStreak++;
    else if (dow === 0) { /* rest day */ }
    else break;
    checkDate.setDate(checkDate.getDate() - 1);
    if (currentStreak > 365) break;
  }

  let tempStreak = 0, allDates = [];
  let d = new Date(data.startDate);
  const todayDate = new Date(today);
  while (d <= todayDate) { allDates.push(d.toISOString().split('T')[0]); d.setDate(d.getDate() + 1); }
  for (const ds of allDates) {
    const log = logs[ds];
    const dow = new Date(ds).getDay();
    if (log && ['cardio','strength','active'].includes(log.type)) { tempStreak++; if (tempStreak > longestStreak) longestStreak = tempStreak; }
    else if (dow === 0) { /* rest */ }
    else tempStreak = 0;
  }

  const now = new Date();
  const monthStart = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-01`;
  let monthWorkouts = 0, monthMissed = 0;
  let d2 = new Date(monthStart);
  while (d2 <= todayDate) {
    const ds = d2.toISOString().split('T')[0];
    const dow = d2.getDay();
    const log = logs[ds];
    if (dow !== 0) {
      if (log && ['cardio','strength','active'].includes(log.type)) monthWorkouts++;
      else if (ds < today) monthMissed++;
    }
    d2.setDate(d2.getDate() + 1);
  }

  const startOfWeek = new Date(now);
  startOfWeek.setDate(now.getDate() - now.getDay() + 1);
  let weekDone = 0;
  for (let i = 0; i < 5; i++) {
    const wd = new Date(startOfWeek); wd.setDate(startOfWeek.getDate() + i);
    const wds = wd.toISOString().split('T')[0];
    if (logs[wds] && ['cardio','strength'].includes(logs[wds].type)) weekDone++;
  }

  const totalWorkouts = totalCardioSessions + totalStrengthSessions;
  const workoutGoal = data.workoutGoal || 500;

  const m = data.milestones;
  if (totalWorkouts >= 1) m.firstWorkout = true;
  if (currentStreak >= 7 || longestStreak >= 7) m.streak7 = true;
  if (totalWorkouts >= 30) m.workouts30 = true;
  if (totalCardioMinutes >= 500) m.cardio500min = true;
  if (currentStreak >= 30 || longestStreak >= 30) m.streak30 = true;
  if (totalWorkouts >= 100) m.workouts100 = true;
  if (totalCardioMinutes >= 1000) m.cardio1000min = true;
  const daysSinceStart = Math.floor((new Date(today) - new Date(data.startDate)) / 86400000);
  if (daysSinceStart >= 180) m.sixMonths = true;
  if (daysSinceStart >= 365) m.oneYear = true;

  return {
    currentStreak, longestStreak, totalCardioMinutes, totalStrengthSessions,
    totalCardioSessions, totalWorkouts, totalVolume: Math.round(totalVolume),
    zone2Compliance: totalCardioSessions > 0 ? Math.round((cardioZone2Sessions / totalCardioSessions) * 100) : 0,
    monthWorkouts, monthMissed, weekDone, weekTotal: 5,
    workoutsToGoal: Math.max(0, workoutGoal - totalWorkouts),
    workoutGoalProgress: Math.min(100, Math.round((totalWorkouts / workoutGoal) * 100)),
    daysUntilGoal: Math.ceil((new Date(data.goalDate) - new Date(today)) / 86400000),
    milestones: m
  };
}

app.get('/api/data', (req, res) => {
  const data = loadData();
  const stats = computeStats(data);
  data.milestones = stats.milestones;
  saveData(data);
  res.json({ ...data, stats });
});

app.get('/api/stats', (req, res) => { const data = loadData(); res.json(computeStats(data)); });

app.post('/api/log', (req, res) => {
  const data = loadData();
  const { date, log } = req.body;
  if (!date || !log) return res.status(400).json({ error: 'date and log required' });
  data.logs[date] = { ...log, loggedAt: new Date().toISOString() };
  if (!data.prs) data.prs = {};
  if (log.type === 'strength' && log.exercises) {
    for (const exId of Object.keys(log.exercises)) {
      const ex = log.exercises[exId];
      if (ex.sets) {
        for (const set of ex.sets) {
          if (set.weight && set.unit !== 'sec') {
            if (!data.prs[exId] || set.weight > data.prs[exId].weight) {
              data.prs[exId] = { weight: set.weight, reps: set.reps, date };
            }
          }
        }
      }
    }
  }
  const stats = computeStats(data);
  data.milestones = stats.milestones;
  saveData(data);
  res.json({ success: true, stats, prs: data.prs });
});

app.get('/api/log/:date', (req, res) => {
  const data = loadData();
  const log = data.logs[req.params.date];
  if (!log) return res.status(404).json({ error: 'No log' });
  res.json(log);
});

app.delete('/api/log/:date', (req, res) => {
  const data = loadData();
  delete data.logs[req.params.date];
  saveData(data);
  res.json({ success: true });
});

app.post('/api/bodyweight', (req, res) => {
  const data = loadData();
  const { date, weight } = req.body;
  if (!date || !weight) return res.status(400).json({ error: 'date and weight required' });
  if (!data.bodyWeight) data.bodyWeight = {};
  data.bodyWeight[date] = parseFloat(weight);
  saveData(data);
  res.json({ success: true });
});

app.get('/health', (req, res) => res.json({ status: 'ok' }));
app.get('*', (req, res) => res.sendFile(path.join(__dirname, 'index.html')));

app.listen(PORT, () => console.log(`🏋️ Best Shape by 60 running on port ${PORT}`));
