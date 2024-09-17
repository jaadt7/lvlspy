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
    T = 0
    p = s.compute_equilibrium_probabilities(T)
    assert p[0] == 1.0
    assert p[1] == 0.0
    T = 1e7
    p = s.compute_equilibrium_probabilities(T)
    assert p[0] == 1.0
    T = 1.0e9
    p = s.compute_equilibrium_probabilities(T)
    assert p[0] < 1.0


def test_levels():
    coll = get_collection()
    s = coll.get()["al26"]
    levels = s.get_levels()
    number_levels = len(levels)
    level = levels[0]
    s.add_level(level)
    assert len(s.get_levels()) == number_levels


def test_transitions():
    coll = get_collection()
    s = coll.get()["al26"]
    levels = s.get_levels()
    assert len(s.get_lower_linked_levels(levels[0])) == 0
    assert len(s.get_upper_linked_levels(levels[0])) > 0
    assert len(s.get_lower_linked_levels(levels[len(levels) - 1])) > 0
    assert len(s.get_upper_linked_levels(levels[len(levels) - 1])) == 0
    transitions = s.get_transitions()
    number_transitions = len(transitions)
    transition = transitions[0]
    s.add_transition(transition)
    assert len(s.get_transitions()) == number_transitions


def test_einstein():
    coll = get_collection()
    s = coll.get()["al26"]
    levs = s.get_levels()
    trans = s.get_level_to_level_transition(levs[1], levs[0])
    upper = trans.get_upper_level()
    lower = trans.get_lower_level()
    ein_a = trans.get_einstein_a()
    s.remove_transition(trans)
    s.add_transition(lt.Transition(upper, lower, ein_a))
    trans = s.get_level_to_level_transition(levs[1], levs[0])
    assert trans.get_einstein_a() == 3.83356e-17
    assert trans.get_einstein_b_upper_to_lower() == 1.5454261181603054e-29
    assert trans.get_einstein_b_lower_to_upper() == 1.4049328346911867e-30

    trans.update_einstein_a(1)
    assert trans.get_einstein_a() == 1

    assert s.get_level_to_level_transition(levs[0], levs[1]) == None


def test_rates():
    def user_rate(temperature):
        return 2.0 * temperature

    coll = get_collection()
    s = coll.get()["al26"]
    levs = s.get_levels()
    trans = s.get_level_to_level_transition(levs[1], levs[0])
    assert trans.compute_lower_to_upper_rate(
        1.0e9
    ) < trans.compute_upper_to_lower_rate(1.0e9)

    assert trans.compute_lower_to_upper_rate(
        1.0e9, user_func=user_rate
    ) == trans.compute_upper_to_lower_rate(1.0e9, user_func=user_rate)


def test_frequency():
    coll = get_collection()
    s = coll.get()["al26"]
    levs = s.get_levels()
    trans = s.get_level_to_level_transition(levs[1], levs[0])
    assert trans.get_frequency() == 5.520390824072181e19


def test_write_xml():
    coll = get_collection()
    assert coll.write_to_xml("out.xml") == None
