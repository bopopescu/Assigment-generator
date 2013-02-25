<form action="/login-post" method="post" class="form-horizontal" >

<div class="control-group">
    <label class="control-label" for="inputLogin">Login</label>
    <div class="controls">
      <input type='text' name='login' id='inputLogin' placeholder="Login">
    </div>
</div>    

%if(lectorLogin):
<div class="control-group">
    <label class="control-label" for="inputPsw">Heslo</label>
    <div class="controls">
      <input type='password' name='password' id='inputPsw' placeholder="Heslo">
    </div>
</div>    
%end

<div class="control-group">
    <div class="controls">
      <input type='submit' value='Přihlásit' class="btn">
    </div>
</div>    

</form>

%rebase layout msgs=msgs