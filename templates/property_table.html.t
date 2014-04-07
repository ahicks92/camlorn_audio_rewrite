<html>
<head>
<title> OpenAL Properties</title>
</head>
<body>
<table>
<tr><th>Name</th><th>Object</th><th>Min</th><th>Max</th></tr>
{% for key in macros.keys()%}
{%set macro = macros[key]%}
<tr>
<td>{{key}}</td>
{%if macro.object%}
<td>{{macro.object}}</td>
{%else%}
<td>Unknown</td>
{%endif%}
{%if macro.range%}
<td>{{macro.range[0]}}</td>
<td>{{macro.range[1]}}</td>
{%else%}
<td>Unknown</td><td>Unknown</td>
{%endif%}
</tr>
{%endfor%}
</table>
</body>
</html>