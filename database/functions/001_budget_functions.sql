CREATE OR REPLACE FUNCTION calculate_trip_estimated_total(p_trip_id bigint)
RETURNS numeric LANGUAGE sql STABLE AS $$
  SELECT COALESCE((SELECT sum(amount) FROM budget_allocations WHERE trip_id=p_trip_id),0)
       + COALESCE((SELECT sum(amount) FROM expenses WHERE trip_id=p_trip_id),0)
$$;

CREATE OR REPLACE FUNCTION remaining_trip_budget(p_trip_id bigint)
RETURNS numeric LANGUAGE sql STABLE AS $$
  SELECT total_budget-calculate_trip_estimated_total(id) FROM trips WHERE id=p_trip_id
$$;

