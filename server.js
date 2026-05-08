const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3001;
const DATA_FILE = path.join(__dirname, 'fitness-data.json');

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Helper: read data
function readData() {
  try {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  } catch (e) {
    return {
      startDate: '2026-05-08',
      goal: 'Best Shape by 60',
      goalDate: '2031-10-18',
      logs: {},
      milestones: {
        firstWorkout: false,
        streak7: false,
        workouts30: false,
        cardio500min: false,
        streak30: false,
        workouts100: false,
        cardio1000min: false,
        sixMonths: false,
        oneYear: false
      }
    };
  }
}

// Helper: write data
function writeData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
}

// Helper: get day of week type for a date string (YYYY-MM-DD)
function getWorkoutType(dateStr) {
  const d = new Date(dateStr + 'T12:00:00');
  const day = d.getDay(); // 0=Sun,1=Mon,...,6=Sat
  if (day === 1 || day === 3 || day === 5) return 'cardio';
  if (day === 2 || day === 4) return 'strength';
  if (day === 6) return 'active';
  return 'rest';
}

// Helper: compute streak (consecutive active days logged, rest days don't break it)
function computeStreak(logs) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  let streak = 0;
  let current = new Date(today);

  while (true) {
    const dateStr = current.toISOString().split('T')[0];
    const type = getWorkoutType(dateStr);
    const log = logs[dateStr];

    if (type === 'rest') {
      // rest days don't break streak, skip back
      current.setDate(current.getDate() - 1);
      continue;
    }

    if (log && log.completed) {
      streak++;
      current.setDate(current.getDate() - 1);
    } else {
      // If today hasn't been logged yet, don't penalize
      if (current.getTime() === today.getTime()) {
        current.setDate(current.getDate() - 1);
        continue;
      }
      break;
    }

    // Safety: don't go back more than 365 days
    const diff = (today.getTime() - current.getTime()) / (1000 * 60 * 60 * 24);
    if (diff > 365) break;
  }

  return streak;
}

// Helper: compute stats
function computeStats(data) {
  const { logs, startDate } = data;
  const today = new Date();
  const todayStr = today.toISOString().split('T')[0];

  // This month
  const year = today.getFullYear();
  const month = today.getMonth();
  const firstOfMonth = new Date(year, month, 1);
  const lastOfMonth = new Date(year, month + 1, 0);

  let monthCompleted = 0;
  let monthTarget = 0;
  let monthMissed = 0;
  let totalCardioMin = 0;
  let zone2Sessions = 0;
  let totalCardioSessions = 0;
  let totalStrengthSessions = 0;
  let longestStreak = 0;
  let currentStreakCount = 0;
  let inStreak = false;

  // Build sorted date list
  const allDates = [];
  const cursor = new Date(firstOfMonth);
  while (cursor <= lastOfMonth) {
    allDates.push(cursor.toISOString().split('T')[0]);
    cursor.setDate(cursor.getDate() + 1);
  }

  for (const dateStr of allDates) {
    if (dateStr > todayStr) break;
    const type = getWorkoutType(dateStr);
    if (type === 'rest') continue;
    monthTarget++;
    const log = logs[dateStr];
    if (log && log.completed) {
      monthCompleted++;
    } else {
      monthMissed++;
    }
  }

  // All time stats
  let streakRun = 0;
  const sortedLogDates = Object.keys(logs).sort();

  for (const dateStr of sortedLogDates) {
    const type = getWorkoutType(dateStr);
    const log = logs[dateStr];
    if (!log || !log.completed) continue;

    if (type === 'cardio') {
      totalCardioSessions++;
      totalCardioMin += log.minutesCompleted || 0;
      if (log.heartRateZone === 'zone2') zone2Sessions++;
    }
    if (type === 'strength') {
      totalStrengthSessions++;
    }
  }

  const streak = computeStreak(logs);

  // Longest streak computation
  const allDatesCursor = new Date(startDate + 'T12:00:00');
  const endDate = new Date(todayStr + 'T12:00:00');
  let tempStreak = 0;
  let prevWasRest = false;

  while (allDatesCursor <= endDate) {
    const ds = allDatesCursor.toISOString().split('T')[0];
    const type = getWorkoutType(ds);
    if (type === 'rest') {
      allDatesCursor.setDate(allDatesCursor.getDate() + 1);
      continue;
    }
    const log = logs[ds];
    if (log && log.completed) {
      tempStreak++;
      if (tempStreak > longestStreak) longestStreak = tempStreak;
    } else if (ds < todayStr) {
      tempStreak = 0;
    }
    allDatesCursor.setDate(allDatesCursor.getDate() + 1);
  }

  const zone2Compliance = totalCardioSessions > 0
    ? Math.round((zone2Sessions / totalCardioSessions) * 100)
    : 0;

  return {
    streak,
    longestStreak,
    monthCompleted,
    monthTarget,
    monthMissed,
    totalCardioMin,
    zone2Compliance,
    totalStrengthSessions,
    totalCardioSessions
  };
}

// Helper: check and update milestones
function updateMilestones(data) {
  const stats = computeStats(data);
  const { milestones, startDate, logs } = data;
  const todayStr = new Date().toISOString().split('T')[0];

  // Count total completed workouts
  const totalCompleted = Object.values(logs).filter(l => l && l.completed).length;

  if (!milestones.firstWorkout && totalCompleted >= 1) milestones.firstWorkout = true;
  if (!milestones.streak7 && stats.longestStreak >= 7) milestones.streak7 = true;
  if (!milestones.workouts30 && totalCompleted >= 30) milestones.workouts30 = true;
  if (!milestones.cardio500min && stats.totalCardioMin >= 500) milestones.cardio500min = true;
  if (!milestones.streak30 && stats.longestStreak >= 30) milestones.streak30 = true;
  if (!milestones.workouts100 && totalCompleted >= 100) milestones.workouts100 = true;
  if (!milestones.cardio1000min && stats.totalCardioMin >= 1000) milestones.cardio1000min = true;

  // Six months from start
  const sixMonthDate = new Date(startDate + 'T12:00:00');
  sixMonthDate.setMonth(sixMonthDate.getMonth() + 6);
  if (!milestones.sixMonths && todayStr >= sixMonthDate.toISOString().split('T')[0]) {
    milestones.sixMonths = true;
  }

  // One year
  const oneYearDate = new Date(startDate + 'T12:00:00');
  oneYearDate.setFullYear(oneYearDate.getFullYear() + 1);
  if (!milestones.oneYear && todayStr >= oneYearDate.toISOString().split('T')[0]) {
    milestones.oneYear = true;
  }

  return milestones;
}

// ─── Routes ────────────────────────────────────────────────────────────────

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// GET all data
app.get('/api/data', (req, res) => {
  const data = readData();
  res.json(data);
});

// POST log a workout
app.post('/api/log', (req, res) => {
  const data = readData();
  const { date, ...logEntry } = req.body;

  if (!date) return res.status(400).json({ error: 'date required' });

  // Determine workout type if not provided
  if (!logEntry.workoutType) {
    logEntry.workoutType = getWorkoutType(date);
  }

  logEntry.loggedAt = new Date().toISOString();
  logEntry.completed = true;
  data.logs[date] = logEntry;

  // Update milestones
  data.milestones = updateMilestones(data);

  writeData(data);

  const stats = computeStats(data);
  res.json({ success: true, log: logEntry, stats, milestones: data.milestones });
});

// GET a specific day's log
app.get('/api/log/:date', (req, res) => {
  const data = readData();
  const log = data.logs[req.params.date];
  if (!log) return res.status(404).json({ error: 'No log for this date' });
  res.json(log);
});

// DELETE a log entry
app.delete('/api/log/:date', (req, res) => {
  const data = readData();
  if (!data.logs[req.params.date]) {
    return res.status(404).json({ error: 'No log for this date' });
  }
  delete data.logs[req.params.date];
  writeData(data);
  res.json({ success: true });
});

// GET stats
app.get('/api/stats', (req, res) => {
  const data = readData();
  const stats = computeStats(data);
  res.json({ ...stats, milestones: data.milestones });
});

// Serve index.html for root
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`🏋️  Best Shape by 60 — Fitness Tracker running on port ${PORT}`);
});
