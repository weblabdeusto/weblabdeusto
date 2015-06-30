from __future__ import print_function, unicode_literals

from flask.ext.admin.contrib.sqla import tools
import flask.ext.admin.contrib.sqla.filters as filters

class FilterAnyEqual(filters.FilterEqual):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyEqual, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        return query.filter(self.column_any.any(self.column == value))

class FilterAnyNotEqual(filters.FilterNotEqual):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyNotEqual, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        return query.filter(self.column_any.any(self.column != value))

class FilterAnyLike(filters.FilterLike):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyLike, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        stmt = tools.parse_like_term(value)
        return query.filter(self.column_any.any(self.column.ilike(stmt)))

class FilterAnyNotLike(filters.FilterNotLike):
    def __init__(self, column, name, column_any, **kwargs):
        self.column_any = column_any
        super(FilterAnyNotLike, self).__init__(column, name, **kwargs)

    def apply(self, query, value):
        stmt = tools.parse_like_term(value)
        return query.filter(self.column_any.any(~self.column.ilike(stmt)))

def generate_filter_any(column, name, column_any, iter_type = tuple):
    return iter_type( 
                    (FilterAnyEqual(column, name, column_any), FilterAnyNotEqual(column, name, column_any), 
                     FilterAnyLike(column, name, column_any), FilterAnyNotLike(column, name, column_any)) )


def get_filter_number(view, name):
    return [ n  
                for (n, f) in enumerate(view._filters) 
                if unicode(f.column).endswith(name) 
                    and isinstance(f.operation.im_self, filters.FilterEqual) 
        ][0]


