SELECT c.clown_id, c.clown_name, s.speciality_name, avg(r.rating) AS average_rating, COUNT(r.review_id)
FROM clown AS c
LEFT JOIN review AS r ON c.clown_id = r.clown_id
JOIN speciality AS s ON c.speciality_id = s.speciality_id
WHERE c.clown_id = 8
GROUP BY c.clown_id, c.clown_name, s.speciality_name
;

SELECT COUNT(review_id) FROM review WHERE clown_id = 8;