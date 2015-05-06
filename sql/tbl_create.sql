CREATE TABLE "statuses" (
       "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
       "status_id" integer NOT NULL,
       "status_text" text,
       "user_id" integer NOT NULL,
       "user_screen_name" text,
       "status_reply" boolean,
       "status_at" datetime,
       "created_at" datetime,
       "updated_at" datetime
       );
