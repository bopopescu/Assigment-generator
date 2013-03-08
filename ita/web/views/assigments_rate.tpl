<div style='float:right;'>
<div><a href='/assigments-lector'><i class="icon-chevron-left"></i> zpátky na seznam</a></div>
</div>
%print(assigment.points )
<h2>{{assigment.login}}</h2>

<pre>
{{assigment.text}}
</pre>

<pre>
    {{assigment.response or "Zatím bez řešení"}}
</pre>

<form action='' method='post'>
    <div style="margin:auto;">
     
        %if assigment.locked:
            <button type="submit" class="btn btn-success" name="action" value="unlock"/><i class='icon-backward'></i> odemknout</button>
        %else:
            <button type="submit" class="btn btn-danger " name="action" value="lock"><i class='icon-lock'></i> zamknout</button>
        %end
        

        <div class="input-append" style='margin-bottom:0px;'>
            <input type="text" value="{{assigment.points or 0}}" class='span1' name="points"/>
            <button type="submit" class="btn btn-inverse" name="action" value="rate"/><i class='icon-thumbs-up icon-white'></i> ohodnotit</button>
        </div>     
    </div>

    
</form>

%rebase layout