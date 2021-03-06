# -*- coding: utf-8 -*-
# Copyright (C) 2011-2013 by Florian Mounier, Kozea
# This file is part of pystil, licensed under a 3-clause BSD license.

from datetime import date, timedelta
from pystil.utils import on, between, parse_referrer
from pystil.context import Hdr, url
from pystil.db import Visit, count, distinct
from pystil.i18n import labelize, titlize
from sqlalchemy import desc, func
from pygal.style import Style
from pygal.util import cut
import pygal


PystilStyle = Style(
    background='transparent',
    plot_background='rgba(255, 255, 255, .2)',
    foreground='#73716a',
    foreground_dark='#73716a',
    foreground_light='#be3e3a',
    opacity='.4',
    opacity_hover='.6',
    transition='500ms',
    colors=(
        "#ca4869",
        "#a54ca1",
        "#504ca5",
        "#4a80ad",
        "#49b4b0",
        "#4ca55d",
        "#a6af44",
        "#eac516",
        "#ea9316",
        "#bb6120",
        "#951313"
    ))


class Chart(object):
    def __init__(self, db, site, criteria, from_date, to_date, host, lang):
        self.db = db
        self.site = site
        self.lang = lang
        self.from_date = from_date
        self.to_date = to_date
        self.table = Visit.__table__
        self.criteria = getattr(Visit, criteria, None)
        self.criteria_name = criteria
        self.chart = None
        self.count_col = func.count(1)
        self.host = host

    def get_chart(self):
        return self.type(
            interpolate='cubic',
            fill=True,
            human_readable=True,
            truncate_legend=200,
            style=PystilStyle,
            width=1000,
            height=400,
            js=[
                self.host + '/static/js/svg.jquery.js',
                self.host + '/static/js/pygal-tooltips.js'
            ],
            legend_at_bottom=self.type != pygal.Pie)

    def get_restrict(self):
        if self.criteria is not None:
            return self.criteria != None
        return True

    def filter(self, query):
        return (query
                .filter(on(self.site, self.table))
                .filter(between(self.from_date, self.to_date, self.table))
                .filter(self.get_restrict()))

    def get_query(self):
        return (
            self.filter(self.db.query(
                self.criteria.label("key"), self.count_col.label("count")))
            .group_by(self.criteria))

    def render(self):
        self.chart = self.get_chart()
        self.populate()
        self.chart.title = titlize(self.criteria_name, self.lang)
        return self.chart.render()

    def render_load(self):
        self.chart = self.type(
            fill=True,
            human_readable=True,
            style=PystilStyle,
            width=1000,
            height=400,
            js=[
                self.host + '/static/js/svg.jquery.js',
                self.host + '/static/js/pygal-tooltips.js'
            ])
        self.chart.no_data_text = 'Loading'
        self.chart.title = titlize(self.criteria_name, self.lang)
        return self.chart.render()


class Line(Chart):
    type = pygal.Line

    def populate(self):
        all = (self.filter(self.db
               .query(Visit.day, count(1), count(distinct(Visit.uuid))))
               .group_by(Visit.day)
               .order_by(Visit.day)
               .all())

        self.chart.x_labels = list(map(
            lambda x: x.strftime('%Y-%m-%d'), cut(all, 0)))
        self.chart.add(labelize('all', self.lang), cut(all, 1))
        self.chart.add(labelize('unique', self.lang), cut(all, 2))

        new = (self.filter(
            self.db
            .query(count(distinct(Visit.uuid))))
            .filter(Visit.last_visit == None)
            .group_by(Visit.day)
            .order_by(Visit.day)
            .all())
        self.chart.add(labelize('new', self.lang), cut(new, 0))
        self.chart.x_label_rotation = 45


class Bar(Chart):
    type = pygal.Bar

    def populate(self):
        all = self.get_query().order_by(self.criteria).all()
        if self.criteria_name == 'spent_time':
            self.chart.x_labels = [
                "<1s", "1s", "2s", "5s", "10s", "20s",
                "30s", "1min", "2min", "5min",  ">10min"]
        else:
            self.chart.x_labels = list(map(str, map(int, cut(all, 0))))
        self.chart.add(labelize(self.criteria_name, self.lang),
                       list(map(float, cut(all, 1))))


class Pie(Chart):
    type = pygal.Pie

    def get_restrict(self):
        # Multi criteria restrict
        if self.criteria_name == 'browser_name_version':
            return (
                (self.table.c.browser_name != None) &
                (self.table.c.browser_version != None))
        return super(Pie, self).get_restrict()

    def populate(self):
        results = (self.get_query()
                   .order_by(desc(self.count_col))
                   .limit(10)
                   .all())
        visits = [{
            'label': (
                parse_referrer(visit.key, host_only=True, second_pass=True)
                if self.criteria_name == 'pretty_referrer' else visit.key),
            'data': visit.count
        } for visit in results]
        all_visits = (self.filter(self.db
                      .query(self.count_col.label("all")))
                      .first()).all or 0
        other = all_visits - sum(visit['data'] for visit in visits)
        if other:
            visits = visits + [{'label': 'Other', 'data': other}]

        for visit in visits:
            self.chart.add(str(visit['label']), float(visit['data']))


class Worldmap(Chart):
    type = pygal.Worldmap

    def populate(self):
        all = self.get_query().all()
        self.chart.add('Top visits', [
            (country.key.lower(), float(country.count)) for country in all
        ])
