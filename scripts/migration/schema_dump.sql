--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY "public"."checkpoint_writes" DROP CONSTRAINT IF EXISTS "fk_writes_thread";
ALTER TABLE IF EXISTS ONLY "public"."checkpoints" DROP CONSTRAINT IF EXISTS "fk_checkpoints_thread";
ALTER TABLE IF EXISTS ONLY "public"."checkpoint_blobs" DROP CONSTRAINT IF EXISTS "fk_blobs_thread";
DROP TRIGGER IF EXISTS "checkpoint_blobs_thread_registration" ON "public"."checkpoint_blobs";
DROP TRIGGER IF EXISTS "auto_insert_thread_on_checkpoint" ON "public"."checkpoints";
DROP INDEX IF EXISTS "public"."threads_user_id_idx";
DROP INDEX IF EXISTS "public"."checkpoints_thread_id_idx";
DROP INDEX IF EXISTS "public"."checkpoint_writes_thread_id_idx";
DROP INDEX IF EXISTS "public"."checkpoint_blobs_thread_id_idx";
ALTER TABLE IF EXISTS ONLY "public"."threads" DROP CONSTRAINT IF EXISTS "threads_pkey";
ALTER TABLE IF EXISTS ONLY "public"."checkpoints" DROP CONSTRAINT IF EXISTS "checkpoints_pkey";
ALTER TABLE IF EXISTS ONLY "public"."checkpoint_writes" DROP CONSTRAINT IF EXISTS "checkpoint_writes_pkey";
ALTER TABLE IF EXISTS ONLY "public"."checkpoint_migrations" DROP CONSTRAINT IF EXISTS "checkpoint_migrations_pkey";
ALTER TABLE IF EXISTS ONLY "public"."checkpoint_blobs" DROP CONSTRAINT IF EXISTS "checkpoint_blobs_pkey";
DROP TABLE IF EXISTS "public"."threads";
DROP TABLE IF EXISTS "public"."checkpoints";
DROP TABLE IF EXISTS "public"."checkpoint_writes";
DROP TABLE IF EXISTS "public"."checkpoint_migrations";
DROP TABLE IF EXISTS "public"."checkpoint_blobs";
SET default_tablespace = '';

SET default_table_access_method = "heap";

--
-- Name: checkpoint_blobs; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."checkpoint_blobs" (
    "thread_id" "text" NOT NULL,
    "checkpoint_ns" "text" DEFAULT ''::"text" NOT NULL,
    "channel" "text" NOT NULL,
    "version" "text" NOT NULL,
    "type" "text" NOT NULL,
    "blob" "bytea"
);


--
-- Name: checkpoint_migrations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."checkpoint_migrations" (
    "v" integer NOT NULL
);


--
-- Name: checkpoint_writes; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."checkpoint_writes" (
    "thread_id" "text" NOT NULL,
    "checkpoint_ns" "text" DEFAULT ''::"text" NOT NULL,
    "checkpoint_id" "text" NOT NULL,
    "task_id" "text" NOT NULL,
    "idx" integer NOT NULL,
    "channel" "text" NOT NULL,
    "type" "text",
    "blob" "bytea" NOT NULL,
    "task_path" "text" DEFAULT ''::"text" NOT NULL
);


--
-- Name: checkpoints; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."checkpoints" (
    "thread_id" "text" NOT NULL,
    "checkpoint_ns" "text" DEFAULT ''::"text" NOT NULL,
    "checkpoint_id" "text" NOT NULL,
    "parent_checkpoint_id" "text",
    "type" "text",
    "checkpoint" "jsonb" NOT NULL,
    "metadata" "jsonb" DEFAULT '{}'::"jsonb" NOT NULL
);


--
-- Name: threads; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."threads" (
    "thread_id" "text" NOT NULL,
    "created_at" timestamp without time zone DEFAULT "now"(),
    "metadata" "jsonb" DEFAULT '{}'::"jsonb",
    "user_id" "text",
    "last_access" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: checkpoint_blobs checkpoint_blobs_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."checkpoint_blobs"
    ADD CONSTRAINT "checkpoint_blobs_pkey" PRIMARY KEY ("thread_id", "checkpoint_ns", "channel", "version");


--
-- Name: checkpoint_migrations checkpoint_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."checkpoint_migrations"
    ADD CONSTRAINT "checkpoint_migrations_pkey" PRIMARY KEY ("v");


--
-- Name: checkpoint_writes checkpoint_writes_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."checkpoint_writes"
    ADD CONSTRAINT "checkpoint_writes_pkey" PRIMARY KEY ("thread_id", "checkpoint_ns", "checkpoint_id", "task_id", "idx");


--
-- Name: checkpoints checkpoints_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."checkpoints"
    ADD CONSTRAINT "checkpoints_pkey" PRIMARY KEY ("thread_id", "checkpoint_ns", "checkpoint_id");


--
-- Name: threads threads_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."threads"
    ADD CONSTRAINT "threads_pkey" PRIMARY KEY ("thread_id");


--
-- Name: checkpoint_blobs_thread_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "checkpoint_blobs_thread_id_idx" ON "public"."checkpoint_blobs" USING "btree" ("thread_id");


--
-- Name: checkpoint_writes_thread_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "checkpoint_writes_thread_id_idx" ON "public"."checkpoint_writes" USING "btree" ("thread_id");


--
-- Name: checkpoints_thread_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "checkpoints_thread_id_idx" ON "public"."checkpoints" USING "btree" ("thread_id");


--
-- Name: threads_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "threads_user_id_idx" ON "public"."threads" USING "btree" ("user_id");


--
-- Name: checkpoints auto_insert_thread_on_checkpoint; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER "auto_insert_thread_on_checkpoint" BEFORE INSERT ON "public"."checkpoints" FOR EACH ROW EXECUTE FUNCTION "public"."insert_thread_if_missing"();


--
-- Name: checkpoint_blobs checkpoint_blobs_thread_registration; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER "checkpoint_blobs_thread_registration" BEFORE INSERT OR UPDATE ON "public"."checkpoint_blobs" FOR EACH ROW EXECUTE FUNCTION "public"."auto_register_thread"();


--
-- Name: checkpoint_blobs fk_blobs_thread; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."checkpoint_blobs"
    ADD CONSTRAINT "fk_blobs_thread" FOREIGN KEY ("thread_id") REFERENCES "public"."threads"("thread_id");


--
-- Name: checkpoints fk_checkpoints_thread; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."checkpoints"
    ADD CONSTRAINT "fk_checkpoints_thread" FOREIGN KEY ("thread_id") REFERENCES "public"."threads"("thread_id") ON DELETE CASCADE;


--
-- Name: checkpoint_writes fk_writes_thread; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."checkpoint_writes"
    ADD CONSTRAINT "fk_writes_thread" FOREIGN KEY ("thread_id") REFERENCES "public"."threads"("thread_id");


--
-- PostgreSQL database dump complete
--

