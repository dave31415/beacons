drop table if exists entries;
create table entries (
    id integer primary key autoincrement,
    uuid string not null,
    major integer not null,
    minor integer not null,
    rssi integer not null,
    date_str string not null 
);
