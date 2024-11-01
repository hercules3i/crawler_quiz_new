Declare @JSON nvarchar(max)
DECLARE @sql nvarchar(MAX), @datafile nvarchar(1000)
DECLARE @SubjectName nvarchar(255)
DECLARE @SubjectCode nvarchar(255)
DECLARE @ExamName nvarchar(255)
DECLARE @ExamCode nvarchar(255)
DECLARE @Index INT = 526
CREATE TABLE #tmpSubjectAndExams
(
	ID INT,
	SubjectName NVARCHAR(255),
	Title NVARCHAR(255),
	ExamName NVARCHAR(255),
	Error BIT,
	Code NVARCHAR(255)
)
print 'tao bang #tmpSubjectAndExams thanh cong'
CREATE TABLE #tmpQuiz
(
	Id INT,
	[Order] INT,
	Duration INT,
	Unit NVARCHAR(255),
	Mark INT,
	Content NVARCHAR(MAX),
	Solve NVARCHAR(MAX),
	QuestionMedia NVARCHAR(MAX),
	Code NVARCHAR(1000),
	[Type] NVARCHAR(1000),
	AnswerData NVARCHAR(MAX),
	IdQuiz INT,
	UserChoose NVARCHAR(255)
)
print 'tao bang #tmpQuiz thanh cong'
CREATE TABLE #tmpFiles
(
   subdirectory NVARCHAR(1000),
   depth INT,
   [file] BIT
)
print 'tao bang #tmpFiles thanh cong'

INSERT INTO #tmpFiles
EXEC xp_dirtree N'D:\CrawlerData\Latex_json\JpJson', 1, 1
--SELECT * FROM #tmpFiles
-- DECLARE the cursors
DECLARE CUR CURSOR FAST_FORWARD READ_ONLY FOR SELECT subdirectory, depth, [file] FROM #tmpFiles

-- DECLARE some variables to store the values in
DECLARE @varSubdirectory NVARCHAR(1000)
DECLARE @varDepth int
DECLARE @varFile bit


OPEN CUR
FETCH NEXT FROM CUR INTO @varSubdirectory, @varDepth, @varFile



WHILE @@FETCH_STATUS = 0
BEGIN
    -- In ra giá trị của @varSubdirectory
    PRINT 'Current Subdirectory: ' + @varSubdirectory
    
    PRINT @Index
    SELECT @datafile = N'D:\CrawlerData\Latex_json\JpJson\file_name'
    SELECT @datafile = replace(@datafile, '''', '''''')
    SELECT @datafile = replace(@datafile, 'file_name', @varSubdirectory)
    PRINT (@datafile)
    
    SELECT @sql = N'SELECT @Var=BulkColumn
                    FROM OPENROWSET(BULK ''' + @datafile + ''',
                   SINGLE_NCLOB) as import'
    PRINT @sql
    
    EXECUTE sp_executesql @sql, N'@Var NVARCHAR(max) OUTPUT', @Var=@JSON OUTPUT
    SELECT *
    FROM OPENJSON (@JSON)
    INSERT INTO #tmpSubjectAndExams
    SELECT *
    FROM OPENJSON (@JSON)
    WITH 
    (
        [ID] int, 
        [SubjectName] nvarchar(255), 
        [Title] nvarchar(255), 
        [ExamName] nvarchar(255), 
        [Error] bit, 
        [Code] nvarchar(255)
    )
    SELECT * FROM #tmpFiles;
    INSERT INTO #tmpQuiz
    SELECT *
    FROM OPENJSON(@JSON,'$.Object.details')
    WITH 
    (
        Id INT,
        [Order] INT,
        Duration INT,
        Unit NVARCHAR(255),
        Mark INT,
        Content NVARCHAR(MAX),
        Solve NVARCHAR(MAX) AS JSON,
        QuestionMedia NVARCHAR(MAX) AS JSON,
        Code NVARCHAR(1000),
        [Type] NVARCHAR(1000),
        AnswerData NVARCHAR(MAX) AS JSON,
        IdQuiz INT,
        UserChoose NVARCHAR(255)
    )
    
    -- Lấy các giá trị cho các biến chèn dữ liệu
    SELECT @SubjectCode = 'LANG-JAPANESE',
           @ExamName = ExamName,
           @ExamCode = Code
    FROM #tmpSubjectAndExams
    
    INSERT INTO LMS_PRACTICE_TEST_HEADER (SUBJECT_CODE, PRACTICE_TEST_CODE, PRACTICE_TEST_TITLE, DURATION, UNIT, CREATED_BY, CREATED_TIME, IS_DELETED) 
    VALUES(@SubjectCode, @ExamCode, @ExamName, 60, 'MINUTE', 'admin', GETDATE(), 0)
    
    INSERT INTO QUIZ_POOL ([CODE], [CONTENT], [JSON_DATA], [SUBJECT_CODE], [TYPE], [QUESTION_MEDIA], [SOLVE], DURATION, UNIT, SHARE, CREATED_BY, CREATED_TIME, IS_DELETED, HAS_CORRECT_ANSWER) 
    SELECT Code, Content, AnswerData, @SubjectCode, [TYPE], QuestionMedia, [SOLVE], [DURATION], [UNIT], '', 'admin', GETDATE(), 0, 1 FROM #tmpQuiz
    
    INSERT INTO LMS_PRACTICE_TEST_DETAIL([QUEST_CODE], [MARK], [ORDER], [PRACTICE_TEST_CODE], DURATION, UNIT, CREATED_BY, CREATED_TIME, IS_DELETED) 
    SELECT Code, Mark, [ORDER], @ExamCode, [DURATION], [UNIT], 'admin', GETDATE(), 0 FROM #tmpQuiz
    
    DELETE #tmpQuiz
    DELETE #tmpSubjectAndExams
    
    SET @Index = @Index + 1
    
    FETCH NEXT FROM CUR INTO @varSubdirectory, @varDepth, @varFile
END


CLOSE CUR
DEALLOCATE CUR

If(OBJECT_ID('tempdb..#tmpFiles') Is Not Null)
Begin
    Drop Table #tmpFiles
End

If(OBJECT_ID('tempdb..#tmpSubjectAndExams') Is Not Null)
Begin
    Drop Table #tmpSubjectAndExams
End

If(OBJECT_ID('tempdb..#tmpQuiz') Is Not Null)
Begin
    Drop Table #tmpQuiz
End