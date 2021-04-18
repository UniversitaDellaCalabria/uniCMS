from rest_framework.filters import SearchFilter


class GenericApiFilter(SearchFilter):
    """
    You can customize GET parameters defining in
    childs classes something like

    search_params = [
        {'name': 'ciao',
         'description': 'cosa fa ciao',
         'required': False,
         'type': 'string'},
        {'name': 'year',
         'description': 'Year',
         'required': False,
         'type': 'int'},
    ]
    """

    def get_schema_operation_parameters(self, view): # pragma: no cover
        params = super().get_schema_operation_parameters(view)
        for search_param in self.search_params:
            params.append(
                {
                    'name': search_param['name'],
                    'required': search_param.get('required', False),
                    'in': 'query',
                    'description': search_param['description'],
                    'schema': search_param.get('schema', {'type':'string'})
                }
            )
        return params
