class SqlQueries:
    """Container for sql statements used by DAG tasks"""

    songplay_table_insert = ("""
        INSERT INTO {} (play_id, start_time, user_id, level, song_id,
            artist_id, session_id, location, user_agent)
            SELECT
                md5(events.sessionid || events.ts),
                TIMESTAMP 'epoch' + events.ts/1000 * INTERVAL '1 second',
                events.userid,
                events.level,
                songs.song_id,
                songs.artist_id,
                events.sessionid,
                events.location,
                events.useragent
            FROM (SELECT * FROM staging_events WHERE page='NextSong') events
            LEFT JOIN staging_songs songs
            ON events.song = songs.title
                AND events.artist = songs.artist_name
                AND events.length = songs.duration
    """)

    user_table_insert = ("""
        INSERT INTO {} (user_id, first_name, last_name, gender, level)
            SELECT distinct userid, firstname, lastname, gender, level
            FROM staging_events
            WHERE page='NextSong'
    """)

    song_table_insert = ("""
        INSERT INTO {} (song_id, title, artist_id, year, duration)
            SELECT distinct song_id, title, artist_id, year, duration
            FROM staging_songs
    """)

    artist_table_insert = ("""
        INSERT INTO {} (artist_id, name, location, latitude, longitude)
            SELECT distinct artist_id, artist_name, artist_location,
                artist_latitude, artist_longitude
            FROM staging_songs
    """)

    time_table_insert = ("""
        INSERT INTO {} (start_time, hour, day, week, month, year, weekday)
            SELECT
                start_time,
                extract(hour from start_time),
                extract(day from start_time),
                extract(week from start_time),
                extract(month from start_time),
                extract(year from start_time),
                extract(dayofweek from start_time)
            FROM songplays
    """)
