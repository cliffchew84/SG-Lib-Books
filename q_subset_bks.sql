WITH user_bks AS (
    SELECT 
        ub."UserName",
        ub."BID"
    FROM user_books AS ub
    WHERE "UserName" = 'cliffchew84'
), bks_info AS (
    SELECT * 
    FROM books_info
    RIGHT JOIN user_bks
    USING ("BID")
)
SELECT 
    ba."CallNumber",
    bi."TitleName",
    bi."Author",
    bi."BID",
    bi."Subjects",
    bi."Publisher",
    bi."isbns"
FROM books_avail AS ba
RIGHT JOIN bks_info AS bi
USING ("BID")
