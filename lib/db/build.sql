CREATE TABLE IF NOT EXISTS users (
    UserID bigint PRIMARY KEY,
    Username text,
    Balance bigint DEFAULT 0,
    KingdomName text DEFAULT 'Kingdom',
    KingdomEmblem text DEFAULT ':european_castle:',
    Army text[][],
    MobilizedArmy text[][],
    Defense text[][],
    Inventory text[][],
    Inbox text[]
    );

CREATE TABLE IF NOT EXISTS servers (
    ServerID int PRIMARY KEY,
    Prefix text DEFAULT 'k!'
    );