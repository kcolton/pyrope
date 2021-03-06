import re

from pyrope.exceptions import PropertyParsingError


class PropertyMapper:
    def __init__(self, netcache):
        self._netcache = netcache
        self._archtype_to_prop = {}

    def get_property_name(self, archtype, prop_id):
        if archtype not in self._archtype_to_prop:
            self._archtype_to_prop[archtype] = self._build_prop_for_archtype(archtype)
        return self._archtype_to_prop[archtype][prop_id]

    def get_property_max_id(self, archtype):
        if archtype not in self._archtype_to_prop:
            self._archtype_to_prop[archtype] = self._build_prop_for_archtype(archtype)
        return max(self._archtype_to_prop[archtype].keys())

    def _build_prop_for_archtype(self, archtype):
        classname = self._arch_to_class(archtype)
        result, mapping = self._get_netprops_for_class(self._netcache, classname)
        if not result:
            msg = "Could not find Property Ids for " \
                  "archtype %s with classname %s" % (archtype, classname)
            raise PropertyParsingError(msg)
        return mapping

    def _arch_to_class(self, archname):
        if archname == 'GameInfo_Soccar.GameInfo.GameInfo_Soccar:GameReplicationInfoArchetype':
            classname = 'TAGame.GRI_TA'
        elif archname == 'GameInfo_Season.GameInfo.GameInfo_Season:GameReplicationInfoArchetype':
            classname = 'TAGame.GRI_TA'
        elif archname == 'Archetypes.GameEvent.GameEvent_Season:CarArchetype':
            classname = 'TAGame.Car_Season_TA'
        elif archname == 'Archetypes.Ball.CubeBall' or archname == 'Archetypes.Ball.Ball_Puck':
            classname = 'TAGame.Ball_TA'
        else:
            classname = re.sub('_\d+', '', archname).split('.')[-1].split(':')[-1]
            classname = classname.replace("_Default", "_TA") \
                .replace("Archetype", "") \
                .replace("_0", "") \
                .replace("0", "_TA") \
                .replace("1", "_TA") \
                .replace("Default__", "")
            classname = '.' + classname
        return classname

    def _get_netprops_for_class(self, netcache, classname):
        """
        Recursively search netcache Tree for our class. When netcache is found return Mapping of
        each netcache we traversed to that point. The Boolean return is a workaround in case
        the found netcache has an empty mapping there may be a better way to do that. But for now
        I'm glad as fuck that shit actually works. I should have used some kind of tree librarie
        here or a defaultdict or whatever. But its a once per classname thing, so yeah
        """
        mappings = {}
        for k, v in netcache.items():
            if type(k) == str and classname in k:
                return True, v['mapping']
            if type(v) == dict and v != 'mappings':
                result, child_map = self._get_netprops_for_class(v, classname)
                if result:
                    mappings.update(v['mapping'])
                    mappings.update(child_map)
                    return True, mappings
        return False, mappings
