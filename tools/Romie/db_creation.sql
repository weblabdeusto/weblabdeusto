CREATE TABLE IF NOT EXISTS "forotech" (
"username" TEXT PRIMARY KEY,
"name" TEXT,
"surname" TEXT,
"school" TEXT,
"birthday" INTEGER,
"email" TEXT UNIQUE,
"points" INTEGER
);