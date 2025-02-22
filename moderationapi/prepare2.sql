CREATE TABLE IF NOT EXISTS swear_words
(
    word text NOT NULL
);

CREATE TABLE IF NOT EXISTS scheduled
(
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    ad_id uuid NOT NULL,
    ad_title text NOT NULL,
    ad_text text NOT NULL,
    PRIMARY KEY (id)
);