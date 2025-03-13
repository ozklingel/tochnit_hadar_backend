--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3
-- Dumped by pg_dump version 15.3

-- Started on 2024-10-22 00:26:16

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

--
-- TOC entry 2 (class 3079 OID 16503)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 3604 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 864 (class 1247 OID 294348)
-- Name: taskfrequencyrepeattypeenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.taskfrequencyrepeattypeenum AS ENUM (
    'DAILY',
    'WEEKLY',
    'MONTHLY',
    'YEARLY',
    'UNLIMITED'
);


ALTER TYPE public.taskfrequencyrepeattypeenum OWNER TO postgres;

--
-- TOC entry 867 (class 1247 OID 294360)
-- Name: taskfrequencyweekdayenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.taskfrequencyweekdayenum AS ENUM (
    'SUNDAY',
    'MONDAY',
    'TUESDAY',
    'WEDNESDAY',
    'THURSDAY',
    'FRIDAY',
    'SATURDAY'
);


ALTER TYPE public.taskfrequencyweekdayenum OWNER TO postgres;

--
-- TOC entry 873 (class 1247 OID 294384)
-- Name: taskstatusenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.taskstatusenum AS ENUM (
    'TODO',
    'DRAFT',
    'DONE'
);


ALTER TYPE public.taskstatusenum OWNER TO postgres;

--
-- TOC entry 870 (class 1247 OID 294376)
-- Name: tasksubjecttypeenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tasksubjecttypeenum AS ENUM (
    'USER',
    'INSTITUTION',
    'APPRENTICE'
);


ALTER TYPE public.tasksubjecttypeenum OWNER TO postgres;

--
-- TOC entry 882 (class 1247 OID 327218)
-- Name: tasktubtypeenum; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tasktubtypeenum AS ENUM (
    'PERSONALR',
    'GENERAL',
    'CALL',
    'MEET',
    'PERANTs'
);


ALTER TYPE public.tasktubtypeenum OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 223 (class 1259 OID 277699)
-- Name: apprentice; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.apprentice (
    id integer NOT NULL,
    teudatzehut text DEFAULT ''::text,
    accompany_id integer,
    last_name text DEFAULT ''::text,
    maritalstatus text DEFAULT ''::text,
    marriage_date date,
    marriage_date_ivry text,
    teacher_grade_b_phone text DEFAULT ''::text,
    teacher_grade_b text DEFAULT ''::text,
    teacher_grade_b_email text DEFAULT ''::text,
    teacher_grade_a_phone text DEFAULT ''::text,
    teacher_grade_a_email text DEFAULT ''::text,
    teacher_grade_a text DEFAULT ''::text,
    high_school_teacher_phone text DEFAULT ''::text,
    high_school_teacher text DEFAULT ''::text,
    high_school_name text DEFAULT ''::text,
    high_school_teacher_email text DEFAULT ''::text,
    contact1_email text DEFAULT ''::text,
    contact1_first_name text DEFAULT ''::text,
    contact1_last_name text DEFAULT ''::text,
    contact1_phone text DEFAULT ''::text,
    contact1_relation text DEFAULT ''::text,
    contact2_email text DEFAULT ''::text,
    contact2_phone text DEFAULT ''::text,
    contact2_first_name text DEFAULT ''::text,
    contact2_last_name text DEFAULT ''::text,
    contact2_relation text DEFAULT ''::text,
    contact3_phone text DEFAULT ''::text,
    contact3_first_name text DEFAULT ''::text,
    contact3_last_name text DEFAULT ''::text,
    contact3_email text DEFAULT ''::text,
    contact3_relation text DEFAULT ''::text,
    militarycompoundid integer DEFAULT 14509,
    unit_name text DEFAULT ''::text,
    serve_type text DEFAULT ''::text,
    paying boolean DEFAULT false,
    release_date date,
    recruitment_date date,
    onlinestatus integer DEFAULT 0,
    matsber text DEFAULT ''::text,
    thperiod text DEFAULT ''::text,
    password text DEFAULT ''::text,
    phone text DEFAULT ''::text,
    email text DEFAULT ''::text,
    birthday date,
    institution_id integer DEFAULT 0,
    address text DEFAULT ''::text,
    creationdate text DEFAULT ''::text,
    photo_path text DEFAULT 'https://www.gravatar.com/avatar'::text,
    city_id integer DEFAULT 0,
    cluster_id integer DEFAULT 0,
    army_role text DEFAULT ''::text,
    militarypositionold text DEFAULT ''::text,
    militaryupdateddatetime date,
    educationalinstitution text DEFAULT ''::text,
    educationfaculty text DEFAULT ''::text,
    workoccupation text DEFAULT ''::text,
    worktype text DEFAULT ''::text,
    workplace text DEFAULT ''::text,
    workstatus text DEFAULT ''::text,
    militarypositionnew text DEFAULT ''::text,
    first_name text DEFAULT ''::text,
    institution_mahzor text DEFAULT ''::text,
    association_date date,
    birthday_ivry text DEFAULT ''::text,
    house_number integer
);


ALTER TABLE public.apprentice OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 277650)
-- Name: base; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.base (
    id integer NOT NULL,
    name text DEFAULT ''::text,
    cordinatot text DEFAULT ''::text
);


ALTER TABLE public.base OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 277636)
-- Name: cities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cities (
    id integer NOT NULL,
    name text DEFAULT ''::text,
    cluster_id integer DEFAULT 0
);


ALTER TABLE public.cities OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 277620)
-- Name: clusters; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.clusters (
    id integer NOT NULL,
    name text DEFAULT ''::text
);


ALTER TABLE public.clusters OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 277826)
-- Name: ent_group; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ent_group (
    id integer NOT NULL,
    user_id integer,
    group_name text DEFAULT ''::text
);


ALTER TABLE public.ent_group OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 277839)
-- Name: gift; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.gift (
    code text NOT NULL,
    was_used boolean DEFAULT false
);


ALTER TABLE public.gift OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 277600)
-- Name: institutions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.institutions (
    roshyeshiva_phone text DEFAULT ''::text,
    roshyeshiva_name text DEFAULT ''::text,
    admin_phone text DEFAULT ''::text,
    admin_name text DEFAULT ''::text,
    id integer NOT NULL,
    address text DEFAULT ''::text,
    city_id text DEFAULT ''::text,
    phone text DEFAULT ''::text,
    contact_name text DEFAULT ''::text,
    contact_phone text DEFAULT ''::text,
    logo_path text DEFAULT ''::text,
    name text DEFAULT ''::text,
    owner_id text DEFAULT ''::text,
    cluster_id integer,
    shluha text
);


ALTER TABLE public.institutions OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 223879)
-- Name: madadim_setting; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.madadim_setting (
    cenes_madad_date date DEFAULT '1999-09-09'::date,
    tochnitmeet_madad_date date DEFAULT '1999-09-09'::date,
    eshcolmosadmeet_madad_date date DEFAULT '1999-09-09'::date,
    mosadyeshiva_madad_date date DEFAULT '1999-09-09'::date,
    hazana_madad_date date DEFAULT '1999-09-09'::date,
    professionalmeet_madad_date date DEFAULT '1999-09-09'::date,
    matzbarmeet_madad_date date DEFAULT '1999-09-09'::date,
    doforbogrim_madad_date date DEFAULT '1999-09-09'::date,
    basis_madad_date date DEFAULT '1999-09-09'::date,
    callhorim_madad_date date DEFAULT '1999-09-09'::date,
    groupmeet_madad_date date DEFAULT '1999-09-09'::date,
    meet_madad_date date DEFAULT '1999-09-09'::date,
    call_madad_date date DEFAULT '1999-09-09'::date
);


ALTER TABLE public.madadim_setting OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 277784)
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    created_by_id integer,
    created_for_id integer NOT NULL,
    created_at timestamp without time zone,
    subject text DEFAULT ''::text,
    content text DEFAULT ''::text,
    allreadyread boolean DEFAULT false,
    attachments text[] DEFAULT '{}'::text[],
    icon text DEFAULT 'empty'::text,
    description text DEFAULT ''::text,
    type text DEFAULT 'draft'::text,
    ent_group text DEFAULT ''::text
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 277300)
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id integer NOT NULL,
    subject text DEFAULT ''::text,
    userid integer,
    event text DEFAULT ''::text,
    date date,
    created_at timestamp without time zone,
    allreadyread boolean DEFAULT false,
    numoflinesdisplay integer,
    details text DEFAULT ''::text,
    frequency text DEFAULT ''::text,
    institution_id boolean DEFAULT false
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 277628)
-- Name: regions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regions (
    id integer NOT NULL,
    name text DEFAULT ''::text
);


ALTER TABLE public.regions OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 277809)
-- Name: reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reports (
    ent_reported integer NOT NULL,
    user_id integer,
    visit_in_army boolean DEFAULT false,
    visit_date date,
    note text DEFAULT ''::text,
    title text DEFAULT ''::text,
    attachments text[] DEFAULT '{}'::text[],
    description text DEFAULT ''::text,
    allreadyread boolean DEFAULT false,
    ent_group text DEFAULT ''::text,
    created_at timestamp without time zone,
    id uuid NOT NULL
);


ALTER TABLE public.reports OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 277847)
-- Name: system_report; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_report (
    creation_date date DEFAULT '1999-09-09'::date,
    type text DEFAULT ''::text,
    related_id integer,
    value text,
    id uuid NOT NULL
);


ALTER TABLE public.system_report OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 294392)
-- Name: task_frequency; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.task_frequency (
    id integer NOT NULL,
    repeat_count integer,
    repeat_type public.taskfrequencyrepeattypeenum NOT NULL,
    weekdays public.taskfrequencyweekdayenum[],
    CONSTRAINT task_frequency_check CHECK (((repeat_type = 'WEEKLY'::public.taskfrequencyrepeattypeenum) = (weekdays IS NOT NULL)))
);


ALTER TABLE public.task_frequency OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 294391)
-- Name: task_frequency_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.task_frequency_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.task_frequency_id_seq OWNER TO postgres;

--
-- TOC entry 3605 (class 0 OID 0)
-- Dependencies: 230
-- Name: task_frequency_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.task_frequency_id_seq OWNED BY public.task_frequency.id;


--
-- TOC entry 229 (class 1259 OID 277901)
-- Name: tasks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tasks (
    id uuid NOT NULL,
    user_id integer,
    name text DEFAULT ''::text,
    start_date timestamp without time zone,
    created_at timestamp without time zone,
    description text DEFAULT ''::text,
    status text DEFAULT ''::text,
    subject_id text DEFAULT ''::text,
    has_been_read boolean DEFAULT false,
    institution_id boolean DEFAULT false,
    subject_type text,
    made_by_user boolean,
    frequency_id integer,
    end_date timestamp without time zone,
    tub_type text
);

	CREATE TABLE public.notifications (
   id uuid NOT NULL,
    user_id integer,
    name text DEFAULT ''::text,
    description text DEFAULT ''::text,
		has_been_read BOOLEAN,
		    created_at timestamp without time zone

);


ALTER TABLE public.tasks OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 277659)
-- Name: user1; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user1 (
    id integer NOT NULL,
    role_ids text DEFAULT ''::text,
    first_name text DEFAULT ''::text,
    last_name text DEFAULT ''::text,
    teudatzehut text DEFAULT ''::text,
    email text DEFAULT ''::text,
    birthday date,
    institution_id integer DEFAULT 0,
    address text DEFAULT ''::text,
    creationdate date,
    photo_path text DEFAULT 'https://www.gravatar.com/avatar'::text,
    city_id integer DEFAULT 0,
    cluster_id integer DEFAULT 0,
    notifystartweek boolean DEFAULT false,
    notifymorning boolean DEFAULT true,
    notifydaybefore boolean DEFAULT false,
    notifymorning_weekly_report boolean DEFAULT false,
    notifymorning_sevev boolean DEFAULT false,
    notifydaybefore_sevev boolean DEFAULT false,
    notifystartweek_sevev boolean DEFAULT false,
    association_date date,
    region_id integer,
    house_number integer,
    "fcmToken" text
);


ALTER TABLE public.user1 OWNER TO postgres;

--
-- TOC entry 3394 (class 2604 OID 294395)
-- Name: task_frequency id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_frequency ALTER COLUMN id SET DEFAULT nextval('public.task_frequency_id_seq'::regclass);


--
-- TOC entry 3588 (class 0 OID 277650)
-- Dependencies: 221
-- Data for Name: base; Type: TABLE DATA; Schema: public; Owner: postgres
--

--
-- TOC entry 3606 (class 0 OID 0)
-- Dependencies: 230
-- Name: task_frequency_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.task_frequency_id_seq', 65, true);


--
-- TOC entry 3411 (class 2606 OID 277763)
-- Name: apprentice apprentice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apprentice
    ADD CONSTRAINT apprentice_pkey PRIMARY KEY (id);


--
-- TOC entry 3407 (class 2606 OID 277658)
-- Name: base base_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.base
    ADD CONSTRAINT base_pkey PRIMARY KEY (id);


--
-- TOC entry 3405 (class 2606 OID 277644)
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (id);


--
-- TOC entry 3401 (class 2606 OID 277627)
-- Name: clusters clusters_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.clusters
    ADD CONSTRAINT clusters_pkey PRIMARY KEY (id);


--
-- TOC entry 3413 (class 2606 OID 277798)
-- Name: messages contact_forms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT contact_forms_pkey PRIMARY KEY (id, created_for_id);


--
-- TOC entry 3417 (class 2606 OID 277833)
-- Name: ent_group ent_group_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ent_group
    ADD CONSTRAINT ent_group_pkey PRIMARY KEY (id);


--
-- TOC entry 3419 (class 2606 OID 277846)
-- Name: gift gift_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.gift
    ADD CONSTRAINT gift_pkey PRIMARY KEY (code);


--
-- TOC entry 3399 (class 2606 OID 277619)
-- Name: institutions institutions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT institutions_pkey PRIMARY KEY (id);


--
-- TOC entry 3397 (class 2606 OID 277312)
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- TOC entry 3403 (class 2606 OID 277635)
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (id);


--
-- TOC entry 3415 (class 2606 OID 418124)
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id, ent_reported);


--
-- TOC entry 3421 (class 2606 OID 418109)
-- Name: system_report system_report_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_report
    ADD CONSTRAINT system_report_pkey PRIMARY KEY (id);


--
-- TOC entry 3425 (class 2606 OID 294400)
-- Name: task_frequency task_frequency_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.task_frequency
    ADD CONSTRAINT task_frequency_pkey PRIMARY KEY (id);


--
-- TOC entry 3423 (class 2606 OID 327370)
-- Name: tasks task_user_made_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT task_user_made_pkey PRIMARY KEY (id);


--
-- TOC entry 3409 (class 2606 OID 277683)
-- Name: user1 user1_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user1
    ADD CONSTRAINT user1_pkey PRIMARY KEY (id);


--
-- TOC entry 3427 (class 2606 OID 277684)
-- Name: user1 fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user1
    ADD CONSTRAINT fk_1 FOREIGN KEY (institution_id) REFERENCES public.institutions(id);


--
-- TOC entry 3431 (class 2606 OID 277764)
-- Name: apprentice fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apprentice
    ADD CONSTRAINT fk_1 FOREIGN KEY (institution_id) REFERENCES public.institutions(id);


--
-- TOC entry 3435 (class 2606 OID 277799)
-- Name: messages fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT fk_1 FOREIGN KEY (created_by_id) REFERENCES public.user1(id);


--
-- TOC entry 3437 (class 2606 OID 277821)
-- Name: reports fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT fk_1 FOREIGN KEY (user_id) REFERENCES public.user1(id);


--
-- TOC entry 3438 (class 2606 OID 277834)
-- Name: ent_group fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ent_group
    ADD CONSTRAINT fk_1 FOREIGN KEY (user_id) REFERENCES public.user1(id);


--
-- TOC entry 3439 (class 2606 OID 277917)
-- Name: tasks fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_1 FOREIGN KEY (user_id) REFERENCES public.user1(id);


--
-- TOC entry 3426 (class 2606 OID 277922)
-- Name: cities fk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT fk_1 FOREIGN KEY (cluster_id) REFERENCES public.regions(id);


--
-- TOC entry 3428 (class 2606 OID 277689)
-- Name: user1 fk_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user1
    ADD CONSTRAINT fk_2 FOREIGN KEY (city_id) REFERENCES public.cities(id);


--
-- TOC entry 3432 (class 2606 OID 277769)
-- Name: apprentice fk_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apprentice
    ADD CONSTRAINT fk_2 FOREIGN KEY (city_id) REFERENCES public.cities(id);


--
-- TOC entry 3436 (class 2606 OID 277804)
-- Name: messages fk_2; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT fk_2 FOREIGN KEY (created_for_id) REFERENCES public.user1(id);


--
-- TOC entry 3429 (class 2606 OID 277694)
-- Name: user1 fk_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user1
    ADD CONSTRAINT fk_3 FOREIGN KEY (cluster_id) REFERENCES public.clusters(id);


--
-- TOC entry 3433 (class 2606 OID 277779)
-- Name: apprentice fk_3; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apprentice
    ADD CONSTRAINT fk_3 FOREIGN KEY (cluster_id) REFERENCES public.clusters(id);


--
-- TOC entry 3434 (class 2606 OID 277774)
-- Name: apprentice fk_4; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.apprentice
    ADD CONSTRAINT fk_4 FOREIGN KEY (militarycompoundid) REFERENCES public.base(id);


--
-- TOC entry 3430 (class 2606 OID 294451)
-- Name: user1 fk_8; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user1
    ADD CONSTRAINT fk_8 FOREIGN KEY (region_id) REFERENCES public.regions(id);


-- Completed on 2024-10-22 00:26:16

--
-- PostgreSQL database dump complete
--

