CREATE TABLE IF NOT EXISTS advertisers
(
    id uuid NOT NULL,
    name text NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS campaigns
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    impressions_limit bigint NOT NULL,
    clicks_limit bigint NOT NULL,
    cost_per_impression double precision NOT NULL,
    cost_per_click double precision NOT NULL,
    ad_title text NOT NULL,
    ad_text text NOT NULL,
    start_date integer NOT NULL,
    end_date integer NOT NULL,
    gender text,
    age_from integer,
    age_to integer,
    location text,
    advertiser_id uuid NOT NULL,
    image text DEFAULT NULL,
    is_moderated boolean DEFAULT true,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS clicks
(
    campaign_id uuid NOT NULL,
    date integer NOT NULL,
    client_id uuid NOT NULL,
    cost double precision NOT NULL,
    affects_stats boolean NOT NULL DEFAULT false 
);

CREATE TABLE IF NOT EXISTS clients
(
    id uuid NOT NULL,
    login text NOT NULL,
    age integer NOT NULL,
    location text NOT NULL,
    gender text NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS impressions
(
    campaign_id uuid NOT NULL,
    date integer NOT NULL,
    client_id uuid NOT NULL,
    cost double precision NOT NULL,
    affects_stats boolean NOT NULL DEFAULT false 
);

CREATE TABLE IF NOT EXISTS mlscores
(
    client_id uuid NOT NULL,
    advertiser_id uuid NOT NULL,
    score integer NOT NULL
);
