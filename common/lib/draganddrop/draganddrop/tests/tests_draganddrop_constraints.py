# -*- coding: utf-8 -*-
"""Tests for DnD constraints."""

import unittest
import json

from ..draganddrop_constraints import get_all_dragabbles, BadProperty
from ..draganddrop_rules import grade


class TestDragAndDropConstraints(unittest.TestCase):
    """Tests for DnD constraints."""
    def test_grid_correct(self):
        xml = """
        <customresponse>
            <text>
                <h4>Babies and Sun</h4><br/>
                <h4>Drag two babies and one sun. All babies must be under the sun.</h4>
                <br/>
            </text>

            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />
                <draggable id="sun" icon="/static/images/grid_test/sun.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="600" h="600" col="30" row="30"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
        dragabbles = draganddrop.get_all_dragabbles(submission[0], xml)

        constraints = [
            dragabbles['sun'].count == 1,
            dragabbles['baby'].count == 2,
            dragabbles['sun'].on('base_target')[0].y < dragabbles['baby'].on('base_target')[0].y,
            dragabbles['sun'].on('base_target')[0].y < dragabbles['baby'].on('base_target')[1].y
        ]

        if all(constraints):
            correct = ['correct']
        else:
            correct = ['incorrect']
        ]]>
            </answer>
        </customresponse>
        """

        correct_answer = [
            {
                'draggables': ['sun', 'baby'],
                'targets': [
                    'base_target'
                ],
                'rule': 'anyof'
            }
        ]

        constraints_raw = """[
            dragabbles['sun'].count == 1,
            dragabbles['baby'].count == 2,
            dragabbles['sun'].on('base_target')[0].y <
                dragabbles['baby'].on('base_target')[0].y,
            dragabbles['sun'].on('base_target')[0].y <
                dragabbles['baby'].on('base_target')[1].y
        ]"""

        # Correct
        user_input = json.dumps([
            {'sun': 'base_target{2}{2}'},
            {'baby': 'base_target{5}{10}'},
            {'baby': 'base_target{20}{20}'}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(all(eval(constraints_raw)))
        self.assertTrue(grade(user_input, correct_answer))

        self.assertEqual(dragabbles['sun'].on('base_target')[0].x, 55)
        self.assertEqual(dragabbles['sun'].on('base_target')[0].y, 55)

        self.assertEqual(dragabbles['baby'].on('base_target')[0].x, 115)
        self.assertEqual(dragabbles['baby'].on('base_target')[0].y, 215)

        self.assertEqual(dragabbles['baby'].on('base_target')[1].x, 415)
        self.assertEqual(dragabbles['baby'].on('base_target')[1].y, 415)

        # Correct (change order)
        user_input = json.dumps([
            {'sun': 'base_target{2}{2}'},
            {'baby': 'base_target{20}{20}'},
            {'baby': 'base_target{5}{10}'}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(all(eval(constraints_raw)))
        self.assertTrue(grade(user_input, correct_answer))

        self.assertEqual(dragabbles['sun'].on('base_target')[0].x, 55)
        self.assertEqual(dragabbles['sun'].on('base_target')[0].y, 55)

        self.assertEqual(dragabbles['baby'].on('base_target')[0].x, 115)
        self.assertEqual(dragabbles['baby'].on('base_target')[0].y, 215)

        self.assertEqual(dragabbles['baby'].on('base_target')[1].x, 415)
        self.assertEqual(dragabbles['baby'].on('base_target')[1].y, 415)

    def test_grid_fail(self):
        xml = """
        <customresponse>
            <text>
                <h4>Babies and Sun</h4><br/>
                <h4>Drag two babies and one sun. All babies must be under the sun.</h4>
                <br/>
            </text>

            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />
                <draggable id="sun" icon="/static/images/grid_test/sun.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="600" h="600" col="30" row="30"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
        dragabbles = draganddrop.get_all_dragabbles(submission[0], xml)

        constraints = [
            dragabbles['sun'].count == 1,
            dragabbles['baby'].count == 2,
            dragabbles['sun'].on('base_target')[0].y < dragabbles['baby'].on('base_target')[0].y,
            dragabbles['sun'].on('base_target')[0].y < dragabbles['baby'].on('base_target')[1].y
        ]

        if all(constraints):
            correct = ['correct']
        else:
            correct = ['incorrect']
        ]]>
            </answer>
        </customresponse>
        """

        def run_constraints(dragabbles):
            """Execute constraints."""
            constraints_raw = [
                dragabbles['sun'].count == 1,
                dragabbles['baby'].count == 2,
                dragabbles['sun'].on('base_target')[0].y <
                dragabbles['baby'].on('base_target')[0].y,
                dragabbles['sun'].on('base_target')[0].y <
                dragabbles['baby'].on('base_target')[1].y
            ]
            return all(constraints_raw)

        # Correct
        user_input = json.dumps([
            {'sun': 'base_target{2}{2}'},
            {'baby': 'base_target{5}{10}'},
            {'baby': 'base_target{20}{20}'}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)
        self.assertTrue(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'sun': 'base_target{2}{2}'},
            {'baby': 'base_target{20}{20}'}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'baby': 'base_target{5}{10}'},
            {'baby': 'base_target{20}{20}'}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'sun': 'base_target{2}{2}'},
            {'sun': 'base_target{2}{5}'},
            {'baby': 'base_target{5}{10}'},
            {'baby': 'base_target{20}{20}'}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'sun': 'base_target{2}{11}'},
            {'baby': 'base_target{5}{10}'},
            {'baby': 'base_target{20}{20}'}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

    def test_grid_division_not_evenly(self):
        xml = """
        <customresponse>
            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="100" h="100" col="8" row="8"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
                correct = ['correct']
            ]]>
            </answer>
        </customresponse>
        """

        user_input = json.dumps([
            {'baby': 'base_target{5}{8}'},
            {'baby': 'base_target{6}{10}'},
            {'baby': 'base_target{0}{0}'},
            {'baby': 'base_target{1}{1}'},
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertEqual(dragabbles['baby'][0].x, 11.25)
        self.assertEqual(dragabbles['baby'][1].x, 23.75)
        self.assertEqual(dragabbles['baby'][2].x, 73.75)
        self.assertEqual(dragabbles['baby'][3].x, 86.25)

    def test_constraints_nested_draggables(self):
        xml = """
        <customresponse>
            <text>
                <h4>Babies and Sun</h4><br/>
                <h4>Drag exactly two babies or two sun on the house.</h4>
                <br/>
            </text>

            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="house" icon="/static/images/grid_test/house.png" can_reuse="true">
                    <target id="1" x="0" y="0" w="32" h="32"/>
                    <target id="2" x="34" y="0" w="32" h="32"/>
                    <target id="3" x="68" y="0" w="32" h="32"/>
                </draggable>

                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />
                <draggable id="sun" icon="/static/images/grid_test/sun.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="600" h="600" col="30" row="30"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
        dragabbles = draganddrop.get_all_dragabbles(submission[0], xml)

        constraints = [
            dragabbles['house'].count == 1,
            dragabbles['sun'].count == 2 or dragabbles['baby'].count == 2
        ]

        if all(constraints):
            correct = ['correct']
        else:
            correct = ['incorrect']
        ]]>
            </answer>
        </customresponse>
        """

        correct_answer = [
            {
                'draggables': ['house'],
                'targets': ['base_target'],
                'rule': 'exact'
            },
            {
                'draggables': ['sun', 'baby'],
                'targets': [
                    'base_target[house][1]', 'base_target[house][2]', 'base_target[house][3]'
                ],
                'rule': 'anyof'
            }
        ]

        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}},
            {'baby': {'2': {'house': 'base_target'}}},
            {'sun': {'3': {'house': 'base_target'}}}
        ])

        def run_constraints(dragabbles):
            """Execute constraints."""
            constraints_raw = [
                dragabbles['house'].count == 1,
                dragabbles['sun'].count == 2 or dragabbles['baby'].count == 2
            ]
            return all(constraints_raw)

        dragabbles = get_all_dragabbles(user_input, xml)
        self.assertTrue(run_constraints(dragabbles))
        self.assertTrue(grade(user_input, correct_answer))

    def test_constraints_contains(self):
        xml = """
        <customresponse>
            <text>
                <h4>Babies and Sun</h4><br/>
                <h4>Drag exactly two babies or two sun on the house.</h4>
                <br/>
            </text>

            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="house" icon="/static/images/grid_test/house.png" can_reuse="true">
                    <target id="1" x="0" y="0" w="32" h="32"/>
                    <target id="2" x="34" y="0" w="32" h="32"/>
                    <target id="3" x="68" y="0" w="32" h="32"/>
                </draggable>

                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />
                <draggable id="sun" icon="/static/images/grid_test/sun.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="600" h="600" col="30" row="30"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
        dragabbles = draganddrop.get_all_dragabbles(submission[0], xml)

        constraints = [
            dragabbles['house'].count == 1,
            dragabbles['sun'].count == 2 or dragabbles['baby'].count == 2,
            dragabbles['house'].on('base_target')[0].contains('sun', 'sun') or
            dragabbles['house'].on('base_target')[0].contains('baby', 'baby')
        ]

        if all(constraints):
            correct = ['correct']
        else:
            correct = ['incorrect']
        ]]>
            </answer>
        </customresponse>
        """

        def run_constraints(dragabbles):
            """Execute constraints."""
            constraints_raw = [
                dragabbles['house'].count == 1,
                dragabbles['sun'].count == 2 or dragabbles['baby'].count == 2,
                dragabbles['house'].on('base_target')[0].contains('sun', 'sun') or
                dragabbles['house'].on('base_target')[0].contains('baby', 'baby')
            ]
            return all(constraints_raw)

        # Correct
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}},
            {'baby': {'2': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(run_constraints(dragabbles))

        # Correct
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}},
            {'baby': {'3': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(run_constraints(dragabbles))

        # Correct
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'3': {'house': 'base_target'}}},
            {'baby': {'1': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        # Correct
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'sun': {'3': {'house': 'base_target'}}},
            {'sun': {'1': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'sun': {'1': {'house': 'base_target'}}},
            {'sun': {'2': {'house': 'base_target'}}},
            {'sun': {'3': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}},
            {'baby': {'2': {'house': 'base_target'}}},
            {'sun': {'3': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}},
            {'sun': {'2': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

    def test_constraints_for_bad_draggables(self):
        xml = """
        <customresponse>
            <text>
                <h4>Babies and Sun</h4><br/>
                <h4>Drag exactly two babies or two sun on the house.</h4>
                <br/>
            </text>

            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="house" icon="/static/images/grid_test/house.png" can_reuse="true">
                    <target id="1" x="0" y="0" w="32" h="32"/>
                    <target id="2" x="34" y="0" w="32" h="32"/>
                    <target id="3" x="68" y="0" w="32" h="32"/>
                </draggable>

                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />
                <draggable id="sun" icon="/static/images/grid_test/sun.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="600" h="600" col="30" row="30"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
        correct = ['correct']
        ]]>
            </answer>
        </customresponse>
        """

        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}},
            {'baby': {'2': {'house': 'base_target'}}}
        ])

        dragabbles = get_all_dragabbles(user_input, xml)
        constraints_raw = [
            dragabbles['BAD_sun'].count == 2
        ]
        self.assertFalse(all(constraints_raw))

        dragabbles = get_all_dragabbles(user_input, xml)
        constraints_raw = [
            dragabbles['house'].on('BAD_base_target')[0].contains('BAD_sun', 'BAD_sun')
        ]
        self.assertFalse(all(constraints_raw))

    def test_constraints_contains_exact(self):
        xml = """
        <customresponse>
            <text>
                <h4>Babies and Sun</h4><br/>
                <h4>Drag exactly two babies or two sun on the house.</h4>
                <br/>
            </text>

            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="house" icon="/static/images/grid_test/house.png" can_reuse="true">
                    <target id="1" x="0" y="0" w="32" h="32"/>
                    <target id="2" x="34" y="0" w="32" h="32"/>
                    <target id="3" x="68" y="0" w="32" h="32"/>
                </draggable>

                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />
                <draggable id="sun" icon="/static/images/grid_test/sun.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="600" h="600" col="30" row="30"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
        dragabbles = draganddrop.get_all_dragabbles(submission[0], xml)

        constraints = [
            dragabbles['house'].count == 1,
            dragabbles['house'].on('base_target')[0].contains('sun', 'sun', exact=False) or
            dragabbles['house'].on('base_target')[0].contains('baby', 'baby')
        ]

        if all(constraints):
            correct = ['correct']
        else:
            correct = ['incorrect']
        ]]>
            </answer>
        </customresponse>
        """

        def run_constraints(dragabbles):
            """Execute constraints."""
            constraints_raw = [
                dragabbles['house'].count == 1,
                dragabbles['house'].on('base_target')[0].contains('sun', 'sun', exact=False) or
                dragabbles['house'].on('base_target')[0].contains('baby', 'baby')
            ]
            return all(constraints_raw)

        # Correct
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'sun': {'1': {'house': 'base_target'}}},
            {'sun': {'2': {'house': 'base_target'}}},
            {'baby': {'3': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(run_constraints(dragabbles))

        # Correct
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'sun': {'1': {'house': 'base_target'}}},
            {'sun': {'2': {'house': 'base_target'}}},
            {'sun': {'3': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(run_constraints(dragabbles))

        # Correct
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}},
            {'baby': {'2': {'house': 'base_target'}}},
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertTrue(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'sun': {'1': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        # Fail
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'baby': {'1': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

        # Fail
        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'sun': {'1': {'house': 'base_target'}}},
            {'baby': {'3': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertFalse(run_constraints(dragabbles))

    def test_draggables_order(self):
        xml = """
        <customresponse>
            <drag_and_drop_input img="/static/images/grid_test/610x610_blank.png" target_outline="true" >
                <draggable id="house" icon="/static/images/grid_test/house.png" can_reuse="true">
                    <target id="1" x="0" y="0" w="32" h="32"/>
                    <target id="2" x="34" y="0" w="32" h="32"/>
                    <target id="3" x="68" y="0" w="32" h="32"/>
                </draggable>

                <draggable id="baby" icon="/static/images/grid_test/baby.png" can_reuse="true" />
                <draggable id="sun" icon="/static/images/grid_test/sun.png" can_reuse="true" />

                <target id="base_target" type="grid" x="5" y="5" w="600" h="600" col="30" row="30"/>
            </drag_and_drop_input>

            <answer type="loncapa/python"><![CDATA[
                correct = ['correct']
            ]]>
            </answer>
        </customresponse>
        """

        user_input = json.dumps([
            {'house': 'base_target{5}{10}'},
            {'house': 'base_target{6}{10}'},
            {'house': 'base_target{2}{10}'},
            {'house': 'base_target{1}{5}'},
            {'house': 'base_target{27}{1}'},
            {'house': 'base_target{4}{1}'},
            {'house': 'base_target{10}{10}'},
            {'sun': {'1': {'house': 'base_target'}}},
            {'sun': {'2': {'house': 'base_target'}}},
            {'baby': {'3': {'house': 'base_target'}}}
        ])
        dragabbles = get_all_dragabbles(user_input, xml)

        self.assertEqual(dragabbles['house'].count, 7)

        self.assertEqual(dragabbles['house'][0].y, 35)
        self.assertEqual(dragabbles['house'][0].x, 95)

        self.assertEqual(dragabbles['house'][1].y, 35)
        self.assertEqual(dragabbles['house'][1].x, 555)

        self.assertEqual(dragabbles['house'][2].y, 115)
        self.assertEqual(dragabbles['house'][2].x, 35)

        self.assertEqual(dragabbles['house'][3].y, 215)
        self.assertEqual(dragabbles['house'][3].x, 55)

        self.assertEqual(dragabbles['house'][4].y, 215)
        self.assertEqual(dragabbles['house'][4].x, 115)

        self.assertEqual(dragabbles['house'][5].y, 215)
        self.assertEqual(dragabbles['house'][5].x, 135)

        self.assertEqual(dragabbles['house'][6].y, 215)
        self.assertEqual(dragabbles['house'][6].x, 215)


class TestDragAndDropConstraintsBadProperty(unittest.TestCase):
    """Tests for `BadProperty` behavoiur."""
    def test_bad_property(self):
        first_obj = BadProperty()
        second_obj = BadProperty()
        self.assertFalse(first_obj == second_obj)
        self.assertFalse(first_obj != second_obj)
        self.assertFalse(first_obj < second_obj)
        self.assertFalse(first_obj > second_obj)
        self.assertFalse(first_obj <= second_obj)
        self.assertFalse(first_obj >= second_obj)
