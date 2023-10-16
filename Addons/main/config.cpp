#include "script_component.hpp"

class CfgPatches {
	class ADDON {
		author = "Global Conflicts";
		name = QUOTE(ADDON);
		requiredVersion = 1.0;
		requiredAddons[] = {"A3_Ui_F", "cba_main"};
		units[] = {};
		weapons[] = {};
	};
};

class CfgMods {
    class PREFIX {
        dir = "@serverSide";
        name = "Global Conflicts Serverside Addons";
        picture = "A3\Ui_f\data\Logos\arma3_expansion_alpha_ca";
        hidePicture = "true";
        hideName = "true";
        actionName = "Website";
        action = "https://www.globalconflicts.net/";
        description = "Issue Tracker: https://github.com/Global-Conflicts-ArmA/serverAddons/issues";
    };
};