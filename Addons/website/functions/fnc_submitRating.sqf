#include "script_component.hpp"

params [
	["_message", "", [""]],
	["_unit", objNull, [objNull]]
];

if (_message isEqualTo "" || _unit isEqualTo objNull) exitWith {};

private _thread_id = ["gc_websitefunctions.call_submit_rating", [_message, getPlayerUID _unit, missionName]] call py3_fnc_callExtension;
private _has_call_finished = ["gc_websitefunctions.has_call_finished", [_thread_id]] call py3_fnc_callExtension;

[{
	params ["_args", "_pfhID"];
	_args params ["_thread_id", "_has_call_finished", "_unit"];
	if (_has_call_finished) then {
		private _value = ["gc_websitefunctions.get_call_value", [_thread_id]] call py3_fnc_callExtension;
		["gc_ratingResponse", [_value], _unit] call CBA_fnc_targetEvent;
		[_pfhID] call CBA_fnc_removePerFrameHandler;
	} else {
		private _has_call_finished_pfh = ["gc_websitefunctions.has_call_finished", [_thread_id]] call py3_fnc_callExtension;
		if (_has_call_finished_pfh) then {
			private _value = ["gc_websitefunctions.get_call_value", [_thread_id]] call py3_fnc_callExtension;
			["gc_ratingResponse", [_value], _unit] call CBA_fnc_targetEvent;
			[_pfhID] call CBA_fnc_removePerFrameHandler;
		};
	}
}, 2, [_thread_id, _has_call_finished, _unit] ] call CBA_fnc_addPerFrameHandler;