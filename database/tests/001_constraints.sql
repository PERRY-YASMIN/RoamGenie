\set ON_ERROR_STOP on
BEGIN;
INSERT INTO users(email,password_hash,full_name) VALUES('constraint@example.test','not-a-real-password-hash','Constraint Test') RETURNING id \gset user_
INSERT INTO destinations(city,country,description) VALUES('Constraint City','Testland','temporary') RETURNING id \gset destination_
INSERT INTO trips(user_id,destination_id,starting_location,start_date,end_date,traveller_count,total_budget)
VALUES(:user_id,:destination_id,'Origin','2026-09-01','2026-09-02',1,1000) RETURNING id \gset trip_
DO $$ BEGIN
  BEGIN
    INSERT INTO expenses(trip_id,category,amount) VALUES(:trip_id,'invalid',-1);
    RAISE EXCEPTION 'negative expense constraint did not fire';
  EXCEPTION WHEN check_violation THEN NULL; END;
END $$;
DO $$ BEGIN
  BEGIN
    INSERT INTO trips(user_id,destination_id,starting_location,start_date,end_date,traveller_count,total_budget)
    VALUES(:user_id,:destination_id,'Origin','2026-09-03','2026-09-01',0,0);
    RAISE EXCEPTION 'trip constraints did not fire';
  EXCEPTION WHEN check_violation THEN NULL; END;
END $$;
ROLLBACK;
SELECT 'constraint tests passed' result;

