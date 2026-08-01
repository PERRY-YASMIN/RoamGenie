BEGIN;

CREATE TABLE users (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email varchar(254) NOT NULL UNIQUE,
  password_hash text NOT NULL,
  full_name varchar(120) NOT NULL,
  role varchar(20) NOT NULL DEFAULT 'traveller' CHECK (role IN ('traveller','admin')),
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE user_preferences (
  user_id bigint PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  hotel_preference varchar(40), food_preference varchar(80), transport_preference varchar(40), travel_style varchar(40), special_requirements text
);
CREATE TABLE activity_preferences (
  user_id bigint REFERENCES users(id) ON DELETE CASCADE,
  activity varchar(60) NOT NULL, PRIMARY KEY (user_id, activity)
);
CREATE TABLE destinations (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  city varchar(100) NOT NULL, country varchar(100) NOT NULL,
  description text NOT NULL DEFAULT '', average_daily_cost numeric(12,2) CHECK (average_daily_cost >= 0), active boolean NOT NULL DEFAULT true,
  UNIQUE(city,country)
);
CREATE TABLE hotels (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, destination_id bigint NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
  name varchar(150) NOT NULL, price_per_night numeric(12,2) NOT NULL CHECK(price_per_night >= 0), rating numeric(2,1) CHECK(rating BETWEEN 0 AND 5), UNIQUE(destination_id,name)
);
CREATE TABLE restaurants (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, destination_id bigint NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
  name varchar(150) NOT NULL, cuisine varchar(80), average_cost_per_person numeric(12,2) CHECK(average_cost_per_person >= 0), rating numeric(2,1) CHECK(rating BETWEEN 0 AND 5), UNIQUE(destination_id,name)
);
CREATE TABLE attractions (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, destination_id bigint NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
  name varchar(150) NOT NULL, category varchar(60), entry_fee numeric(12,2) NOT NULL DEFAULT 0 CHECK(entry_fee >= 0), rating numeric(2,1) CHECK(rating BETWEEN 0 AND 5), UNIQUE(destination_id,name)
);
CREATE TABLE transport_options (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, origin varchar(100) NOT NULL, destination_id bigint NOT NULL REFERENCES destinations(id) ON DELETE CASCADE,
  mode varchar(40) NOT NULL, provider varchar(100), estimated_cost numeric(12,2) NOT NULL CHECK(estimated_cost >= 0), duration_minutes integer CHECK(duration_minutes > 0)
);
CREATE TABLE trips (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  destination_id bigint NOT NULL REFERENCES destinations(id), starting_location varchar(120) NOT NULL,
  start_date date NOT NULL, end_date date NOT NULL, traveller_count integer NOT NULL CHECK(traveller_count > 0),
  total_budget numeric(12,2) NOT NULL CHECK(total_budget > 0), estimated_total numeric(12,2) NOT NULL DEFAULT 0 CHECK(estimated_total >= 0),
  status varchar(20) NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','planned','completed','cancelled')),
  created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(), CHECK(end_date >= start_date)
);
CREATE TABLE trip_members (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, trip_id bigint NOT NULL REFERENCES trips(id) ON DELETE CASCADE, display_name varchar(120) NOT NULL, age_group varchar(30), special_requirements text);
CREATE TABLE itineraries (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, trip_id bigint NOT NULL REFERENCES trips(id) ON DELETE CASCADE, version integer NOT NULL DEFAULT 1 CHECK(version > 0), summary text NOT NULL DEFAULT '', provider varchar(40) NOT NULL DEFAULT 'mock', created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(trip_id,version));
CREATE TABLE itinerary_days (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, itinerary_id bigint NOT NULL REFERENCES itineraries(id) ON DELETE CASCADE, day_number integer NOT NULL CHECK(day_number > 0), itinerary_date date NOT NULL, UNIQUE(itinerary_id,day_number));
CREATE TABLE itinerary_items (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, itinerary_day_id bigint NOT NULL REFERENCES itinerary_days(id) ON DELETE CASCADE, item_order integer NOT NULL CHECK(item_order > 0), start_time time, title varchar(180) NOT NULL, category varchar(50) NOT NULL, estimated_cost numeric(12,2) NOT NULL DEFAULT 0 CHECK(estimated_cost >= 0), notes text, UNIQUE(itinerary_day_id,item_order));
CREATE TABLE expenses (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, trip_id bigint NOT NULL REFERENCES trips(id) ON DELETE CASCADE, category varchar(40) NOT NULL, description text, amount numeric(12,2) NOT NULL CHECK(amount >= 0), incurred_on date);
CREATE TABLE budget_allocations (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, trip_id bigint NOT NULL REFERENCES trips(id) ON DELETE CASCADE, category varchar(40) NOT NULL, amount numeric(12,2) NOT NULL CHECK(amount >= 0), UNIQUE(trip_id,category));
CREATE TABLE saved_trips (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE, trip_id bigint NOT NULL REFERENCES trips(id) ON DELETE CASCADE, saved_at timestamptz NOT NULL DEFAULT now(), UNIQUE(user_id,trip_id));
CREATE TABLE reviews (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE, destination_id bigint NOT NULL REFERENCES destinations(id) ON DELETE CASCADE, rating integer NOT NULL CHECK(rating BETWEEN 1 AND 5), comment text, UNIQUE(user_id,destination_id));
CREATE TABLE ai_conversations (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, user_id bigint NOT NULL REFERENCES users(id) ON DELETE CASCADE, trip_id bigint REFERENCES trips(id) ON DELETE SET NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE ai_messages (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, conversation_id bigint NOT NULL REFERENCES ai_conversations(id) ON DELETE CASCADE, role varchar(20) NOT NULL CHECK(role IN ('user','assistant','system')), content text NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE weather_snapshots (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, destination_id bigint NOT NULL REFERENCES destinations(id) ON DELETE CASCADE, observed_at timestamptz NOT NULL, summary varchar(160) NOT NULL, temperature_c numeric(5,2), provider varchar(40) NOT NULL DEFAULT 'mock');
CREATE TABLE packing_items (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, trip_id bigint NOT NULL REFERENCES trips(id) ON DELETE CASCADE, item varchar(120) NOT NULL, category varchar(40), is_packed boolean NOT NULL DEFAULT false, UNIQUE(trip_id,item));
CREATE TABLE trip_audit (id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, trip_id bigint, action varchar(10) NOT NULL, changed_at timestamptz NOT NULL DEFAULT now(), changed_by text NOT NULL DEFAULT current_user, old_row jsonb, new_row jsonb);

COMMIT;
