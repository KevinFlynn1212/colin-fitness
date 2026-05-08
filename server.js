const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;
const DATA_FILE = path.join(__dirname, 'fitness-data.json');

app.use(express.json());
app.use(express.static(__dirname));

function loadData() {
  try { return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8')); }
  catch(e) { return getDefaultData(); }
}

function getDefaultData() {
  return {
    startDate:'2026-05-08', goal:'Best Bove 60', goalDate:'2031-10-18',
    workoutGoal:500, logs:{}, prs:{}, bodyWeight:{},
    cheatDays:0, spinsAvailable:{}, cheatHistory:[],
    milestones:{firstWorkout:false,streak7:false,workouts30:false,cardio500min:false,streak30:false,workouts100:false,cardio1000min:false,sixMonths:false,oneYear:false}
  };
}

function saveData(data) { fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2)); }

function computeStats(data) {
  const logs = data.logs;
  const logDates = Object.keys(logs).sort();
  let totalCardioMinutes=0, totalStrengthSessions=0, cardioZone2Sessions=0, totalCardioSessions=0, totalVolume=0;

  for (const date of logDates) {
    const log = logs[date];
    if (log.type==='cardio') {
      totalCardioMinutes += log.minutes||0;
      totalCardioSessions++;
      if (log.zone==='zone2') cardioZone2Sessions++;
    } else if (log.type==='strength') {
      totalStrengthSessions++;
      for (const exId of Object.keys(log.exercises||{})) {
        for (const set of (log.exercises[exId].sets||[])) {
          if (set.weight && set.unit!=='sec') totalVolume += set.weight*(set.reps||1);
        }
      }
    }
  }

  const today = new Date().toISOString().split('T')[0];
  let currentStreak=0;
  let checkDate = new Date(today);
  while (true) {
    const ds = checkDate.toISOString().split('T')[0];
    const log = logs[ds], dow = checkDate.getDay();
    if (log && ['cardio','strength','active','cheat'].includes(log.type)) currentStreak++;
    else if (dow===0) { /* rest */ }
    else break;
    checkDate.setDate(checkDate.getDate()-1);
    if (currentStreak>365) break;
  }

  let longestStreak=0, tempStreak=0;
  let d = new Date(data.startDate), todayDate = new Date(today);
  while (d<=todayDate) {
    const ds=d.toISOString().split('T')[0], log=logs[ds], dow=new Date(ds).getDay();
    if (log && ['cardio','strength','active','cheat'].includes(log.type)) { tempStreak++; if(tempStreak>longestStreak)longestStreak=tempStreak; }
    else if (dow===0) {}
    else tempStreak=0;
    d.setDate(d.getDate()+1);
  }

  const now = new Date();
  const monthStart = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-01`;
  let monthWorkouts=0, monthMissed=0;
  let d2=new Date(monthStart);
  while (d2<=new Date(today)) {
    const ds=d2.toISOString().split('T')[0], dow=d2.getDay(), log=logs[ds];
    if (dow!==0) {
      if (log && ['cardio','strength','active','cheat'].includes(log.type)) monthWorkouts++;
      else if (ds<today) monthMissed++;
    }
    d2.setDate(d2.getDate()+1);
  }

  const startOfWeek = new Date(now);
  startOfWeek.setDate(now.getDate()-now.getDay()+1);
  let weekDone=0;
  for (let i=0;i<5;i++) {
    const wd=new Date(startOfWeek); wd.setDate(startOfWeek.getDate()+i);
    const wds=wd.toISOString().split('T')[0];
    if (logs[wds]&&['cardio','strength'].includes(logs[wds].type)) weekDone++;
  }

  const totalWorkouts = totalCardioSessions+totalStrengthSessions;
  const workoutGoal = data.workoutGoal||500;
  const m = data.milestones||{};

  // Check milestone triggers and award spins
  const spins = data.spinsAvailable||{};
  if (totalWorkouts>=1 && !m.firstWorkout) { m.firstWorkout=true; }
  if ((currentStreak>=7||longestStreak>=7) && !m.streak7) { m.streak7=true; if(!spins.streak7)spins.streak7=true; }
  if (totalWorkouts>=30 && !m.workouts30) { m.workouts30=true; if(!spins.workouts30)spins.workouts30=true; }
  if (totalCardioMinutes>=500 && !m.cardio500min) { m.cardio500min=true; if(!spins.cardio500)spins.cardio500=true; }
  if ((currentStreak>=30||longestStreak>=30) && !m.streak30) { m.streak30=true; if(!spins.streak30)spins.streak30=true; }
  if (totalWorkouts>=100 && !m.workouts100) { m.workouts100=true; if(!spins.workouts100)spins.workouts100=true; }
  if (totalCardioMinutes>=1000 && !m.cardio1000min) { m.cardio1000min=true; if(!spins.cardio1000)spins.cardio1000=true; }
  const daysSinceStart = Math.floor((new Date(today)-new Date(data.startDate))/86400000);
  if (daysSinceStart>=180) m.sixMonths=true;
  if (daysSinceStart>=365) m.oneYear=true;

  // Streak-based spins (every 7 days, every 14, every 30)
  if (currentStreak>0 && currentStreak%7===0 && currentStreak<=13 && !spins[`streak${currentStreak}`]) {
    spins[`streak${currentStreak}`]=true;
  }
  if (currentStreak===14 && !spins.streak14) spins.streak14=true;

  data.milestones = m;
  data.spinsAvailable = spins;

  return {
    currentStreak, longestStreak, totalCardioMinutes, totalStrengthSessions,
    totalCardioSessions, totalWorkouts, totalVolume:Math.round(totalVolume),
    zone2Compliance:totalCardioSessions>0?Math.round((cardioZone2Sessions/totalCardioSessions)*100):0,
    monthWorkouts, monthMissed, weekDone, weekTotal:5,
    workoutsToGoal:Math.max(0,workoutGoal-totalWorkouts),
    workoutGoalProgress:Math.min(100,Math.round((totalWorkouts/workoutGoal)*100)),
    daysUntilGoal:Math.ceil((new Date(data.goalDate)-new Date(today))/86400000),
    milestones:m
  };
}

app.get('/api/data', (req,res) => {
  const data = loadData();
  const stats = computeStats(data);
  saveData(data);
  res.json({...data, stats});
});

app.get('/api/stats', (req,res) => { const data=loadData(); res.json(computeStats(data)); });

app.post('/api/log', (req,res) => {
  const data = loadData();
  const {date,log} = req.body;
  if (!date||!log) return res.status(400).json({error:'date and log required'});
  data.logs[date] = {...log, loggedAt:new Date().toISOString()};
  if (!data.prs) data.prs={};
  if (log.type==='strength'&&log.exercises) {
    for (const exId of Object.keys(log.exercises)) {
      for (const set of (log.exercises[exId].sets||[])) {
        if (set.weight&&set.unit!=='sec') {
          if (!data.prs[exId]||set.weight>data.prs[exId].weight) {
            data.prs[exId]={weight:set.weight,reps:set.reps,date};
          }
        }
      }
    }
  }
  const stats = computeStats(data);
  saveData(data);
  res.json({success:true, stats, prs:data.prs});
});

app.get('/api/log/:date', (req,res) => {
  const data=loadData(), log=data.logs[req.params.date];
  if (!log) return res.status(404).json({error:'No log'});
  res.json(log);
});

app.delete('/api/log/:date', (req,res) => {
  const data=loadData(); delete data.logs[req.params.date]; saveData(data);
  res.json({success:true});
});

app.post('/api/bodyweight', (req,res) => {
  const data=loadData();
  const {date,weight}=req.body;
  if (!date||!weight) return res.status(400).json({error:'required'});
  if (!data.bodyWeight) data.bodyWeight={};
  data.bodyWeight[date]=parseFloat(weight);
  saveData(data);
  res.json({success:true});
});

app.post('/api/spin-reward', (req,res) => {
  const data=loadData();
  const {prize,reason}=req.body;
  if (!data.spinsAvailable) data.spinsAvailable={};
  if (!data.cheatHistory) data.cheatHistory=[];
  // Clear the spin
  if (reason) data.spinsAvailable[reason]=false;
  // Apply prize
  if (prize.cheatDays>0) {
    data.cheatDays=(data.cheatDays||0)+prize.cheatDays;
    data.cheatHistory.push({date:new Date().toISOString().split('T')[0],type:'earned',amount:prize.cheatDays,prize:prize.label});
  } else if (prize.special) {
    data.cheatHistory.push({date:new Date().toISOString().split('T')[0],type:'earned',amount:0,prize:prize.label});
  }
  saveData(data);
  res.json({success:true,cheatDays:data.cheatDays});
});

app.post('/api/cashin-cheat', (req,res) => {
  const data=loadData();
  const {date}=req.body;
  if ((data.cheatDays||0)===0) return res.status(400).json({error:'No cheat days'});
  data.cheatDays--;
  if (!data.cheatHistory) data.cheatHistory=[];
  data.cheatHistory.push({date,type:'used',amount:-1,prize:'Cheat Day Used'});
  data.logs[date]={type:'cheat',loggedAt:new Date().toISOString()};
  saveData(data);
  res.json({success:true,cheatDays:data.cheatDays});
});

app.get('/health', (req,res) => res.json({status:'ok'}));
app.get('*', (req,res) => res.sendFile(path.join(__dirname,'index.html')));

app.listen(PORT, () => console.log(`🎰 Best Bove 60 running on port ${PORT}`));
