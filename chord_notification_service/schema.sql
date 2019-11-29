DROP TABLE IF EXISTS notifications;

CREATE TABLE notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    action_type TEXT,  -- Generic fields to be used at a notification-specific level to guide UIs
    action_target TEXT, -- "
    read INTEGER NOT NULL DEFAULT 0 CHECK (read = 0 OR read = 1)
);
