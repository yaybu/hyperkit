
create table distro (
    name text not null,
    primary key(name)
);

create table release (
    name text not null,
    distro text not null,
    foreign key(distro) references distro(name),
    primary key(name)
);

create table architecture (
    name text not null,
    distro text not null,
    foreign key(distro) references distro(name),
    primary key(name)
);

create table hypervisor (
    name text not null
);

create table candidate (
    distro text not null,
    release text not null,
    architecture text not null,
    foreign key(release, distro) references release(name, distro),
    foreign key(architecture, distro) references architecture(name, distro)
);

create table test_run (
    id int not null,
    hypervisor text not null,
    distro text not null,
    release text not null,
    architecture text not null,
    status text not null,
    foreign key(hypervisor) references hypervisor(name),
    foreign key(distro) references distro(name),
    foreign key(release) references release(name),
    foreign key(architecture) references architecture(name),
    primary key(id)
);

create table build (
    id int not null,
    test_run int not null,
    name text not null,
    succeeded int not null,
    details text,
    foreign key (test_run) references test_run(id),
    primary key(id)
);
