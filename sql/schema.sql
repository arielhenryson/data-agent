
-- Drop tables if they exist
DROP TABLE IF EXISTS "Tasks" CASCADE;
DROP TABLE IF EXISTS "Projects" CASCADE;
DROP TABLE IF EXISTS "Teams" CASCADE;
DROP TABLE IF EXISTS "Users" CASCADE;
DROP TABLE IF EXISTS "Organizations" CASCADE;

-- Create Organizations table
CREATE TABLE "Organizations" (
    "OrganizationID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255) NOT NULL,
    "CreatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Users table
CREATE TABLE "Users" (
    "UserID" SERIAL PRIMARY KEY,
    "Username" VARCHAR(255) NOT NULL UNIQUE,
    "Email" VARCHAR(255) NOT NULL UNIQUE,
    "OrganizationID" INTEGER,
    "CreatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("OrganizationID") REFERENCES "Organizations"("OrganizationID")
);

-- Create Teams table
CREATE TABLE "Teams" (
    "TeamID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255) NOT NULL,
    "OrganizationID" INTEGER NOT NULL,
    "CreatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("OrganizationID") REFERENCES "Organizations"("OrganizationID")
);

-- Create Projects table
CREATE TABLE "Projects" (
    "ProjectID" SERIAL PRIMARY KEY,
    "Name" VARCHAR(255) NOT NULL,
    "TeamID" INTEGER NOT NULL,
    "CreatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("TeamID") REFERENCES "Teams"("TeamID")
);

-- Create Tasks table
CREATE TABLE "Tasks" (
    "TaskID" SERIAL PRIMARY KEY,
    "ProjectID" INTEGER NOT NULL,
    "AssigneeID" INTEGER,
    "Title" VARCHAR(255) NOT NULL,
    "Description" TEXT,
    "Status" VARCHAR(50) NOT NULL,
    "DueDate" DATE,
    "CreatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("ProjectID") REFERENCES "Projects"("ProjectID"),
    FOREIGN KEY ("AssigneeID") REFERENCES "Users"("UserID")
);

-- Populate Organizations
INSERT INTO "Organizations" ("Name") VALUES
('Innovate Inc.'),
('Synergy Corp');

-- Populate Users
INSERT INTO "Users" ("Username", "Email", "OrganizationID") VALUES
('johndoe', 'johndoe@innovate.com', 1),
('janesmith', 'janesmith@innovate.com', 1),
('peterjones', 'peterjones@synergy.com', 2);

-- Populate Teams
INSERT INTO "Teams" ("Name", "OrganizationID") VALUES
('Development', 1),
('Marketing', 1),
('Engineering', 2);

-- Populate Projects
INSERT INTO "Projects" ("Name", "TeamID") VALUES
('Project Alpha', 1),
('Project Beta', 1),
('Marketing Campaign Q3', 2),
('New Feature Launch', 3);

-- Populate Tasks
INSERT INTO "Tasks" ("ProjectID", "AssigneeID", "Title", "Description", "Status", "DueDate") VALUES
(1, 1, 'Design database schema', 'Design the initial database schema for Project Alpha.', 'In Progress', '2025-08-15'),
(1, 2, 'Develop API endpoints', 'Develop REST API endpoints for user management.', 'To Do', '2025-08-20'),
(2, 1, 'Setup staging environment', 'Set up the staging environment for Project Beta.', 'Done', '2025-07-30'),
(3, 2, 'Create ad copy', 'Write ad copy for the Q3 marketing campaign.', 'In Progress', '2025-08-05'),
(4, 3, 'Implement new feature', 'Implement the core logic for the new feature.', 'To Do', '2025-09-01');
