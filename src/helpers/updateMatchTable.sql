use bwf_api;

-- select * from `match` limit 10;

-- update `match` set WinnerPoints = 
-- 	(
--     select sum(`set`.WinnerScore) from `set` 
--     where `match`.WinnerId = `set`.WinnerId 
-- 		and `match`.LoserId = `set`.LoserId 
-- 		and `match`.TournamentId = `set`.TournamentId
-- 	group by `set`.WinnerId, `set`.LoserId, `set`.TournamentId
--     );

-- update `match` set LoserPoints = 
-- 	(
-- 	select sum(`set`.LoserScore) from `set` 
--     where `match`.WinnerId = `set`.WinnerId 
-- 		and `match`.LoserId = `set`.LoserId 
-- 		and `match`.TournamentId = `set`.TournamentId
-- 	group by `set`.WinnerId, `set`.LoserId, `set`.TournamentId
--     );

-- update `match` set SetCount = 
-- 	(
--     select count(`set`.WinnerId) from `set`
--     where `match`.WinnerId = `set`.WinnerId 
-- 		and `match`.LoserId = `set`.LoserId 
-- 		and `match`.TournamentId = `set`.TournamentId
-- 	group by `set`.WinnerId, `set`.LoserId, `set`.TournamentId
--     );

-- update `match` set StartDate = 
-- 	(
--     select `tournament`.StartDate from `tournament`
--     where `tournament`.Id = `match`.TournamentId 
--     );
    