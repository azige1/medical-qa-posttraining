CREATE TABLE users (
  user_id INTEGER PRIMARY KEY,
  user_name TEXT NOT NULL,
  city TEXT NOT NULL,
  vip_level TEXT NOT NULL
);

CREATE TABLE items (
  item_id INTEGER PRIMARY KEY,
  item_name TEXT NOT NULL,
  category TEXT NOT NULL,
  price REAL NOT NULL
);

CREATE TABLE purchases (
  purchase_id INTEGER PRIMARY KEY,
  user_id INTEGER NOT NULL,
  item_id INTEGER NOT NULL,
  purchase_date TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  paid_amount REAL NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(user_id),
  FOREIGN KEY (item_id) REFERENCES items(item_id)
);
