<div style='float:right;'>
<div><a href='/assigments'><i class="icon-chevron-left"></i> zpátky na seznam</a></div>
</div>

<h2>{{lecture.name}}</h2>

<pre>
{{assigment.text}}
</pre>


%if assigment.locked:
<pre>
    {{assigment.response or ""}}
</pre>

<div> <i class="icon-lock"></i> Možnost odpovídat je zamčená</div>

%else:

<form action='' method='post'>
    <textarea style="width:100%; height:400px;" name="response" >{{assigment.response or ""}}</textarea>
    <input type='submit' value="Odeslat" class="btn" />
</form>
%end
%rebase layout