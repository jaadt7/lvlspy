import requests, io
import lvlspy.level as lv
import lvlspy.spcoll as lc
import lvlspy.species as ls
import lvlspy.transition as lt


def get_collection():
    test_coll = lc.SpColl()
    test_coll.update_from_xml(
        io.BytesIO(requests.get("https://osf.io/dqzs9/download").content)
    )
    return test_coll


def test_validation():
    test_coll = lc.SpColl()
    assert (
        test_coll.validate(
            io.BytesIO(requests.get("https://osf.io/dqzs9/download").content)
        )
        == None
    )


def test_species():
    coll = get_collection()
    assert "al26" in coll.get() and "al27" in coll.get()


def test_energy_and_multiplicity():
    coll = get_collection()
    s = coll.get()["al26"]
    levs = s.get_levels()
    assert levs[0].get_energy() == 0.0
    assert levs[0].get_multiplicity() == 11


def test_probability():
    coll = get_collection()
    s = coll.get()["al26"]
    T = 1e7
    p = s.compute_equilibrium_probabilities(T)
    assert p[0] == 1.0

def test_transitions():
    coll = get_collection()
    s = coll.get()["al26"]
    levels = s.get_levels()
    upwards = s.get_upward_transitions_from_level(levels[0])
    assert len(upwards) > 0
    downwards = s.get_downward_transitions_from_level(levels[len(levels)-1])
    assert len(downwards) > 0

def test_einstein():
    coll = get_collection()
    s = coll.get()["al26"]
    levs = s.get_levels()
    for _trans in s.get_transitions():
        i_upper = levs.index(_trans.get_upper_level())
        i_lower = levs.index(_trans.get_lower_level())
        if i_upper == 1 and i_lower == 0:
            upper = _trans.get_upper_level()
            lower = _trans.get_lower_level()
            ein_a = _trans.get_einstein_a()
            s.remove_transition(_trans)
            s.add_transition(lt.Transition(upper, lower, ein_a))
            assert _trans.get_einstein_a() == 3.83356e-17
            assert _trans.get_einstein_b_upper_to_lower() == 1.5454261181603054e-29
            assert _trans.get_einstein_b_lower_to_upper() == 1.4049328346911867e-30

            _trans.update_einstein_a(1)
            assert _trans.get_einstein_a() == 1
            break


def test_frequency():
    coll = get_collection()
    s = coll.get()["al26"]
    levs = s.get_levels()
    trans = s.get_transitions()
    for _trans in trans:
        i_upper = levs.index(_trans.get_upper_level())
        i_lower = levs.index(_trans.get_lower_level())
        if i_upper == 1 and i_lower == 0:
            assert _trans.get_frequency() == 5.520390824072181e19
            break

def test_write_xml():
    coll = get_collection()
    assert coll.write_to_xml('out.xml') == None
