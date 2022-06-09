CREATE TABLE IF NOT EXISTS botusers(
    user_id int PRIMARY KEY,
    user_token char(256),
    firstname char(256),
    user_country json,
    user_city json
); 

CREATE TABLE IF NOT EXISTS foundusers(
    found_id int PRIMARY KEY,
    user_id int NOT NULL REFERENCES botusers(user_id) ON DELETE CASCADE,
    firstname char(256) NOT NULL,
    lastname char(256) NOT NULL,
    profile text NOT NULL UNIQUE ,
    photos text NOT NULL,
    num serial
);

CREATE TABLE IF NOT EXISTS favorites(
    user_id int NOT NULL REFERENCES botusers(user_id) ON DELETE CASCADE,
    found_id int NOT NULL,
    firstname char(256) NOT NULL,
    lastname char(256) NOT NULL,
    profile text NOT NULL,
    photos text NOT NULL,
    PRIMARY KEY(user_id, found_id)
    
);




