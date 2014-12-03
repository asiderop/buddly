-- buddy table contains all user information
drop table if exists buddy;
create table buddy (
    id_ integer primary key autoincrement,
    hash_ text not null unique,
    name text not null,
    email text not null unique,
    bio text
);

-- buddy_list table contains all wish lists
drop table if exists buddy_list;
create table buddy_list (
    id_ integer primary key autoincrement,
    buddy_id integer not null,
    type_id integer not null,
    url text not null,
    description text,
    foreign key (buddy_id) references buddy(id_),
    foreign key (type_id) references list_type(id_)
);

-- list_type table contains all wish list types
drop table if exists list_type;
create table list_type (
    id_ integer primary key,
    name text not null,
    base_url text not null
);

INSERT INTO list_type VALUES
    (1, "Buddly",    "http://buddly.thequery.net"),
    (2, "Amazon",    "https://www.amazon.com"),
    (3, "Pinterest", "https://www.pinterest.com"),
    (4, "Elfster",   "https://www.elfster.com");

-- event table contains information about a single gift exchange event
drop table if exists event;
create table event (
    id_ integer primary key autoincrement,
    name text not null,
    description text not null,
    image blob,
    start_date timestamp,
    num_per_santa integer not null default 1
);

-- the table maps an event to buddies (and owners)
drop table if exists event_to_buddies;
create table event_to_buddies (
    event_id integer not null,
    buddy_id integer not null,
    is_owner integer default 0,
    primary key (event_id, buddy_id),
    foreign key (buddy_id) references buddy(id_),
    foreign key (event_id) references event(id_)
);

-- restrictions table lists santa-buddy pairings that are not allowed
drop table if exists restrictions;
create table restrictions (
    santa_id integer not null,
    buddy_id integer not null,
    primary key (santa_id, buddy_id),
    foreign key (santa_id) references buddy(id_),
    foreign key (buddy_id) references buddy(id_)
);

-- pair table maps santas to buddies for an event
drop table if exists pair;
create table pair (
    event_id integer not null,
    santa_id integer not null,
    buddy_id integer not null,
    primary key (event_id, santa_id),
    check (santa_id != buddy_id),
    foreign key (event_id) references event(id_),
    foreign key (santa_id) references buddy(id_),
    foreign key (buddy_id) references buddy(id_)
);

