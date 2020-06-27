DROP TABLE IF EXISTS configs;
CREATE TABLE  configs ( email VARCHAR(120) PRIMARY KEY,  VARCHAR(20), token char(200), secret CHAR(200));
DROP TABLE IF EXISTS video_cache;
CREATE TABLE youtube_cache (id char(11) PRIMARY KEY, title VARCHAR(120), thumbnail_url VARCHAR(400));
