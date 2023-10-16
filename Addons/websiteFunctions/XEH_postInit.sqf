#include "script_component.hpp"

["gc_onSubmitReview", {
	params ["_message", "_player"]; 
	[_message, _player] call FUNC(submitReview);
}] call CBA_fnc_addEventHandler;

["gc_onSubmitBugReport", {
	params ["_message", "_player"]; 
	[_message, _player] call FUNC(submitBugReport);
}] call CBA_fnc_addEventHandler;

["gc_onSubmitRating", {
	params ["_message", "_player"]; 
	[_message, _player] call FUNC(submitRating);
}] call CBA_fnc_addEventHandler;

["gc_onGetBugReports", {
	params ["_player"]; 
	[_player] call FUNC(getBugReports);
}] call CBA_fnc_addEventHandler;