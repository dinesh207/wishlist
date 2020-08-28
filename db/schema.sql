CREATE TABLE if not exists Users (
 Id integer PRIMARY KEY,
 FirstName text not null,
 LastName text not null,
 Email text not null UNIQUE,
 Password text not null
);

CREATE TABLE if not exists Books (
 Id integer PRIMARY KEY,
 Title text not null,
 Author text not null,
 ISBN text not null,
 DateOfPublication text not null
);

CREATE TABLE if not exists Wishlist (
 id integer PRIMARY KEY,
 UserId text not null,
 BookId text not null,
 UNIQUE(UserId, BookId),
 FOREIGN KEY (UserId) references Users (Id),
 FOREIGN KEY (BookId) references Books (Id)
);