PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY,
  telegram_id INTEGER UNIQUE NOT NULL,
  level TEXT DEFAULT 'beginner',
  total_xp INTEGER DEFAULT 0,
  current_streak INTEGER DEFAULT 0,
  longest_streak INTEGER DEFAULT 0,
  last_activity_date DATE,
  daily_goal INTEGER DEFAULT 10,
  reminder_enabled BOOLEAN DEFAULT 1,
  reminder_time TEXT DEFAULT '09:00',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vocabulary (
  id INTEGER PRIMARY KEY,
  indonesian TEXT NOT NULL,
  russian TEXT NOT NULL,
  category TEXT NOT NULL,
  difficulty INTEGER DEFAULT 1,
  part_of_speech TEXT,
  examples_json TEXT,
  notes TEXT,
  audio_url TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(indonesian, russian)
);

CREATE INDEX IF NOT EXISTS idx_vocabulary_category ON vocabulary(category);
CREATE INDEX IF NOT EXISTS idx_vocabulary_difficulty ON vocabulary(difficulty);

CREATE TABLE IF NOT EXISTS user_words (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  word_id INTEGER NOT NULL,

  ease_factor REAL DEFAULT 2.5,
  interval_days INTEGER DEFAULT 0,
  repetitions INTEGER DEFAULT 0,
  next_review DATE,

  times_seen INTEGER DEFAULT 0,
  times_correct INTEGER DEFAULT 0,
  times_wrong INTEGER DEFAULT 0,
  last_seen TIMESTAMP,
  last_result TEXT,

  status TEXT DEFAULT 'new',

  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (word_id) REFERENCES vocabulary(id) ON DELETE CASCADE,
  UNIQUE(user_id, word_id)
);

CREATE INDEX IF NOT EXISTS idx_user_words_review ON user_words(user_id, next_review);
CREATE INDEX IF NOT EXISTS idx_user_words_status ON user_words(user_id, status);

CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  session_type TEXT NOT NULL,

  words_seen INTEGER DEFAULT 0,
  words_correct INTEGER DEFAULT 0,
  words_wrong INTEGER DEFAULT 0,
  xp_earned INTEGER DEFAULT 0,
  duration_seconds INTEGER,

  lesson_id TEXT,
  scenario_id TEXT,

  started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS user_lessons (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  lesson_id TEXT NOT NULL,

  status TEXT DEFAULT 'locked',
  score INTEGER,
  attempts INTEGER DEFAULT 0,

  started_at TIMESTAMP,
  completed_at TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, lesson_id)
);

CREATE TABLE IF NOT EXISTS achievements (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  achievement_id TEXT NOT NULL,

  unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, achievement_id)
);

CREATE TABLE IF NOT EXISTS daily_stats (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  date DATE NOT NULL,

  words_learned INTEGER DEFAULT 0,
  words_reviewed INTEGER DEFAULT 0,
  correct_answers INTEGER DEFAULT 0,
  wrong_answers INTEGER DEFAULT 0,
  xp_earned INTEGER DEFAULT 0,
  time_spent_seconds INTEGER DEFAULT 0,
  sessions_count INTEGER DEFAULT 0,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, date)
);

-- Reminders log: prevents spamming the same user multiple times per day.
CREATE TABLE IF NOT EXISTS reminders_sent (
  id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  date DATE NOT NULL,
  reminder_time TEXT NOT NULL,
  sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE(user_id, date)
);

