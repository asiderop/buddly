-- buddy table contains all user information
drop table if exists buddy;
create table buddy (
    id integer primary key autoincrement,
    name text not null,
    email text not null unique,
    hash text not null unique
);

-- event table contains information about a single gift exchange event
drop table if exists event;
create table event (
    id integer primary key autoincrement,
    name text not null,
    description text not null,
    image blob,
    start_date real,
    end_date real
);

-- admin table maps events to owners
drop table if exists admin;
create table admin (
    buddyid integer not null,
    eventid integer not null,
    primary key (buddyid, eventid),
    foreign key (buddyid) references buddy(id),
    foreign key (eventid) references event(id)
);

-- pair table maps santas to buddies for an event
drop table if exists pair;
create table pair (
    santaid integer not null,
    buddyid integer not null,
    eventid integer not null,
    primary key (santaid, buddyid, eventid),
    check (santaid != buddyid),
    foreign key (santaid) references buddy(id),
    foreign key (buddyid) references buddy(id),
    foreign key (eventid) references event(id)
);

