# Normalized Database Design
## AI Travel Planner & Budget Optimizer — RoamGenie
### Academic Milestone 4: Normalized Database Design (1NF to 3NF/BCNF)

---

## 1. Normalization Objective

Database normalization is the systematic technique of organizing a relational schema to minimize data redundancy and prevent insertion, update, and deletion anomalies while enforcing referential integrity. 

In RoamGenie, normalization ensures that:
1. **Redundancy is minimized:** Destination descriptions, hotel tariffs, and attraction categories are stored once in their master tables rather than repeated across thousands of individual user trip itineraries.
2. **Anomalies are eliminated:** Modifying a hotel nightly rate or deleting a scheduled day activity does not corrupt the core destination catalogue or user profile.
3. **Data consistency is enforced:** Referential integrity rules (such as `ON DELETE CASCADE`) guarantee that dependent child records (such as day slots and activity items) remain synchronized with their parent trips.

---

## 2. Functional Dependency Analysis

A functional dependency $X \rightarrow Y$ holds over a relation $R$ if and only if whenever two tuples agree on attribute(s) $X$, they must also agree on attribute(s) $Y$.

Below is the functional dependency analysis for core RoamGenie relations:

### 2.1 Relation: `users`
* $F_1: \text{id} \rightarrow \{\text{email}, \text{password\_hash}, \text{full\_name}, \text{role}, \text{created\_at}, \text{updated\_at}\}$
* $F_2: \text{email} \rightarrow \{\text{id}, \text{password\_hash}, \text{full\_name}, \text{role}, \text{created\_at}, \text{updated\_at}\}$
* **Candidate Keys:** $\{\text{id}\}$, $\{\text{email}\}$
* **Primary Key:** $\text{id}$

### 2.2 Relation: `destinations`
* $F_1: \text{id} \rightarrow \{\text{city}, \text{country}, \text{description}, \text{average\_daily\_cost}, \text{active}\}$
* $F_2: \{\text{city}, \text{country}\} \rightarrow \{\text{id}, \text{description}, \text{average\_daily\_cost}, \text{active}\}$
* **Candidate Keys:** $\{\text{id}\}$, $\{\text{city}, \text{country}\}$
* **Primary Key:** $\text{id}$

### 2.3 Relation: `hotels`
* $F_1: \text{id} \rightarrow \{\text{destination\_id}, \text{name}, \text{price\_per\_night}, \text{rating}\}$
* $F_2: \{\text{destination\_id}, \text{name}\} \rightarrow \{\text{id}, \text{price\_per\_night}, \text{rating}\}$
* **Candidate Keys:** $\{\text{id}\}$, $\{\text{destination\_id}, \text{name}\}$
* **Primary Key:** $\text{id}$

### 2.4 Relation: `trips`
* $F_1: \text{id} \rightarrow \{\text{user\_id}, \text{destination\_id}, \text{starting\_location}, \text{start\_date}, \text{end\_date}, \text{traveller\_count}, \text{total\_budget}, \text{estimated\_total}, \text{status}, \text{created\_at}, \text{updated\_at}\}$
* **Candidate Key:** $\{\text{id}\}$
* **Primary Key:** $\text{id}$

### 2.5 Relation: `itinerary_days`
* $F_1: \text{id} \rightarrow \{\text{itinerary\_id}, \text{day\_number}, \text{itinerary\_date}\}$
* $F_2: \{\text{itinerary\_id}, \text{day\_number}\} \rightarrow \{\text{id}, \text{itinerary\_date}\}$
* **Candidate Keys:** $\{\text{id}\}$, $\{\text{itinerary\_id}, \text{day\_number}\}$
* **Primary Key:** $\text{id}$

### 2.6 Relation: `itinerary_items`
* $F_1: \text{id} \rightarrow \{\text{itinerary\_day\_id}, \text{item\_order}, \text{start\_time}, \text{title}, \text{category}, \text{estimated\_cost}, \text{notes}\}$
* $F_2: \{\text{itinerary\_day\_id}, \text{item\_order}\} \rightarrow \{\text{id}, \text{start\_time}, \text{title}, \text{category}, \text{estimated\_cost}, \text{notes}\}$
* **Candidate Keys:** $\{\text{id}\}$, $\{\text{itinerary\_day\_id}, \text{item\_order}\}$
* **Primary Key:** $\text{id}$

### 2.7 Relation: `budget_allocations`
* $F_1: \text{id} \rightarrow \{\text{trip\_id}, \text{category}, \text{amount}\}$
* $F_2: \{\text{trip\_id}, \text{category}\} \rightarrow \{\text{id}, \text{amount}\}$
* **Candidate Keys:** $\{\text{id}\}$, $\{\text{trip\_id}, \text{category}\}$
* **Primary Key:** $\text{id}$

---

## 3. First Normal Form (1NF)

### 3.1 Definition
A relation $R$ is in First Normal Form (1NF) if and only if:
1. All attributes contain strictly atomic (indivisible) domain values.
2. There are no repeating groups or multi-valued arrays nested within a single record.
3. Every row in the relation is uniquely identifiable via a primary key.

### 3.2 1NF Decomposition in RoamGenie

#### Example A: User Activity Preferences
* **Un-normalized Anti-Pattern (Violates 1NF):**
  $$\text{users\_unnormalized}(\underline{\text{id}}, \text{email}, \text{full\_name}, \text{activity\_interests})$$
  Where `activity_interests` stores a multi-valued string: `"heritage, food_tasting, trekking"`. This violates attribute atomicity and makes SQL queries searching for specific interests inefficient and complex.
* **RoamGenie 1NF Decomposition:**
  Decomposed into a separate relational table where each interest is an atomic row:
  $$\text{activity\_preferences}(\underline{\text{user\_id}}, \underline{\text{activity}})$$

#### Example B: Day-Wise Scheduled Activities
* **Un-normalized Anti-Pattern (Violates 1NF):**
  $$\text{trips\_unnormalized}(\underline{\text{id}}, \text{destination}, \text{daily\_activities})$$
  Where `daily_activities` stores a nested JSON array of morning, afternoon, and evening tasks.
* **RoamGenie 1NF Decomposition:**
  Decomposed into discrete entities: `itineraries`, `itinerary_days`, and `itinerary_items`. Each item represents exactly one atomic record:
  $$\text{itinerary\_items}(\underline{\text{id}}, \text{itinerary\_day\_id}, \text{item\_order}, \text{start\_time}, \text{title}, \text{category}, \text{estimated\_cost}, \text{notes})$$

---

## 4. Second Normal Form (2NF)

### 4.1 Definition
A relation $R$ is in Second Normal Form (2NF) if and only if:
1. $R$ is in 1NF.
2. No non-prime attribute is partially functionally dependent on any candidate key of $R$ (i.e., every non-prime attribute must depend on the *entire* candidate key, not a proper subset).

*Note: Any relation whose candidate keys consist strictly of single attributes is trivially in 2NF.*

### 4.2 2NF Analysis in RoamGenie

* **Single-Attribute Keys:** In relations such as `users`, `destinations`, `trips`, `hotels`, `restaurants`, `attractions`, and `itinerary_items`, the primary key is a single surrogate attribute `id`. Because no composite primary key exists, partial key dependencies are mathematically impossible, satisfying 2NF.
* **Composite Candidate Keys:**
  - In `activity_preferences(user_id, activity)`, the candidate key is $\{\text{user\_id}, \text{activity}\}$. All attributes are prime (members of the key); thus, no non-prime partial dependency can exist.
  - In `budget_allocations`, considering candidate key $\{\text{trip\_id}, \text{category}\}$, the non-prime attribute `amount` depends on the combination of the specific trip *and* the specific category. It does not depend on `trip_id` alone (a trip has multiple category amounts) nor on `category` alone (a category amount varies by trip). Thus, full functional dependency holds.

---

## 5. Third Normal Form (3NF)

### 5.1 Definition
A relation $R$ is in Third Normal Form (3NF) if and only if:
1. $R$ is in 2NF.
2. For every non-trivial functional dependency $X \rightarrow A$, either:
   - $X$ is a superkey of $R$, or
   - $A$ is a prime attribute (part of a candidate key).

In practical terms, 3NF eliminates **transitive functional dependencies** ($X \rightarrow Y \rightarrow Z$, where non-key attribute $Z$ depends on non-key attribute $Y$).

### 5.2 3NF Decomposition & Proofs in RoamGenie

#### Example A: Hotel and Destination Relationship
* **Transitive Dependency Anti-Pattern (Violates 3NF):**
  Suppose hotels and destination details were combined into a single relation:
  $$\text{hotels\_unnormalized}(\underline{\text{hotel\_id}}, \text{name}, \text{price}, \text{destination\_id}, \text{city\_name}, \text{country}, \text{avg\_daily\_cost})$$
  Here, functional dependencies exist:
  $$\text{hotel\_id} \rightarrow \text{destination\_id}$$
  $$\text{destination\_id} \rightarrow \{\text{city\_name}, \text{country}, \text{avg\_daily\_cost}\}$$
  Because $\text{destination\_id}$ is not a candidate key for the whole relation, the dependency $\text{hotel\_id} \rightarrow \{\text{city\_name}, \text{country}\}$ is transitive.
  *Anomalies caused:*
  - *Redundancy:* City and country names are duplicated across every hotel in that city.
  - *Update Anomaly:* Renaming a city requires updating thousands of hotel rows.
  - *Insertion Anomaly:* Cannot record a new destination until at least one hotel is registered.
* **RoamGenie 3NF Normalized Solution:**
  Decompose into two separate 3NF relations linked by foreign key:
  $$\text{destinations}(\underline{\text{id}}, \text{city}, \text{country}, \text{description}, \text{average\_daily\_cost}, \text{active})$$
  $$\text{hotels}(\underline{\text{id}}, \text{destination\_id} \rightarrow \text{destinations.id}, \text{name}, \text{price\_per\_night}, \text{rating})$$

#### Example B: Trips and User Information
* In `trips`, traveller personal details (such as `full_name` or `email`) are not stored. Only `user_id` is referenced as a foreign key.
* The dependency $\text{trip\_id} \rightarrow \text{user\_id} \rightarrow \text{email}$ is resolved by isolating user profile attributes inside `users`.

---

## 6. Boyce-Codd Normal Form (BCNF) Evaluation

### 6.1 Definition
A relation $R$ is in Boyce-Codd Normal Form (BCNF) if and only if for every non-trivial functional dependency $X \rightarrow A$, $X$ is a **strict superkey** of $R$.

BCNF is a stricter version of 3NF that eliminates anomalies in relations containing overlapping composite candidate keys.

### 6.2 BCNF Evaluation in RoamGenie
* In `destinations`, the non-trivial dependencies are:
  - $\text{id} \rightarrow \{\text{city}, \text{country}, \text{description}, \text{average\_daily\_cost}, \text{active}\}$ (where $\text{id}$ is a superkey)
  - $\{\text{city}, \text{country}\} \rightarrow \{\text{id}, \text{description}, \text{average\_daily\_cost}, \text{active}\}$ (where $\{\text{city}, \text{country}\}$ is a superkey)
  Every determinant is a candidate superkey. Therefore, `destinations` satisfies BCNF.
* In all 22 domain relations across RoamGenie, every functional dependency has a determinant that is a candidate key or superkey. Thus, the database schema satisfies 3NF and conforms to BCNF.

---

## 7. Final Normalized Design & Anomaly Prevention

The resulting 22-table normalized relational architecture provides formal guarantees against the classical database anomalies:

| Anomaly Type | Un-Normalized Vulnerability | RoamGenie 3NF/BCNF Guarantee |
| :--- | :--- | :--- |
| **Insertion Anomaly** | Cannot create a new destination without booking a trip or hotel. | Destinations exist independently in `destinations` and can be catalogued before any hotels or trips exist. |
| **Update Anomaly** | Changing an attraction entry fee requires updating dozens of saved user itineraries. | Master attraction fees live solely in `attractions`. Realized trip items snapshot specific schedule costs in `itinerary_items` without mutating master catalogue rows. |
| **Deletion Anomaly** | Deleting a cancelled trip accidentally deletes the user account or host destination. | Cascading deletes are scoped strictly: deleting a trip removes its dependent child rows (`itineraries`, `itinerary_days`, `itinerary_items`, `budget_allocations`) while preserving `users` and `destinations`. |

---

## 8. Relationship Integrity & Constraint Enforcement

The database enforces integrity through multiple complementary mechanisms:
1. **Primary Key Constraints (`PRIMARY KEY`):** Guarantees entity uniqueness across all relations.
2. **Foreign Key Constraints (`REFERENCES`):** Enforces referential integrity across master and transactional tables.
3. **Cascade Rules (`ON DELETE CASCADE`):** Automatically purges orphan records when parent entities are removed (e.g., deleting a trip removes its budget allocations).
4. **Domain Check Constraints (`CHECK`):** Restricts numerical bounds (e.g., `price_per_night >= 0`, `rating BETWEEN 0 AND 5`, `end_date >= start_date`).
5. **Unique Constraints (`UNIQUE`):** Prevents duplicate entries (e.g., `UNIQUE(destination_id, name)` on hotels, `UNIQUE(city, country)` on destinations).
