private _path = "\userconfig\gc_server_briefing.hpp";
if (fileExists _path) then {
    call compile preprocessFileLineNumbers _path;
    [[GC_BRIEFING_TITLE, GC_BRIEFING_ARRAY], {
        [{!isNull player}, {
            _this params [
                ["_title", "Server Briefing", [""]],
                ["_array", [], [[]]]
            ];
            player createDiarySubject ["GC_SERVER_BRIEFING", _title];
            _array apply {
                player createDiaryRecord ["GC_SERVER_BRIEFING", _x];
            };
        }, _this] call CBA_fnc_waitUntilAndExecute;
    }] remoteExec ["BIS_fnc_call", 0, true];
} else {
    diag_log format ["Server Briefing file (%1) does not exist!", _path]
};