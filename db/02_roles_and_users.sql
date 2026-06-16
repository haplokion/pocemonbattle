DECLARE
    role_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO role_exists FROM dba_roles WHERE role = 'GAME_PLAYER_ROLE';
    IF role_exists = 0 THEN
        EXECUTE IMMEDIATE 'CREATE ROLE GAME_PLAYER_ROLE';
    END IF;
END;
/