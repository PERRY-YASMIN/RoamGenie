CREATE OR REPLACE PROCEDURE refresh_trip_total(p_trip_id bigint)
LANGUAGE plpgsql AS $$
BEGIN
  UPDATE trips SET estimated_total=calculate_trip_estimated_total(p_trip_id),updated_at=now() WHERE id=p_trip_id;
  IF NOT FOUND THEN RAISE EXCEPTION 'trip % does not exist',p_trip_id; END IF;
END $$;
