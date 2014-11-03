-- buddy table contains all user information
drop table if exists buddy;
create table buddy (
    id_ integer primary key autoincrement,
    hash_ text not null unique,
    name text not null,
    email text not null unique
);

-- event table contains information about a single gift exchange event
drop table if exists event;
create table event (
    id_ integer primary key autoincrement,
    name text not null,
    description text not null,
    image blob,
    start_date timestamp
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

-- pair table maps santas to buddies for an event
drop table if exists pair;
create table pair (
    santa_id integer not null,
    buddy_id integer not null,
    event_id integer not null,
    primary key (santa_id, buddy_id, event_id),
    check (santa_id != buddy_id),
    foreign key (santa_id) references buddy(id_),
    foreign key (buddy_id) references buddy(id_),
    foreign key (event_id) references event(id_)
);

