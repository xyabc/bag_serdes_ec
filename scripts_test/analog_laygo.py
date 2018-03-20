# -*- coding: utf-8 -*-

from typing import Dict, Any, Set

import yaml

from bag.core import BagProject
from bag.layout.routing import RoutingGrid
from bag.layout.template import TemplateDB

from abs_templates_ec.laygo.core import LaygoBase

from serdes_ec.layout.qdr_hybrid.amp import IntegAmp


class LaygoDummy(LaygoBase):
    """A dummy laygo cell to test AnalogBase-LaygoBase pitch matching.

    Parameters
    ----------
    temp_db : TemplateDB
            the template database.
    lib_name : str
        the layout library name.
    params : Dict[str, Any]
        the parameter values.
    used_names : Set[str]
        a set of already used cell names.
    **kwargs :
        dictionary of optional parameters.  See documentation of
        :class:`bag.layout.template.TemplateBase` for details.
    """

    def __init__(self, temp_db, lib_name, params, used_names, **kwargs):
        # type: (TemplateDB, str, Dict[str, Any], Set[str], **kwargs) -> None
        LaygoBase.__init__(self, temp_db, lib_name, params, used_names, **kwargs)
        self._sch_params = None

    @property
    def sch_params(self):
        # type: () -> Dict[str, Any]
        return self._sch_params

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        return dict(
            config='laygo configuration dictionary.',
            row_layout_info='The AnalogBase information dictionary.',
            num_col='Number of laygo olumns.'
        )

    def draw_layout(self):
        row_layout_info = self.params['row_layout_info']
        num_col = self.params['num_col']

        if num_col is None:
            raise ValueError('num_col must be a positive integer.')

        self.set_rows_direct(row_layout_info, num_col=num_col)
        self.fill_space()


def make_tdb(prj, target_lib, specs):
    grid_specs = specs['routing_grid']
    layers = grid_specs['layers']
    widths = grid_specs['widths']
    spaces = grid_specs['spaces']
    bot_dir = grid_specs['bot_dir']
    width_override = grid_specs.get('width_override', None)

    routing_grid = RoutingGrid(prj.tech_info, layers, spaces, widths, bot_dir,
                               width_override=width_override)
    tdb = TemplateDB('template_libs.def', routing_grid, target_lib, use_cybagoa=True)
    return tdb


def generate(prj, specs):
    impl_lib = specs['impl_lib']
    impl_cell = specs['impl_cell']
    params = specs['params']
    laygo_params = specs['laygo_params']

    temp_db = make_tdb(prj, impl_lib, specs)

    name_list = [impl_cell, impl_cell + '_LAYGO']
    temp1 = temp_db.new_template(params=params, temp_cls=IntegAmp, debug=False)

    laygo_params['row_layout_info'] = temp1.row_layout_info
    temp2 = temp_db.new_template(params=laygo_params, temp_cls=LaygoDummy, debug=False)

    temp_list = [temp1, temp2]
    print('creating layout')
    temp_db.batch_layout(prj, temp_list, name_list)
    print('layout done')


if __name__ == '__main__':
    with open('specs_test/analog_laygo.yaml', 'r') as f:
        block_specs = yaml.load(f)

    local_dict = locals()
    if 'bprj' not in local_dict:
        print('creating BAG project')
        bprj = BagProject()

    else:
        print('loading BAG project')
        bprj = local_dict['bprj']

    generate(bprj, block_specs)
