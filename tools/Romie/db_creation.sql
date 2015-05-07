CREATE TABLE IF NOT EXISTS "users" (
	"username" TEXT PRIMARY KEY,
	"email" TEXT UNIQUE,
	"name" TEXT,
	"surname" TEXT,
	"school" TEXT,
	"birthday" INTEGER,
	"grade" TEXT,
	"sex" INTEGER,
	"psycho" INTEGER DEFAULT 0,
	"points" INTEGER DEFAULT 0
);
