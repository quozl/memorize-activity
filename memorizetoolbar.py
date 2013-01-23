#    Copyright (C) 2006, 2007, 2008 One Laptop Per Child
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

from gi.repository import GObject
from os.path import join, dirname

from gettext import gettext as _
from sugar.graphics.toolbutton import ToolButton
from sugar.graphics.toolcombobox import ToolComboBox
from sugar.graphics.alert import Alert
from sugar.graphics.icon import Icon
from sugar.activity.widgets import RadioMenuButton
from sugar.graphics.menuitem import MenuItem

import logging
from gobject import SIGNAL_RUN_FIRST, TYPE_PYOBJECT

_logger = logging.getLogger('memorize-activity')


class MemorizeToolbarBuilder(GObject.GObject):

    __gtype_name__ = 'MemoryToolbarBuilder'

    standard_game_names = ['addition',
                           'letters',
                           'sounds'
                           ]
    translated_game_names = [_('Addition'),
                             _('Letters'),
                             _('Sounds')
                            ]

    __gsignals__ = {
    'game_changed': (SIGNAL_RUN_FIRST, None, 5 * [TYPE_PYOBJECT])
    }

    def __init__(self, activity):
        GObject.GObject.__init__(self)
        self.activity = activity
        self.toolbar = self.activity.get_toolbar_box().toolbar
        self.jobject = None

        # Change demo games button
        self._demo_games = RadioMenuButton(icon_name='memorize-collection')
        self._demo_games.props.tooltip = _('Load demo games')

        for i, game in enumerate(self.translated_game_names):
            menu_item = MenuItem(game, icon_name=self.standard_game_names[i])
            menu_item.connect('activate', self.__activate_game_cb, i)
            self._demo_games.props.palette.menu.append(menu_item)
            menu_item.show()
        self.toolbar.insert(self._demo_games, -1)
        self._selected_game = self.standard_game_names[0]

        # Change size combobox
        self._size_combo = RadioMenuButton(icon_name='change_size')
        self._size_combo.props.tooltip = _('Change size')
        self._sizes = ['4 X 4', '5 X 5', '6 X 6']

        for i, f in enumerate(self._sizes):
            menu_item = MenuItem(f, icon_name=self._sizes[i])
            menu_item.connect('activate', self._game_size_cb, i)
            self._size_combo.props.palette.menu.append(menu_item)
            menu_item.show()
        self.toolbar.insert(self._size_combo, -1)
        self._selected_game_size = self._sizes[0][0]

        # Reset Button
        self._restart_button = ToolButton('game-new')
        self._restart_button.connect('clicked', self._game_reset_cb)
        self._restart_button.set_tooltip(_('Restart Game'))
        self.toolbar.insert(self._restart_button, -1)
        self._restart_button.show()

    def _game_reset_cb(self, widget):
        self.activity.game.model.count = 0
        self.emit('game_changed', None, None, 'reset', None, None)

    def update_controls(self, active):
        self._size_combo.set_sensitive(active)
        self._demo_games.set_sensitive(active)
        self._restart_button.set_sensitive(active)

    def _game_size_cb(self, widget, i):
        self._selected_game_size = int(self._sizes[i][0])
        self._size_combo.props.icon_name = self._sizes[i]
        self.emit('game_changed', None, self._selected_game_size, 'size', None,
                None)

    def __activate_game_cb(self, menu, i):
        self._game_selected_index = i
        if self.activity.game.model.is_demo:
            self._change_game()
        else:
            alert = Alert()
            alert.props.title = _('Discard your modified game?')
            icon = Icon(icon_name='dialog-ok')
            alert.add_button(1, _('Discard'), icon)
            icon = Icon(icon_name='dialog-cancel')
            alert.add_button(0, _('Do not discard'), icon)
            alert.connect('response', self._change_game_alert_cb)
            self.activity.add_alert(alert)

    def _change_game_alert_cb(self, alert, response_id):
        if alert is not None:
            self.activity.remove_alert(alert)
        if response_id == 1:
            self._change_game()

    def _change_game(self):
        title = self.translated_game_names[self._game_selected_index]
        game_size = int(self._selected_game_size)

        game_name = self.standard_game_names[self._game_selected_index]
        self._demo_games.props.icon_name = game_name
        game_file = join(dirname(__file__), 'demos', game_name + '.zip')
        self.emit('game_changed', game_file, game_size, 'demo', title, None)

    def reset(self, widget):
        self._demo_games.props.icon_name = 'memorize-collection'

    def update_toolbar(self, widget, data, grid):
        size = data.get('size')
        self._size_combo.props.icon_name = size + ' X ' + size
