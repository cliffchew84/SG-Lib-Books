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
    bi."TitleName",
    bi."Author",
    ba."BranchName",
    ba."CallNumber",
    ba."StatusDesc",
    ba."DueDate",
    ba."InsertTime",
    bi."BID",
    bi."Subjects",
    bi."Publisher",
    bi."isbns"
FROM books_avail AS ba
RIGHT JOIN bks_info AS bi
USING ("BID")
