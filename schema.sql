DROP TABLE IF EXISTS contacts;
CREATE TABLE contacts(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  organization text not null,
  contactPerson text not null,
  phoneNumber text not null,
  email text not null,
  address text not null
)