<h1>Úprava profilu {{user.login}}</h1>
<h2>Změna hesla</h2>
<form action='' method='post' class='form-horizontal'>
    <div class="control-group">
        <label class="control-label" for="psw">Nové heslo</label>
        <div class="controls">
            <input type='password' id="psw" name="psw" />
        </div>
    </div>

    <div class="control-group">
        <label class="control-label" for="pswControl">Heslo pro kontrolu</label>
        <div class="controls">
            <input type='password' id="pswControl" name="pswControl" />
        </div>
    </div>
    
    <div class="control-group">
        <div class="controls">
            <input type='submit' name="gogogo" value='Nastavit' />
        </div>
    </div>    
</form>
%rebase layout