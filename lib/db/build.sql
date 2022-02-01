CREATE TABLE IF NOT EXISTS users (
    UserID bigint PRIMARY KEY,
    Username text,
    Balance bigint DEFAULT 0,
    KingdomName text DEFAULT 'Kingdom',
    KingdomEmblem text DEFAULT 'https://cdn.discordapp.com/emojis/851545024901546054.png',
    Army text[][],
    MobilizedArmy text[][],
    Defense text[][],
    Inventory text[][],
    Inbox text[]
    );

CREATE TABLE IF NOT EXISTS servers (
    ServerID bigint PRIMARY KEY,
    Prefix text DEFAULT 'k!'
    );

CREATE TABLe IF NOT EXISTS reminders (
    ReminderID bigint PRIMARY KEY,
    Task text,
    ReminderTime timestamp,
    UserID bigint
    );
