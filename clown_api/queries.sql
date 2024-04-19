
-- select * from review;

-- SELECT clown_id, COUNT(review_id) AS review_count, AVG(rating) as average_rating
-- FROM review
-- GROUP BY clown_id


SELECT 
    c.clown_id, 
    c.clown_name, 
    s.speciality_name, 
    AVG(r.rating) AS average_rating, 
    COUNT(r.review_id) AS review_count
FROM clown AS c
LEFT JOIN review AS r ON c.clown_id = r.clown_id
JOIN speciality AS s ON c.speciality_id = s.speciality_id
WHERE r.review_id IS NOT NULL
GROUP BY c.clown_id, c.clown_name, s.speciality_name
ORDER BY average_rating desc;



SELECT c.clown_id, c.clown_name, s.speciality_name
FROM clown AS c
LEFT JOIN review AS r ON c.clown_id = r.clown_id
JOIN speciality AS s ON c.speciality_id = s.speciality_id
WHERE r.review_id IS NULL
GROUP BY c.clown_id, c.clown_name, s.speciality_name;

