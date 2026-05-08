# Best Shape by 60 — Colin's Fitness Tracker

Personal fitness tracking app built around Colin's cardiac-safe workout plan.

## Features
- Daily workout guidance based on schedule
- Cardio, strength, and active rest logging
- Streak tracking and missed day counter
- 60th birthday countdown
- Monthly calendar with color-coded history
- Progress stats and health snapshot
- Milestone achievements

## Deployment

### Build & Run (Docker)
```bash
cd /data/.openclaw/workspace/fitness-tracker
docker build -t colin-fitness .
docker stop colin-fitness 2>/dev/null; docker rm colin-fitness 2>/dev/null
docker run -d --name colin-fitness -p 3001:3001 \
  -v $(pwd)/fitness-data.json:/app/fitness-data.json \
  --restart unless-stopped colin-fitness
```

### Access
http://187.124.64.233:3001

## Weekly Schedule
| Day | Workout |
|-----|---------|
| Mon | Full Body Strength (45 min) |
| Tue | Zone 2 Cardio (30 min) |
| Wed | Full Body Strength (45 min) |
| Thu | Zone 2 Cardio (30 min) |
| Fri | Zone 2 Cardio (30 min) |
| Sat | Active Rest / Dog Walk |
| Sun | Full Rest |
