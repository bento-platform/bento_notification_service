DROP TABLE IF EXISTS notifications;

CREATE TABLE notifications (
    id TEXT PRIMARY KEY,  -- UUID
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    notification_type TEXT,  -- Generic fields to be used at a notification-specific level to guide UIs
    action_target TEXT, -- "
    read INTEGER NOT NULL DEFAULT 0 CHECK (read = 0 OR read = 1),
    timestamp TEXT NOT NULL
);
