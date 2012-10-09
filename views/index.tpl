<html>
<head>
	<title>Generátor</title>
</head>
<body>
<h1>Zadání</h1>
<p>Příznaky: <b>{{", ".join(flags)}}</b></p>
<pre>
{{output}}
</pre>
<hr>
<h2>Použité fragmenty</h2>
%for file in files:
<hr />
<h3>{{file}}</h3>
<pre>
{{"".join(files[file])}}
</pre>
%end

</body>
</html>