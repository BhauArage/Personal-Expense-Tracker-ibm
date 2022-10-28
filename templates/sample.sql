{% macro find_user(id) %}
select
    *
from clients
where clients.id={{id}};
{% endmacro %}