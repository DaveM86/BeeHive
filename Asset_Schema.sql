--
-- PostgreSQL database dump
--

-- Dumped from database version 13.1
-- Dumped by pg_dump version 13.1

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: activity_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.activity_log (
    activity_log_id integer NOT NULL,
    activity_type character varying(50),
    serial_number character varying(50),
    date_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    query_submitted character varying(2000)
);


ALTER TABLE public.activity_log OWNER TO postgres;

--
-- Name: activity; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.activity AS
 SELECT to_char(activity_log.date_time, 'dd-mm-yy HH24:MI'::text) AS datetime,
    activity_log.activity_type,
    activity_log.serial_number,
    activity_log.query_submitted
   FROM public.activity_log;


ALTER TABLE public.activity OWNER TO postgres;

--
-- Name: activity_log_activity_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.activity_log_activity_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.activity_log_activity_log_id_seq OWNER TO postgres;

--
-- Name: activity_log_activity_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.activity_log_activity_log_id_seq OWNED BY public.activity_log.activity_log_id;


--
-- Name: equiptment; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equiptment (
    equip_id integer NOT NULL,
    serial_number character varying(50),
    part_number character varying(50) NOT NULL,
    description character varying(50),
    encrytpion character varying(50),
    location_id integer,
    room_box_id integer,
    barcode character varying(50)
);


ALTER TABLE public.equiptment OWNER TO postgres;

--
-- Name: location; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.location (
    location_id integer NOT NULL,
    building_capability character varying(100) NOT NULL
);


ALTER TABLE public.location OWNER TO postgres;

--
-- Name: asset_location; Type: VIEW; Schema: public; Owner: david
--

CREATE VIEW public.asset_location AS
 SELECT equiptment.serial_number,
    equiptment.description,
    location.building_capability
   FROM (public.equiptment
     JOIN public.location ON ((equiptment.location_id = location.location_id)));


ALTER TABLE public.asset_location OWNER TO david;

--
-- Name: comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comments (
    comment_id integer NOT NULL,
    equip_id integer,
    comment character varying(2000) NOT NULL,
    date timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.comments OWNER TO postgres;

--
-- Name: comments_comment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comments_comment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.comments_comment_id_seq OWNER TO postgres;

--
-- Name: comments_comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comments_comment_id_seq OWNED BY public.comments.comment_id;


--
-- Name: deployments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deployments (
    deployment_id integer NOT NULL,
    deployment_location character varying(50) NOT NULL,
    num_personnel_req smallint NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL
);


ALTER TABLE public.deployments OWNER TO postgres;

--
-- Name: deployments_deployment_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deployments_deployment_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deployments_deployment_id_seq OWNER TO postgres;

--
-- Name: deployments_deployment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deployments_deployment_id_seq OWNED BY public.deployments.deployment_id;


--
-- Name: equip_fault; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.equip_fault (
    equip_id integer,
    fault_id integer
);


ALTER TABLE public.equip_fault OWNER TO postgres;

--
-- Name: equiptment_equip_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.equiptment_equip_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.equiptment_equip_id_seq OWNER TO postgres;

--
-- Name: equiptment_equip_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.equiptment_equip_id_seq OWNED BY public.equiptment.equip_id;


--
-- Name: faults; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.faults (
    fault_id integer NOT NULL,
    fault_desc character varying(250) NOT NULL,
    fault_date timestamp without time zone NOT NULL,
    status character varying(50) NOT NULL,
    raised_by character varying(50) NOT NULL,
    booking_ref character varying(50),
    update_fault character varying(250),
    last_update timestamp without time zone NOT NULL
);


ALTER TABLE public.faults OWNER TO postgres;

--
-- Name: faults_fault_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.faults_fault_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faults_fault_id_seq OWNER TO postgres;

--
-- Name: faults_fault_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.faults_fault_id_seq OWNED BY public.faults.fault_id;


--
-- Name: location_location_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.location_location_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.location_location_id_seq OWNER TO postgres;

--
-- Name: location_location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.location_location_id_seq OWNED BY public.location.location_id;


--
-- Name: network_connections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.network_connections (
    connection_id integer NOT NULL,
    switch_id integer,
    port_number smallint NOT NULL,
    equip_id integer
);


ALTER TABLE public.network_connections OWNER TO postgres;

--
-- Name: network_connections_connection_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.network_connections_connection_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.network_connections_connection_id_seq OWNER TO postgres;

--
-- Name: network_connections_connection_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.network_connections_connection_id_seq OWNED BY public.network_connections.connection_id;


--
-- Name: room_box; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.room_box (
    room_box_id integer NOT NULL,
    room_box character varying(100) NOT NULL,
    location_id integer
);


ALTER TABLE public.room_box OWNER TO postgres;

--
-- Name: room_box_room_box_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.room_box_room_box_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.room_box_room_box_id_seq OWNER TO postgres;

--
-- Name: room_box_room_box_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.room_box_room_box_id_seq OWNED BY public.room_box.room_box_id;


--
-- Name: switches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.switches (
    switch_id integer NOT NULL,
    switch_serial character varying(50) NOT NULL,
    description character varying(100),
    location_id integer,
    room_id integer,
    num_ports smallint NOT NULL
);


ALTER TABLE public.switches OWNER TO postgres;

--
-- Name: switches_switch_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.switches_switch_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.switches_switch_id_seq OWNER TO postgres;

--
-- Name: switches_switch_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.switches_switch_id_seq OWNED BY public.switches.switch_id;


--
-- Name: activity_log activity_log_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_log ALTER COLUMN activity_log_id SET DEFAULT nextval('public.activity_log_activity_log_id_seq'::regclass);


--
-- Name: comments comment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments ALTER COLUMN comment_id SET DEFAULT nextval('public.comments_comment_id_seq'::regclass);


--
-- Name: deployments deployment_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployments ALTER COLUMN deployment_id SET DEFAULT nextval('public.deployments_deployment_id_seq'::regclass);


--
-- Name: equiptment equip_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equiptment ALTER COLUMN equip_id SET DEFAULT nextval('public.equiptment_equip_id_seq'::regclass);


--
-- Name: faults fault_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faults ALTER COLUMN fault_id SET DEFAULT nextval('public.faults_fault_id_seq'::regclass);


--
-- Name: location location_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.location ALTER COLUMN location_id SET DEFAULT nextval('public.location_location_id_seq'::regclass);


--
-- Name: network_connections connection_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.network_connections ALTER COLUMN connection_id SET DEFAULT nextval('public.network_connections_connection_id_seq'::regclass);


--
-- Name: room_box room_box_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_box ALTER COLUMN room_box_id SET DEFAULT nextval('public.room_box_room_box_id_seq'::regclass);


--
-- Name: switches switch_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.switches ALTER COLUMN switch_id SET DEFAULT nextval('public.switches_switch_id_seq'::regclass);


--
-- Name: activity_log activity_log_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.activity_log
    ADD CONSTRAINT activity_log_pkey PRIMARY KEY (activity_log_id);


--
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (comment_id);


--
-- Name: deployments deployments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deployments
    ADD CONSTRAINT deployments_pkey PRIMARY KEY (deployment_id);


--
-- Name: equiptment equiptment_barcode_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equiptment
    ADD CONSTRAINT equiptment_barcode_key UNIQUE (barcode);


--
-- Name: equiptment equiptment_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equiptment
    ADD CONSTRAINT equiptment_pkey PRIMARY KEY (equip_id);


--
-- Name: equiptment equiptment_serial_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equiptment
    ADD CONSTRAINT equiptment_serial_number_key UNIQUE (serial_number);


--
-- Name: faults faults_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faults
    ADD CONSTRAINT faults_pkey PRIMARY KEY (fault_id);


--
-- Name: location location_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.location
    ADD CONSTRAINT location_pkey PRIMARY KEY (location_id);


--
-- Name: network_connections network_connections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.network_connections
    ADD CONSTRAINT network_connections_pkey PRIMARY KEY (connection_id);


--
-- Name: room_box room_box_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_box
    ADD CONSTRAINT room_box_pkey PRIMARY KEY (room_box_id);


--
-- Name: switches switches_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.switches
    ADD CONSTRAINT switches_pkey PRIMARY KEY (switch_id);


--
-- Name: comments comments_equip_id_fkey_cascade; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_equip_id_fkey_cascade FOREIGN KEY (equip_id) REFERENCES public.equiptment(equip_id) ON DELETE CASCADE;


--
-- Name: equip_fault equip_fault_equip_id_fkey_cascade; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equip_fault
    ADD CONSTRAINT equip_fault_equip_id_fkey_cascade FOREIGN KEY (equip_id) REFERENCES public.equiptment(equip_id) ON DELETE CASCADE;


--
-- Name: equip_fault equip_fault_fault_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equip_fault
    ADD CONSTRAINT equip_fault_fault_id_fkey FOREIGN KEY (fault_id) REFERENCES public.faults(fault_id);


--
-- Name: equiptment equiptment_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equiptment
    ADD CONSTRAINT equiptment_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.location(location_id);


--
-- Name: equiptment equiptment_room_box_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.equiptment
    ADD CONSTRAINT equiptment_room_box_id_fkey FOREIGN KEY (room_box_id) REFERENCES public.room_box(room_box_id);


--
-- Name: network_connections network_connections_equip_id_fkey_cascade; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.network_connections
    ADD CONSTRAINT network_connections_equip_id_fkey_cascade FOREIGN KEY (equip_id) REFERENCES public.equiptment(equip_id) ON DELETE CASCADE;


--
-- Name: network_connections network_connections_switch_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.network_connections
    ADD CONSTRAINT network_connections_switch_id_fkey FOREIGN KEY (switch_id) REFERENCES public.switches(switch_id);


--
-- Name: room_box room_box_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.room_box
    ADD CONSTRAINT room_box_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.location(location_id);


--
-- Name: switches switches_location_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.switches
    ADD CONSTRAINT switches_location_id_fkey FOREIGN KEY (location_id) REFERENCES public.location(location_id);


--
-- Name: switches switches_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.switches
    ADD CONSTRAINT switches_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.room_box(room_box_id);


--
-- PostgreSQL database dump complete
--

